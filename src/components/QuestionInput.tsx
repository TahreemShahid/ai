import React, { useState } from 'react';
import { Send, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface QuestionInputProps {
  onSubmit: (question: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export const QuestionInput: React.FC<QuestionInputProps> = ({
  onSubmit,
  isLoading = false,
  disabled = false
}) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading && !disabled) {
      onSubmit(question.trim());
      // Don't clear the question - keep it for follow-up questions
      // setQuestion(''); // This line is commented out
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="answer-section">
      <div className="flex items-center gap-3 mb-4">
        <MessageCircle className="h-6 w-6 text-primary" />
        <h3 className="text-lg font-medium text-foreground">
          Ask a Question
        </h3>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <Textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What would you like to know about this PDF? Ask anything..."
          className="min-h-[100px] resize-none"
          disabled={disabled || isLoading}
        />
        
        <div className="flex justify-end">
          <Button
            type="submit"
            variant="gradient"
            disabled={!question.trim() || isLoading || disabled}
            className="min-w-[120px]"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
                Processing...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Ask Question
              </>
            )}
          </Button>
        </div>
      </form>
      
      {disabled && (
        <p className="text-sm text-muted-foreground mt-2 text-center">
          Please upload a PDF file first
        </p>
      )}
    </div>
  );
};