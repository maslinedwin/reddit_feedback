'use client';

import { useChat } from 'ai/react';
import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import UsersPage from './users/page';
import SubredditsPage from './subreddits/page';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border px-6 py-5 bg-black/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Reddit Insights AI
              </h1>
              <p className="text-sm text-muted-foreground">Powered by Advanced RAG Analysis</p>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-warning animate-pulse' : 'bg-success'}`} />
              <span className="text-xs text-muted-foreground">{isLoading ? 'Processing' : 'Ready'}</span>
            </div>
          </div>
        </div>
      </header>

      <Tabs defaultValue="chat" className="flex-1 flex flex-col">
        <div className="border-b border-border px-6">
          <div className="max-w-7xl mx-auto">
            <TabsList className="h-12 bg-transparent border-0 p-0">
              <TabsTrigger 
                value="chat" 
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-6"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                Chat
              </TabsTrigger>
              <TabsTrigger 
                value="users" 
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-6"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Users
              </TabsTrigger>
              <TabsTrigger 
                value="subreddits" 
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-6"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Platforms
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        <TabsContent value="chat" className="flex-1 flex flex-col mt-0">
          {/* Messages Area */}
          <ScrollArea className="flex-1 p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="min-h-[60vh] flex items-center justify-center">
              <Card className="p-8 sm:p-10 lg:p-12 text-center border-primary/20 bg-gradient-to-b from-card to-background max-w-3xl">
                <div className="space-y-6">
                  <div className="inline-flex p-4 rounded-2xl bg-primary/10 mb-4">
                    <svg className="w-12 h-12 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  
                  <div>
                    <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                      Welcome to Reddit Insights AI
                    </h2>
                    <p className="text-muted-foreground text-lg">
                      Unlock the power of community feedback with AI-driven analysis
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto mt-8">
                    <Button
                      variant="outline"
                      className="justify-start p-4 h-auto hover:bg-primary/5 hover:border-primary/50 transition-all group"
                      onClick={() => handleInputChange({ target: { value: 'What are the common complaints about Patreon?' } } as any)}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-destructive/10 group-hover:bg-destructive/20 transition-colors">
                          <svg className="w-5 h-5 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div className="text-left">
                          <p className="font-semibold">Common complaints</p>
                          <p className="text-xs text-muted-foreground">Pain points & issues</p>
                        </div>
                      </div>
                    </Button>
                    
                    <Button
                      variant="outline"
                      className="justify-start p-4 h-auto hover:bg-primary/5 hover:border-primary/50 transition-all group"
                      onClick={() => handleInputChange({ target: { value: 'What features do users want most?' } } as any)}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-success/10 group-hover:bg-success/20 transition-colors">
                          <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        </div>
                        <div className="text-left">
                          <p className="font-semibold">Feature requests</p>
                          <p className="text-xs text-muted-foreground">Most wanted updates</p>
                        </div>
                      </div>
                    </Button>
                    
                    <Button
                      variant="outline"
                      className="justify-start p-4 h-auto hover:bg-primary/5 hover:border-primary/50 transition-all group"
                      onClick={() => handleInputChange({ target: { value: 'How do creators feel about monetization?' } } as any)}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-warning/10 group-hover:bg-warning/20 transition-colors">
                          <svg className="w-5 h-5 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div className="text-left">
                          <p className="font-semibold">Creator sentiment</p>
                          <p className="text-xs text-muted-foreground">Monetization insights</p>
                        </div>
                      </div>
                    </Button>
                    
                    <Button
                      variant="outline"
                      className="justify-start p-4 h-auto hover:bg-primary/5 hover:border-primary/50 transition-all group"
                      onClick={() => handleInputChange({ target: { value: 'What are the top user frustrations?' } } as any)}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div className="text-left">
                          <p className="font-semibold">User frustrations</p>
                          <p className="text-xs text-muted-foreground">Top pain points</p>
                        </div>
                      </div>
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'assistant' && (
                <Avatar className="h-8 w-8 border border-primary/30">
                  <AvatarFallback className="bg-gradient-to-br from-primary/20 to-accent/20 text-primary text-xs font-bold">
                    AI
                  </AvatarFallback>
                </Avatar>
              )}
              <Card className={`max-w-[80%] p-4 ${
                m.role === 'user' 
                  ? 'bg-primary text-primary-foreground border-primary' 
                  : 'bg-card/50 backdrop-blur-sm border-border/50'
              }`}>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={vscDarkPlus}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className="px-1 py-0.5 rounded bg-muted text-sm" {...props}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {m.content}
                  </ReactMarkdown>
                </div>
              </Card>
              {m.role === 'user' && (
                <Avatar className="h-8 w-8 border border-primary">
                  <AvatarFallback className="bg-primary text-primary-foreground text-xs font-bold">
                    U
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <Avatar className="h-8 w-8">
                <AvatarFallback>AI</AvatarFallback>
              </Avatar>
              <Card className="p-4 space-y-2">
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-4 w-[200px]" />
                <Skeleton className="h-4 w-[150px]" />
              </Card>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mx-4 mb-4">
          <AlertDescription>{error.message}</AlertDescription>
        </Alert>
      )}

      {/* Input Area */}
      <footer className="border-t border-border bg-black/50 backdrop-blur-sm p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                placeholder="Ask me anything about Reddit feedback..."
                className="min-h-[60px] resize-none bg-input/50 border-border/50 focus:border-primary/50 transition-colors pr-12"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e as any);
                  }
                }}
                disabled={isLoading}
                rows={1}
              />
              <div className="absolute bottom-3 right-3 text-xs text-muted-foreground">
                {input.length}/1000
              </div>
            </div>
            <Button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="h-auto min-h-[60px] px-6 bg-primary hover:bg-primary/90 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  <span>Sending</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <span>Send</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
              )}
            </Button>
          </div>
          <div className="flex items-center justify-between mt-3">
            <div className="text-xs text-muted-foreground">
              Press <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Shift + Enter</kbd> for new line
            </div>
            <div className="flex gap-2 text-xs">
              <button type="button" className="text-muted-foreground hover:text-primary transition-colors">
                Clear history
              </button>
            </div>
          </div>
        </form>
      </footer>
        </TabsContent>

        <TabsContent value="users" className="flex-1 mt-0">
          <UsersPage />
        </TabsContent>

        <TabsContent value="subreddits" className="flex-1 mt-0">
          <SubredditsPage />
        </TabsContent>
      </Tabs>
    </div>
  );
}