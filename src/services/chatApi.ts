const API_BASE_URL = 'http://localhost:8000';

export interface ChatMessageRequest {
  message: string;
  sessionId: string;
  filename?: string;
  abortSignal?: AbortSignal;
}

export interface ChatMessageResponse {
  content: string;
  sessionId: string;
  success: boolean;
}

export interface PDFUploadResponse {
  success: boolean;
  message: string;
  filename?: string;
}

export class ChatAIService {
  static async uploadPDF(file: File): Promise<PDFUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async sendMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: request.message,
        session_id: request.sessionId,
        filename: request.filename,
      }),
      signal: request.abortSignal,
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async sendMessageStream(
    request: ChatMessageRequest,
    onChunk: (chunk: string) => void,
    onComplete: (response: ChatMessageResponse) => void,
    onError: (error: Error) => void
  ) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: request.message,
          session_id: request.sessionId,
          filename: request.filename,
        }),
        signal: request.abortSignal,
      });

      if (!response.ok) {
        throw new Error(`Stream request failed: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              // Stream complete, parse final response
              try {
                const finalResponse = JSON.parse(fullResponse);
                onComplete(finalResponse);
              } catch (e) {
                onError(new Error('Failed to parse final response'));
              }
              return;
            }
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                fullResponse = data;
                onChunk(parsed.content);
              }
            } catch (e) {
              // Ignore parsing errors for partial chunks
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw error;
      }
      onError(error instanceof Error ? error : new Error('Unknown error'));
    }
  }

  static async deleteFile(filename: string): Promise<{ success: boolean; message?: string }> {
    const response = await fetch(`${API_BASE_URL}/delete_file?filename=${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`File delete failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async getSessionHistory(sessionId: string): Promise<ChatMessageResponse[]> {
    const response = await fetch(`${API_BASE_URL}/chat/history?session_id=${encodeURIComponent(sessionId)}`);

    if (!response.ok) {
      throw new Error(`Failed to get session history: ${response.statusText}`);
    }

    return response.json();
  }

  static async clearSession(sessionId: string): Promise<{ success: boolean }> {
    const response = await fetch(`${API_BASE_URL}/chat/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
      throw new Error(`Failed to clear session: ${response.statusText}`);
    }

    return response.json();
  }
}
