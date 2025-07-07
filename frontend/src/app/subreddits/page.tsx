'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Plus, X, RefreshCw, Zap } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface MonitoredSubreddit {
  subreddit: string;
  platform_name: string;
  added_at: string;
  is_active: boolean;
  last_scraped?: string;
  posts_collected: number;
  users_found: number;
}

export default function SubredditsPage() {
  const [subreddits, setSubreddits] = useState<MonitoredSubreddit[]>([]);
  const [newSubreddit, setNewSubreddit] = useState('');
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [collecting, setCollecting] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchSubreddits();
  }, []);

  const fetchSubreddits = async () => {
    try {
      const response = await fetch('http://localhost:8000/subreddits');
      const data = await response.json();
      
      if (data.success) {
        setSubreddits(data.subreddits);
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load monitored subreddits',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddSubreddit = async () => {
    if (!newSubreddit.trim()) return;

    setAdding(true);
    try {
      const response = await fetch('http://localhost:8000/subreddits/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          subreddit: newSubreddit.trim(),
          platform_name: newSubreddit.trim() 
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        toast({
          title: 'Success',
          description: `Added r/${newSubreddit} to monitoring`,
        });
        
        setNewSubreddit('');
        fetchSubreddits();
        
        // Optionally trigger immediate collection
        handleCollectNow(newSubreddit.trim());
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add subreddit',
        variant: 'destructive',
      });
    } finally {
      setAdding(false);
    }
  };

  const handleRemoveSubreddit = async (subreddit: string) => {
    try {
      const response = await fetch(`http://localhost:8000/subreddits/${subreddit}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        toast({
          title: 'Success',
          description: `Stopped monitoring r/${subreddit}`,
        });
        fetchSubreddits();
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to remove subreddit',
        variant: 'destructive',
      });
    }
  };

  const handleCollectNow = async (subreddit: string) => {
    setCollecting(subreddit);
    
    try {
      const response = await fetch(`http://localhost:8000/collect/${subreddit}`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        toast({
          title: 'Collection Complete',
          description: `Collected ${data.items_collected} items from r/${subreddit}`,
        });
        fetchSubreddits();
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to collect from subreddit',
        variant: 'destructive',
      });
    } finally {
      setCollecting(null);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-3xl font-bold">Platform Subreddits</h2>
        <p className="text-muted-foreground mt-1">
          Add and manage subreddits to monitor for creator platforms
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add New Platform</CardTitle>
          <CardDescription>
            Enter a subreddit name to start monitoring (e.g., "buymeacoffee", "onlyfans")
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                r/
              </span>
              <Input
                placeholder="buymeacoffee"
                value={newSubreddit}
                onChange={(e) => setNewSubreddit(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddSubreddit()}
                className="pl-8"
                disabled={adding}
              />
            </div>
            <Button 
              onClick={handleAddSubreddit}
              disabled={adding || !newSubreddit.trim()}
            >
              {adding ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Add & Scan
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {subreddits.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-muted-foreground">
                No subreddits monitored yet. Add one above to get started!
              </p>
            </CardContent>
          </Card>
        ) : (
          subreddits.map((sub) => (
            <Card key={sub.subreddit} className={!sub.is_active ? 'opacity-60' : ''}>
              <CardContent className="flex items-center justify-between p-6">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-semibold">r/{sub.subreddit}</h3>
                    <Badge variant={sub.is_active ? 'default' : 'secondary'}>
                      {sub.platform_name}
                    </Badge>
                    {!sub.is_active && (
                      <Badge variant="outline">Inactive</Badge>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Added: {formatDate(sub.added_at)} | 
                    Last scraped: {formatDate(sub.last_scraped)} | 
                    Posts: {sub.posts_collected} | 
                    Users: {sub.users_found}
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCollectNow(sub.subreddit)}
                    disabled={collecting === sub.subreddit}
                  >
                    {collecting === sub.subreddit ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Zap className="h-4 w-4 mr-1" />
                        Collect Now
                      </>
                    )}
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveSubreddit(sub.subreddit)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <Alert>
        <AlertDescription>
          <strong>Tip:</strong> The system will automatically collect new posts daily at 2 AM. 
          Use "Collect Now" for immediate updates. Each platform's users will be tagged and 
          analyzed for creator likelihood and engagement metrics.
        </AlertDescription>
      </Alert>
    </div>
  );
}