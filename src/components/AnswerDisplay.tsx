import React from 'react';
import { Brain, BookOpen, AlertCircle } from 'lucide-react';

interface AnswerDisplayProps {
  answer?: string;
  sourceChunks?: string[];
  error?: string;
  isLoading?: boolean;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({
  answer,
  sourceChunks = [],
  error,
  isLoading = false
}) => {
  if (isLoading) {
    return (
      <div className="answer-section">
        <div className="flex items-center gap-3 mb-6">
          <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary border-t-transparent" />
          <h3 className="text-lg font-medium text-foreground">
            Processing your question...
          </h3>
        </div>
        
        <div className="space-y-3">
          <div className="h-4 bg-muted animate-pulse rounded" />
          <div className="h-4 bg-muted animate-pulse rounded w-3/4" />
          <div className="h-4 bg-muted animate-pulse rounded w-1/2" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="answer-section border-destructive/50 bg-destructive/5">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="h-6 w-6 text-destructive" />
          <h3 className="text-lg font-medium text-destructive">
            Error Processing Request
          </h3>
        </div>
        <p className="text-destructive/80">{error}</p>
      </div>
    );
  }

  if (!answer) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* AI Answer */}
      <div className="answer-section">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="h-6 w-6 text-primary" />
          <h3 className="text-lg font-medium text-foreground">
            AI Answer
          </h3>
        </div>
        
        <div className="prose prose-invert max-w-none">
          <p className="text-foreground leading-relaxed whitespace-pre-wrap">
            {answer}
          </p>
        </div>
      </div>

      {/* Supporting Sources */}
      {sourceChunks.length > 0 && (
        <div className="answer-section">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="h-6 w-6 text-primary" />
            <h3 className="text-lg font-medium text-foreground">
              Supporting Excerpts
            </h3>
            <span className="px-2 py-1 text-xs bg-primary/20 text-primary rounded-full">
              {sourceChunks.length} source{sourceChunks.length !== 1 ? 's' : ''}
            </span>
          </div>
          
          <div className="space-y-3">
            {sourceChunks.map((chunk, index) => (
              <div key={index} className="source-chunk">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium text-primary">
                    Excerpt {index + 1}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {chunk}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};