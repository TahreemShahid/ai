import React from 'react';
import { Header } from '@/components/Header';
import { ChatInterface } from '@/components/ChatInterface';
import { useChatAI } from '@/hooks/useChatAI';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { 
  RotateCcw, 
  Trash2
} from 'lucide-react';

const Chat = () => {
  const {
    messages,
    isProcessing,
    uploadedFile,
    isUploading,
    error,
    sendMessage,
    uploadFile,
    removeFile,
    clearConversation,
    clearError,
    reset,
  } = useChatAI();

  const { toast } = useToast();

  React.useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: error,
        variant: "destructive",
      });
      clearError();
    }
  }, [error, toast, clearError]);

  const handleFileUpload = (file: File | null) => {
    if (file === null) {
      removeFile();
    } else {
      uploadFile(file);
    }
  };

  const handleClearConversation = () => {
    clearConversation();
    toast({
      title: "Conversation Cleared",
      description: "Your chat history has been cleared.",
    });
  };

  const handleReset = () => {
    reset();
    toast({
      title: "Reset Complete",
      description: "All data has been reset.",
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Chat Interface */}
        <div className="mb-8">
          <ChatInterface
            messages={messages}
            onSendMessage={sendMessage}
            onFileUpload={handleFileUpload}
            selectedFile={uploadedFile}
            isLoading={isProcessing}
            isUploading={isUploading}
          />
        </div>

        {/* Controls */}
        <div className="flex justify-center gap-4">
          <Button
            variant="outline"
            onClick={handleClearConversation}
            disabled={messages.length === 0}
            className="flex items-center gap-2"
          >
            <RotateCcw className="h-4 w-4" />
            Clear Chat
          </Button>
          <Button
            variant="outline"
            onClick={handleReset}
            className="flex items-center gap-2"
          >
            <Trash2 className="h-4 w-4" />
            Reset All
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
