from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import json
import shutil
from typing import List, Dict, Optional
import uvicorn
import uuid
from datetime import datetime

# LangChain and your LLM wrapper imports
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Import your custom LLM wrapper 
from custom_langchain import MyDualEndpointLLM as LLM


app = FastAPI(title="AI Chat API", version="2.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for sessions and files
uploaded_files = {}
vector_stores = {}
chat_sessions: Dict[str, Dict] = {}

TMP_FOLDER = "./tmp_uploads"
os.makedirs(TMP_FOLDER, exist_ok=True)  # Ensure temp folder exists


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


def process_pdf_and_create_vectorstore(pdf_path: str, filename: str):
    try:
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(chunks, embedding_model)
        vector_stores[filename] = vector_store
        return vector_store
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise e


def get_or_create_session(session_id: str):
    """Get or create a chat session with memory"""
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


@app.get("/")
async def root():
    return {"message": "AI Chat API is running", "status": "healthy"}


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
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    try:
        file_path = os.path.join(TMP_FOLDER, file.filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        process_pdf_and_create_vectorstore(file_path, file.filename)

        uploaded_files[file.filename] = {
            'path': file_path,
            'size': len(content)
        }

        print(f"Successfully processed: {file.filename}")

        return {
            "success": True,
            "message": f"PDF '{file.filename}' uploaded and processed successfully",
            "filename": file.filename
        }
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.delete("/delete_file")
async def delete_file(filename: str = Query(...)):
    file_info = uploaded_files.pop(filename, None)
    vector_stores.pop(filename, None)
    if file_info and os.path.exists(file_info['path']):
        try:
            os.remove(file_info['path'])
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"Error deleting file: {str(e)}"}
    return {"success": False, "message": "File not found"}


@app.post("/chat", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest):
    try:
        config = load_config()
        session = get_or_create_session(request.session_id)
        
        # Get conversation history
        memory = session["memory"]
        llm = session["llm"]
        
        # Prepare context based on uploaded file
        context = ""
        sources = []
        if request.filename and request.filename in vector_stores:
            vector_store = vector_stores[request.filename]
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            relevant_docs = retriever.get_relevant_documents(request.message)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            sources = [doc.page_content for doc in relevant_docs]
        
        # Build the prompt with context and history
        chat_history = memory.chat_memory.messages
        history_text = ""
        if chat_history:
            history_text = "\n\nPrevious conversation:\n" + "\n".join([
                f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                for msg in chat_history[-4:]  # Last 4 messages for context
            ])
        
        # Create the full prompt
        if context:
            full_prompt = f"""You are an intelligent AI assistant with access to document context. Use the following information to provide helpful, accurate responses.

Document Context:
{context}

{history_text}

User: {request.message}

Assistant:"""
        else:
            full_prompt = f"""You are an intelligent AI assistant. Provide helpful, accurate, and engaging responses.

{history_text}

User: {request.message}

Assistant:"""
        
        # Generate response
        response = llm.invoke(full_prompt)
        
        # Update memory
        memory.chat_memory.add_user_message(request.message)
        memory.chat_memory.add_ai_message(response)
        session["message_count"] += 1

        return ChatMessageResponse(
            content=response,
            sources=sources,
            session_id=request.session_id,
            success=True
        )
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/chat/stream")
async def chat_message_stream(request: ChatMessageRequest):
    """Streaming chat endpoint for real-time responses"""
    
    async def generate_stream():
        try:
            config = load_config()
            session = get_or_create_session(request.session_id)
            
            memory = session["memory"]
            llm = session["llm"]
            
            # Prepare context (same as non-streaming)
            context = ""
            sources = []
            if request.filename and request.filename in vector_stores:
                vector_store = vector_stores[request.filename]
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                relevant_docs = retriever.get_relevant_documents(request.message)
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                sources = [doc.page_content for doc in relevant_docs]
            
            chat_history = memory.chat_memory.messages
            history_text = ""
            if chat_history:
                history_text = "\n\nPrevious conversation:\n" + "\n".join([
                    f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                    for msg in chat_history[-4:]
                ])
            
            if context:
                full_prompt = f"""You are an intelligent AI assistant with access to document context. Use the following information to provide helpful, accurate responses.

Document Context:
{context}

{history_text}

User: {request.message}

Assistant:"""
            else:
                full_prompt = f"""You are an intelligent AI assistant. Provide helpful, accurate, and engaging responses.

{history_text}

User: {request.message}

Assistant:"""
            
            # Stream the response
            response_chunks = []
            for chunk in llm.stream(full_prompt):
                response_chunks.append(chunk)
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # Complete response
            full_response = "".join(response_chunks)
            
            # Update memory
            memory.chat_memory.add_user_message(request.message)
            memory.chat_memory.add_ai_message(full_response)
            session["message_count"] += 1
            
            # Send final response with sources
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
    
    return StreamingResponse(generate_stream(), media_type="text/plain")


@app.get("/chat/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in chat_sessions:
        return {"messages": []}
    
    session = chat_sessions[session_id]
    memory = session["memory"]
    
    messages = []
    for msg in memory.chat_memory.messages:
        messages.append({
            "role": "user" if isinstance(msg, HumanMessage) else "assistant",
            "content": msg.content,
            "timestamp": session["created_at"].isoformat()
        })
    
    return {"messages": messages}


@app.post("/chat/clear")
async def clear_chat_session(session_id: str):
    """Clear a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {"success": True}


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    if request.filename not in vector_stores:
        raise HTTPException(status_code=400, detail="PDF not found. Please upload first.")
    try:
        config = load_config()
        haiku_llm = LLM(
            secret_key=config["API_KEY"],
            non_stream_url=config["AI_Agent_URL"],
            stream_url=config["AI_Agent_Stream_URL"]
        )

        vector_store = vector_stores[request.filename]
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})

        qa_chain = RetrievalQA.from_chain_type(
            llm=haiku_llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain.invoke(request.question)
        answer = result["result"]
        source_chunks = [doc.page_content for doc in result["source_documents"]]

        return QuestionResponse(
            answer=answer,
            source_chunks=source_chunks
        )
    except Exception as e:
        print(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


# Cleanup temp folder on shutdown
@app.on_event("shutdown")
def cleanup_tmp_folder():
    if os.path.exists(TMP_FOLDER):
        print(f"Cleaning up temp uploads folder {TMP_FOLDER} ...")
        shutil.rmtree(TMP_FOLDER)


if __name__ == "__main__":
    print("Starting AI Chat API server...")
    print("\nServer will start on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
