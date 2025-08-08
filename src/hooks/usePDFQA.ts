import { useState, useCallback } from 'react';
import { PDFQAService, QuestionResponse } from '@/services/api';

interface UsePDFQAState {
  isUploading: boolean;
  isProcessing: boolean;
  uploadedFile: File | null;
  currentAnswer: QuestionResponse | null;
  error: string | null;
}

export const usePDFQA = () => {
  const [state, setState] = useState<UsePDFQAState>({
    isUploading: false,
    isProcessing: false,
    uploadedFile: null,
    currentAnswer: null,
    error: null,
  });

  const uploadFile = useCallback(async (file: File) => {
    setState(prev => ({ ...prev, isUploading: true, error: null }));
    
    try {
      const response = await PDFQAService.uploadPDF(file);
      if (response.success) {
        setState(prev => ({
          ...prev,
          uploadedFile: file,
          isUploading: false,
          currentAnswer: null, // Clear previous answer
        }));
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
  }, []);

  const askQuestion = useCallback(async (question: string) => {
    if (!state.uploadedFile) {
      setState(prev => ({ ...prev, error: 'Please upload a PDF first' }));
      return;
    }

    setState(prev => ({ ...prev, isProcessing: true, error: null }));
    
    try {
      const response = await PDFQAService.askQuestion(question, state.uploadedFile.name);
      setState(prev => ({
        ...prev,
        currentAnswer: response,
        isProcessing: false,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        error: error instanceof Error ? error.message : 'Question processing failed',
      }));
    }
  }, [state.uploadedFile]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const reset = useCallback(() => {
    setState({
      isUploading: false,
      isProcessing: false,
      uploadedFile: null,
      currentAnswer: null,
      error: null,
    });
  }, []);

  return {
    ...state,
    uploadFile,
    askQuestion,
    clearError,
    reset,
  };
};