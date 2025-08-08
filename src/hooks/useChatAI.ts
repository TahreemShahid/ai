import { useState, useCallback, useRef } from 'react';
import { ChatMessage } from '@/components/ChatInterface';
import { ChatAIService } from '@/services/chatApi';

interface UseChatAIState {
  messages: ChatMessage[];
  isProcessing: boolean;
  uploadedFile: File | null;
  isUploading: boolean;
  error: string | null;
  sessionId: string | null;
}

export const useChatAI = () => {
  const [state, setState] = useState<UseChatAIState>({
    messages: [],
    isProcessing: false,
    uploadedFile: null,
    isUploading: false,
    error: null,
    sessionId: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const generateSessionId = useCallback(() => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  const addMessage = useCallback((message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };
    
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, newMessage],
    }));
    
    return newMessage;
  }, []);

  const updateLastMessage = useCallback((updates: Partial<ChatMessage>) => {
    setState(prev => ({
      ...prev,
      messages: prev.messages.map((msg, index) => 
        index === prev.messages.length - 1 ? { ...msg, ...updates } : msg
      ),
    }));
  }, []);

  const uploadFile = useCallback(async (file: File) => {
    setState(prev => ({ ...prev, isUploading: true, error: null }));
    
    try {
      const response = await ChatAIService.uploadPDF(file);
      if (response.success) {
        setState(prev => ({
          ...prev,
          uploadedFile: file,
          isUploading: false,
          sessionId: prev.sessionId || generateSessionId(),
        }));

        // Add system message about file upload
        addMessage({
          role: 'assistant',
          content: `I've successfully uploaded and processed "${file.name}". I can now help you with questions about this document or engage in general conversation. What would you like to know?`,
        });
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isUploading: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      }));
    }
  }, [addMessage, generateSessionId]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller for this request
    abortControllerRef.current = new AbortController();

    // Add user message
    addMessage({
      role: 'user',
      content: content.trim(),
    });

    // Add assistant message placeholder for streaming
    const assistantMessage = addMessage({
      role: 'assistant',
      content: '',
      isStreaming: true,
    });

    setState(prev => ({ ...prev, isProcessing: true, error: null }));

    try {
      const response = await ChatAIService.sendMessage({
        message: content.trim(),
        sessionId: state.sessionId || generateSessionId(),
        filename: state.uploadedFile?.name,
        abortSignal: abortControllerRef.current.signal,
      });

      // Update the assistant message with the response
      updateLastMessage({
        content: response.content,
        isStreaming: false,
      });

      // Set session ID if not already set
      if (!state.sessionId) {
        setState(prev => ({ ...prev, sessionId: response.sessionId }));
      }

    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        // Request was cancelled, remove the assistant message
        setState(prev => ({
          ...prev,
          messages: prev.messages.filter(msg => msg.id !== assistantMessage.id),
        }));
      } else {
        // Update the assistant message with error
        updateLastMessage({
          content: `I apologize, but I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
          isStreaming: false,
        });
      }
    } finally {
      setState(prev => ({ ...prev, isProcessing: false }));
      abortControllerRef.current = null;
    }
  }, [state.sessionId, state.uploadedFile, addMessage, updateLastMessage, generateSessionId]);

  const clearConversation = useCallback(() => {
    setState(prev => ({
      ...prev,
      messages: [],
      sessionId: generateSessionId(),
    }));
  }, [generateSessionId]);

  const removeFile = useCallback(async () => {
    if (state.uploadedFile) {
      try {
        await ChatAIService.deleteFile(state.uploadedFile.name);
      } catch (error) {
        console.error('Error deleting file:', error);
      }
    }
    
    setState(prev => ({
      ...prev,
      uploadedFile: null,
    }));

    // Add system message about file removal
    addMessage({
      role: 'assistant',
      content: 'I\'ve removed the uploaded document. I can still help you with general questions or you can upload a new document.',
    });
  }, [state.uploadedFile, addMessage]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const reset = useCallback(() => {
    setState({
      messages: [],
      isProcessing: false,
      uploadedFile: null,
      isUploading: false,
      error: null,
      sessionId: generateSessionId(),
    });
  }, [generateSessionId]);

  return {
    ...state,
    sendMessage,
    uploadFile,
    removeFile,
    clearConversation,
    clearError,
    reset,
  };
};
