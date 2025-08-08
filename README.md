# AI Assistant – Intelligent Chatbot

A modern React frontend for an intelligent AI chatbot with agentic capabilities and contextual memory. Upload documents, engage in conversations, and get intelligent responses with source citations—all powered by advanced AI services.

## Features

- 🤖 **Intelligent AI Chat** – Engage in natural conversations with contextual memory and agentic reasoning
- 📝 **Document Analysis** – Upload PDFs and ask intelligent questions with source citations
- 🧠 **Contextual Memory** – AI remembers conversation history and maintains context across interactions
- ⚡ **Real-time Streaming** – Get instant, streaming responses for a dynamic chat experience
- 📚 **Source Citations** – Get supporting excerpts and evidence with every response
- 🎨 **Modern UI** – Beautiful, responsive chat interface with real-time feedback
- 🔄 **Session Management** – Persistent chat sessions with conversation history
- 🛠️ **Agentic Capabilities** – AI that can reason, plan, and take actions autonomously

## Quick Start

### Frontend (React)

1. **Install dependencies:**
```bash
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API keys:**
Create `keys.txt` in your backend directory:
```json
{
    "API_KEY": "your-api-key",
    "AI_Agent_URL": "your-ai-agent-url",
    "AI_Agent_Stream_URL": "your-stream-url"
}
```

3. **Start the API server:**
```bash
python api_server.py
```

The backend will be available at `http://localhost:8000`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx      # Main chat interface
│   │   ├── PDFUploader.tsx        # File upload component
│   │   └── Header.tsx             # App header
│   ├── hooks/
│   │   └── useChatAI.ts           # Chat session management
│   ├── services/
│   │   └── chatApi.ts             # Chat API communication
│   └── pages/
│       └── Chat.tsx               # Main chat page

backend/
├── api_server.py                  # FastAPI server with chat endpoints
├── custom_langchain.py           # Custom LLM wrapper
└── keys.txt                      # API configuration
```

## Development Workflow

1. **Start Backend:**
```bash
cd backend/
python api_server.py
```

2. **Start Frontend:**
```bash
npm run dev
```

3. **Open in Browser:**
Visit `http://localhost:8080`

## API Endpoints

### Chat Endpoints
- `POST /chat` - Send a chat message
- `POST /chat/stream` - Stream chat responses in real-time
- `GET /chat/history` - Get chat history for a session
- `POST /chat/clear` - Clear a chat session

### Document Endpoints
- `POST /upload` - Upload PDF file for processing
- `POST /ask` - Ask questions about uploaded PDFs
- `DELETE /delete_file` - Delete uploaded file

### Utility Endpoints
- `GET /health` - Health check

## Configuration

### Backend Configuration (keys.txt)
```json
{
    "API_KEY": "your-api-key",
    "AI_Agent_URL": "https://your-ai-agent-url",
    "AI_Agent_Stream_URL": "https://your-stream-url"
}
```

### Frontend Configuration
Update API base URL in `src/services/chatApi.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000'; // Adjust as needed
```

## Agentic AI Features

### Contextual Memory
- Maintains conversation history across sessions
- Remembers user preferences and context
- Intelligent context switching between topics

### Document Intelligence
- PDF processing and vectorization
- Semantic search and retrieval
- Source citation and evidence provision

### Streaming Responses
- Real-time response generation
- Progressive content display
- Abort/cancel functionality

### Session Management
- Persistent chat sessions
- Conversation history retrieval
- Session cleanup and reset

## Production Deployment

### Frontend
```bash
npm run build
# Deploy the dist/ folder to your hosting service
```

### Backend
```bash
# For production, use gunicorn or similar
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
```

## Docker Setup (Optional)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/keys.txt:/app/keys.txt
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure CORS is properly configured in your backend
2. **File Upload Fails**: Check file size limits and PDF validation
3. **API Connection**: Verify backend is running on the correct port
4. **Streaming Issues**: Check browser compatibility and network connectivity

### Chat Session Issues

1. **Memory Loss**: Sessions are stored in memory, restarting the server will clear them
2. **Context Issues**: Ensure proper session ID management
3. **Response Errors**: Check API key configuration and service availability

## Technologies Used

- **Frontend**: React 18, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, LangChain, HuggingFace Embeddings, FAISS
- **AI**: Custom LLM integration with agentic capabilities
- **Memory**: ConversationBufferMemory for contextual awareness
- **Streaming**: Server-Sent Events for real-time responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## License

MIT License - see LICENSE file for details