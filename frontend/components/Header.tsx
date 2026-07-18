import Link from 'next/link';
import { Sparkles, History } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-background/60 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <div className="p-2 bg-gradient-to-tr from-primary to-blue-500 rounded-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
            OptiResume AI
          </span>
        </Link>
        
        <nav className="flex items-center space-x-6 text-sm font-medium">
          <Link href="/" className="transition-colors hover:text-primary">
            Upload
          </Link>
          <Link href="/dashboard" className="transition-colors hover:text-primary flex items-center">
            <History className="w-4 h-4 mr-1.5" />
            Library
          </Link>
        </nav>
      </div>
    </header>
  );
}
