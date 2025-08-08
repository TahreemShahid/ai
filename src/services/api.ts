const API_BASE_URL = 'http://localhost:8000'; // Adjust as needed

export interface PDFUploadResponse {
  success: boolean;
  message: string;
  filename?: string;
}

export interface QuestionResponse {
  answer: string;
  source_chunks: string[];
}

export interface ComparisonRequest {
  text1: string;
  text2: string;
  comparison_type: string;
}

export interface ComparisonResponse {
  comparison: string;
  success: boolean;
}

export interface SummarizationRequest {
  text: string;
  summary_type: string;
  audience?: string;
}

export interface SummarizationResponse {
  summary: string;
  success: boolean;
}

export class PDFQAService {
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

  static async askQuestion(question: string, filename: string): Promise<QuestionResponse> {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, filename }),
    });

    if (!response.ok) {
      throw new Error(`Question failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async compareTexts(
    text1: string,
    text2: string,
    comparison_type: string = 'comprehensive'
  ): Promise<ComparisonResponse> {
    const response = await fetch(`${API_BASE_URL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text1, text2, comparison_type }),
    });

    if (!response.ok) {
      throw new Error(`Comparison failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async summarizeText(
    text: string,
    summary_type: string = 'brief',
    audience?: string
  ): Promise<SummarizationResponse> {
    const response = await fetch(`${API_BASE_URL}/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, summary_type, audience }),
    });

    if (!response.ok) {
      throw new Error(`Summarization failed: ${response.statusText}`);
    }

    return response.json();
  }

  // New method to delete uploaded file on backend
  static async deleteFile(filename: string): Promise<{ success: boolean; message?: string }> {
    const response = await fetch(`${API_BASE_URL}/delete_file?filename=${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`File delete failed: ${response.statusText}`);
    }

    return response.json();
  }
}
