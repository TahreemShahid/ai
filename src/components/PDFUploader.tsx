import React, { useCallback, useState, useRef, useEffect } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { PDFQAService } from '@/services/api';

interface PDFUploaderProps {
  onFileSelect: (file: File | null) => void;
  selectedFile?: File | null;
  isLoading?: boolean;
}

export const PDFUploader: React.FC<PDFUploaderProps> = ({
  onFileSelect,
  selectedFile,
  isLoading = false
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(file => file.type === 'application/pdf');
    if (pdfFile) {
      onFileSelect(pdfFile);
    }
    // Reset so same file can be uploaded again
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      onFileSelect(file);
    }
    // Always reset input so same file can be uploaded again
    if (e.target) e.target.value = '';
  }, [onFileSelect]);

  const removeFile = useCallback(async () => {
    if (selectedFile && !isLoading) {
      try {
        const result = await PDFQAService.deleteFile(selectedFile.name);
        if (result.success) {
          onFileSelect(null);
          if (fileInputRef.current) fileInputRef.current.value = '';
        } else {
          console.error('Delete failed:', result.message);
        }
      } catch (e) {
        console.error('Failed to delete file:', e);
      }
    }
  }, [selectedFile, isLoading, onFileSelect]);

  useEffect(() => {
    if (!selectedFile && fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [selectedFile]);

  if (selectedFile) {
    return (
      <div className="answer-section">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="h-8 w-8 text-primary" />
            <div>
              <p className="font-medium text-foreground">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          {!isLoading && (
            <Button
              variant="ghost"
              size="sm"
              onClick={removeFile}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        {isLoading && (
          <p className="text-blue-600 mt-2 font-medium flex items-center gap-2">
            <svg
              className="animate-spin h-5 w-5 text-blue-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              ></path>
            </svg>
            Processing PDF, please wait...
          </p>
        )}
      </div>
    );
  }

  return (
    <div
      className={cn(
        "upload-area",
        isDragOver && "dragover"
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <Upload className="h-12 w-12 text-primary mx-auto mb-4" />
      <h3 className="text-lg font-medium text-foreground mb-2">
        Drop your PDF here
      </h3>
      <p className="text-muted-foreground mb-4">
        or click to browse your files
      </p>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileInput}
        className="hidden"
        id="pdf-upload"
        disabled={isLoading}
      />
      <Button asChild variant="gradient" disabled={isLoading}>
        <label htmlFor="pdf-upload" className={isLoading ? 'cursor-not-allowed' : 'cursor-pointer'}>
          {isLoading ? 'Uploading...' : 'Choose PDF File'}
        </label>
      </Button>
      <p className="text-xs text-muted-foreground mt-3">
        Supports PDF files up to 50MB
      </p>
    </div>
  );
};
