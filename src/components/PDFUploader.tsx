import React, { useCallback, useState, useRef } from 'react';
import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { PDFQAService } from '@/services/api';

interface PDFUploaderProps {
  onFilesSelect: (files: File[]) => void;
  isLoading?: boolean;
}

export const PDFUploader: React.FC<PDFUploaderProps> = ({
  onFilesSelect,
  isLoading = false
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFiles = useCallback((fileList: FileList | File[]) => {
    const validFiles = Array.from(fileList).filter(
      file => file.type === 'application/pdf'
    );
    if (validFiles.length) {
      onFilesSelect(validFiles);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [onFilesSelect]);

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
    processFiles(e.dataTransfer.files);
  }, [processFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      processFiles(e.target.files);
    }
  }, [processFiles]);

  const removeFile = useCallback(async (fileName: string) => {
    try {
      const result = await PDFQAService.deleteFile(fileName);
      if (!result.success) {
        console.error('Delete failed:', result.message);
      }
    } catch (e) {
      console.error('Failed to delete file:', e);
    }
  }, []);

  return (
    <div
      className={cn(
        'upload-area',
        isDragOver && 'dragover'
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <Upload className="h-12 w-12 text-primary mx-auto mb-4" />
      <h3 className="text-lg font-medium text-foreground mb-2">
        Drop your PDFs here
      </h3>
      <p className="text-muted-foreground mb-4">
        or click to browse your files
      </p>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        multiple
        onChange={handleFileInput}
        className="hidden"
        id="pdf-upload"
        disabled={isLoading}
      />
      <Button asChild variant="gradient" disabled={isLoading}>
        <label
          htmlFor="pdf-upload"
          className={isLoading ? 'cursor-not-allowed' : 'cursor-pointer'}
        >
          {isLoading ? 'Uploading...' : 'Choose PDF Files'}
        </label>
      </Button>
      <p className="text-xs text-muted-foreground mt-3">
        Supports multiple PDF files up to 50MB each
      </p>
    </div>
  );
};
