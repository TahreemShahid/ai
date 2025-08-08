from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import json
import shutil
from typing import List, Dict, Optional, AsyncGenerator
import uvicorn
from datetime import datetime

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from custom_langchain import MyDualEndpointLLM as LLM

# Initialize FastAPI app
app = FastAPI(title="Agentic PDF Chatbot Backend", version="1.0.0")

# CORS middleware (Adjust allow_origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals for storing uploaded files and vector DBs, sessions
uploaded_files: Dict[str, Dict] = {}
vector_stores: Dict[str, FAISS] = {}
chat_sessions: Dict[str, Dict] = {}

TMP_FOLDER = "./tmp_uploads"
os.makedirs(TMP_FOLDER, exist_ok=True)

# === Pydantic models ===

class QuestionRequest(BaseModel):
    question: str
    filename: str

class QuestionResponse(BaseModel):
    answer: str
    source_chunks: List[str]

class ChatMessageRequest(BaseModel):
    message: str
    session_id: str
    filename: Optional[str] = None

class ChatMessageResponse(BaseModel):
    content: str
    sources: Optional[List[str]] = None
    session_id: str
    success: bool


# === Helper Functions ===

def load_config():
    if not os.path.exists("keys.txt"):
        raise FileNotFoundError("keys.txt not found. Please create it with your API configuration.")
    with open("keys.txt", "r") as f:
        config = json.load(f)
    required_keys = ["API_KEY", "AI_Agent_URL", "AI_Agent_Stream_URL"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing keys in keys.txt: {missing_keys}")
    return config


def process_pdf_and_create_vectorstore(pdf_path: str, filename: str) -> FAISS:
    """Load PDF, chunk text, create and store FAISS vector indices"""
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embedding_model)
    vector_stores[filename] = vector_store
    return vector_store


def get_or_create_session(session_id: str) -> Dict:
    """Retrieve or initialize a chat session with conversation memory and LLM"""
    if session_id not in chat_sessions:
        config = load_config()
        llm = LLM(
            secret_key=config["API_KEY"],
            non_stream_url=config["AI_Agent_URL"],
            stream_url=config["AI_Agent_Stream_URL"]
        )
        chat_sessions[session_id] = {
            "memory": ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=2000
            ),
            "llm": llm,
            "created_at": datetime.now(),
            "message_count": 0
        }
    return chat_sessions[session_id]


def build_strict_prompt(context: str, history_messages: List, user_message: str) -> str:
    """
    Construct prompt with explicit instructions restricting the assistant to summarization,
    comparison, and PDF-based Q&A only.
    """
    history_text = ""
    if history_messages:
        history_text = "\n\nPrevious conversation:\n" + "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in history_messages[-10:] 
        )
    
    system_instruction = (
        "You are an AI assistant specialized ONLY in summarizing a text/pdf, comparing two text snippets/pdfs, "
        "and answering questions based on the provided PDF document context.\n"
        "DO NOT answer questions unrelated to the PDFs or these tasks.\n"
        "If a question is outside your scope, respond politely with: "
        "'Sorry, I can only assist with information from the PDFs provided.'\n\n"
    )

    if context:
        prompt = (
            system_instruction +
            f"Document Context:\n{context}\n\n" +
            history_text + "\n\n" +
            f"User: {user_message}\n\nAssistant:"
        )
    else:
        prompt = (
            system_instruction +
            history_text + "\n\n" +
            f"User: {user_message}\n\nAssistant:"
        )

    return prompt


# === API Endpoints ===

@app.get("/")
async def root():
    return {"message": "Agentic PDF Chatbot API running", "status": "healthy"}


@app.get("/health")
async def health_check():
    try:
        config = load_config()
        return {
            "status": "healthy",
            "uploaded_files": len(uploaded_files),
            "active_sessions": len(chat_sessions),
            "ai_service_configured": True
        }
    except Exception as e:
        return {
            "status": "degraded",
            "uploaded_files": len(uploaded_files),
            "active_sessions": len(chat_sessions),
            "ai_service_configured": False,
            "error": str(e)
        }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Limit file size (e.g., 10MB max)
    MAX_SIZE = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="PDF file too large (max 10MB).")
    
    try:
        sanitized_filename = os.path.basename(file.filename)
        file_path = os.path.join(TMP_FOLDER, sanitized_filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Process PDF into vector store
        process_pdf_and_create_vectorstore(file_path, sanitized_filename)

        uploaded_files[sanitized_filename] = {
            "path": file_path,
            "size": len(content)
        }

        return {
            "success": True,
            "message": f"PDF '{sanitized_filename}' uploaded and processed.",
            "filename": sanitized_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.delete("/delete_file")
async def delete_file(filename: str = Query(...)):
    file_info = uploaded_files.pop(filename, None)
    vector_stores.pop(filename, None)
    if file_info and os.path.exists(file_info["path"]):
        try:
            os.remove(file_info["path"])
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Error deleting file: {str(e)}"}
    return {"success": False, "message": "File not found"}


@app.post("/chat", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest):
    """
    Chat endpoint that responds only using summarization, comparison,
    or question answering based on PDFs + chat history.
    """
    if request.filename and request.filename not in vector_stores:
        raise HTTPException(status_code=400, detail="PDF not found. Upload before chatting.")
    try:
        session = get_or_create_session(request.session_id)
        memory = session["memory"]
        llm = session["llm"]
        
        # Retrieve document context if PDF filename provided
        context = ""
        sources = []
        if request.filename:
            vector_store = vector_stores[request.filename]
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            relevant_docs = retriever.get_relevant_documents(request.message)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            sources = [doc.page_content for doc in relevant_docs]

        prompt = build_strict_prompt(context, memory.chat_memory.messages, request.message)

        # Invoke language model
        response = llm.invoke(prompt)

        # Update conversation memory
        memory.chat_memory.add_user_message(request.message)
        memory.chat_memory.add_ai_message(response)
        session["message_count"] += 1

        return ChatMessageResponse(
            content=response,
            sources=sources,
            session_id=request.session_id,
            success=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/chat/stream")
async def chat_message_stream(request: ChatMessageRequest):
    """
    Streaming chat endpoint same as /chat but responses are streamed chunk-by-chunk.
    """

    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            session = get_or_create_session(request.session_id)
            memory = session["memory"]
            llm = session["llm"]

            context = ""
            sources = []
            if request.filename:
                vector_store = vector_stores[request.filename]
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                relevant_docs = retriever.get_relevant_documents(request.message)
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                sources = [doc.page_content for doc in relevant_docs]

            prompt = build_strict_prompt(context, memory.chat_memory.messages, request.message)

            # Stream response chunks
            response_chunks = []
            async for chunk in llm.stream(prompt):
                response_chunks.append(chunk)
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            full_response = "".join(response_chunks)
            memory.chat_memory.add_user_message(request.message)
            memory.chat_memory.add_ai_message(full_response)
            session["message_count"] += 1

            # Send final event with sources and success
            final_response = {
                "content": full_response,
                "sources": sources,
                "session_id": request.session_id,
                "success": True
            }
            yield f"data: {json.dumps(final_response)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            error_response = {
                "content": f"Error: {str(e)}",
                "session_id": request.session_id,
                "success": False
            }
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.get("/chat/history")
async def get_chat_history(session_id: str):
    """Return full chat history for given session"""
    session = chat_sessions.get(session_id)
    if not session:
        return {"messages": []}
    messages = [
        {
            "role": "user" if isinstance(m, HumanMessage) else "assistant",
            "content": m.content,
            "timestamp": session["created_at"].isoformat(),
        }
        for m in session["memory"].chat_memory.messages
    ]
    return {"messages": messages}


@app.post("/chat/clear")
async def clear_chat_session(session_id: str):
    """Clear conversation memory for the given session."""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {"success": True}


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Direct question answering that strictly uses RetrievalQA chain.
    Returns answer and source chunks.
    """
    if request.filename not in vector_stores:
        raise HTTPException(status_code=400, detail="PDF not found. Please upload first.")
    try:
        config = load_config()
        haiku_llm = LLM(
            secret_key=config["API_KEY"],
            non_stream_url=config["AI_Agent_URL"],
            stream_url=config["AI_Agent_Stream_URL"],
        )
        vector_store = vector_stores[request.filename]
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})

        # LangChain's RetrievalQA, can be customized in custom_langchain.py with strict prompts
        qa_chain = RetrievalQA.from_chain_type(
            llm=haiku_llm, chain_type="stuff", retriever=retriever, return_source_documents=True
        )
        result = qa_chain.invoke(request.question)

        answer = result.get("result", "")
        source_chunks = [doc.page_content for doc in result.get("source_documents", [])]

        return QuestionResponse(answer=answer, source_chunks=source_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


# --- Cleanup uploaded PDFs on shutdown ---

@app.on_event("shutdown")
def cleanup_tmp_folder():
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)


# === Main ===
if __name__ == "__main__":
    print("Starting Agentic PDF Chatbot Backend API")
    uvicorn.run(app, host="0.0.0.0", port=8000)
