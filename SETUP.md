# AI Assistant Setup Guide

This guide will help you set up and run the AI Assistant chatbot with agentic AI capabilities.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager

## Quick Setup

### 1. Install Dependencies

**Backend (Python):**
```bash
pip install -r requirements.txt
```

**Frontend (Node.js):**
```bash
npm install
```

### 2. Configure API Keys

Create a `keys.txt` file in the root directory:
```json
{
    "API_KEY": "your-actual-api-key",
    "AI_Agent_URL": "https://your-ai-agent-url",
    "AI_Agent_Stream_URL": "https://your-stream-url"
}
```

**Note:** Replace the placeholder values with your actual API credentials.

### 3. Start the Application

**Option A: Start both frontend and backend together**
```bash
npm run dev:full
```

**Option B: Start them separately**

Terminal 1 (Backend):
```bash
npm run backend
# or
python start_backend.py
```

Terminal 2 (Frontend):
```bash
npm run dev
```

### 4. Access the Application

- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Testing the Setup

Run the demo script to test all functionality:
```bash
python demo_chat.py
```

## Features Available

### 🤖 AI Chat
- Natural conversation with contextual memory
- Real-time streaming responses
- Session management

### 📄 Document Analysis
- Upload PDF files
- Ask questions about document content
- Get source citations

### 🧠 Agentic Capabilities
- Contextual memory across conversations
- Intelligent reasoning and planning
- Autonomous decision making

### ⚡ Real-time Features
- Streaming responses
- Live chat interface
- Instant feedback

## Troubleshooting

### Common Issues

1. **"keys.txt not found"**
   - Create the `keys.txt` file with your API configuration

2. **"Missing required packages"**
   - Run `pip install -r requirements.txt`

3. **"Server connection failed"**
   - Ensure the backend is running on port 8000
   - Check if the API keys are correct

4. **"CORS errors"**
   - The backend is configured to allow all origins in development
   - For production, update the CORS settings in `api_server.py`

### Port Conflicts

If ports 8000 or 8080 are already in use:

**Backend (change in `api_server.py`):**
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change port number
```

**Frontend (change in `vite.config.ts`):**
```typescript
export default defineConfig({
  server: {
    port: 8081  // Change port number
  }
})
```

## Development

### Project Structure
```
├── src/
│   ├── components/          # React components
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   └── pages/              # Page components
├── api_server.py           # FastAPI backend
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
└── keys.txt              # API configuration
```

### Adding New Features

1. **New API Endpoints:** Add to `api_server.py`
2. **New Components:** Create in `src/components/`
3. **New Pages:** Add to `src/pages/` and update routing in `App.tsx`

## Production Deployment

### Backend
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
```

### Frontend
```bash
npm run build
# Deploy the dist/ folder to your hosting service
```

## Support

If you encounter issues:

1. Check the console logs for error messages
2. Verify your API keys are correct
3. Ensure all dependencies are installed
4. Test with the demo script: `python demo_chat.py`

## Next Steps

- Customize the AI prompts in `api_server.py`
- Add authentication and user management
- Implement database storage for chat history
- Add more document types support
- Enhance the UI with additional features
