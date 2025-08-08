import React from 'react';
import { Brain } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Header: React.FC = () => {
  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-center">
          <Link to="/" className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-r from-primary to-primary-glow shadow-glow">
              <Brain className="h-6 w-6 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary-glow bg-clip-text text-transparent">
              AI Assistant
            </h1>
          </Link>
        </div>
      </div>
    </header>
  );
};