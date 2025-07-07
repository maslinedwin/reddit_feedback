'use client';

import { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";

interface UserSummary {
  user_id: string;
  username: string;
  post_count: number;
  comment_count: number;
  total_score: number;
  platform?: string;  // Platform where user was found
  platform_sentiment: string;  // Changed from patreon_sentiment
  platform_rating: number;  // Changed from patreon_rating
  main_topics: string[];
  summary: string;
  reddit_profile_url: string;
  lead_score: number;  // 0-100 conversion likelihood
  // New fields
  creator_likelihood: number;
  discussion_starter_score: number;
  last_active_in_data?: string;
  account_age_days_in_data: number;
  // Reddit enriched fields
  reddit_account_created?: string;
  reddit_account_age_days?: number;
  reddit_link_karma?: number;
  reddit_comment_karma?: number;
  reddit_total_karma?: number;
  reddit_last_active?: string;
  is_active?: boolean;
  account_status?: string;
}

type SortField = 'username' | 'activity' | 'score' | 'rating' | 'creator' | 'discussion' | 'lastActive' | 'accountAge' | 'leadScore';
type SortDirection = 'asc' | 'desc';

export default function UsersPage() {
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<SortField>('activity');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/users');
      if (!response.ok) throw new Error('Failed to fetch users');
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const filteredUsers = users.filter(user => {
    const searchLower = searchTerm.toLowerCase();
    return (
      user.username.toLowerCase().includes(searchLower) ||
      user.summary.toLowerCase().includes(searchLower) ||
      user.main_topics.some(topic => topic.toLowerCase().includes(searchLower)) ||
      user.platform_sentiment.toLowerCase().includes(searchLower) ||
      (user.platform?.toLowerCase() || '').includes(searchLower)
    );
  });

  const sortedUsers = [...filteredUsers].sort((a, b) => {
    let aValue: any;
    let bValue: any;

    switch (sortField) {
      case 'username':
        aValue = a.username.toLowerCase();
        bValue = b.username.toLowerCase();
        break;
      case 'activity':
        aValue = a.post_count + a.comment_count;
        bValue = b.post_count + b.comment_count;
        break;
      case 'score':
        aValue = a.total_score;
        bValue = b.total_score;
        break;
      case 'rating':
        aValue = a.platform_rating;
        bValue = b.platform_rating;
        break;
      case 'creator':
        aValue = a.creator_likelihood;
        bValue = b.creator_likelihood;
        break;
      case 'discussion':
        aValue = a.discussion_starter_score;
        bValue = b.discussion_starter_score;
        break;
      case 'lastActive':
        aValue = new Date(a.reddit_last_active || a.last_active_in_data || '1970-01-01').getTime();
        bValue = new Date(b.reddit_last_active || b.last_active_in_data || '1970-01-01').getTime();
        break;
      case 'accountAge':
        aValue = a.reddit_account_age_days || a.account_age_days_in_data || 0;
        bValue = b.reddit_account_age_days || b.account_age_days_in_data || 0;
        break;
      case 'leadScore':
        aValue = a.lead_score || 0;
        bValue = b.lead_score || 0;
        break;
    }

    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return (
        <svg className="w-4 h-4 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    
    return sortDirection === 'asc' ? (
      <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
      </svg>
    );
  };

  // Helper function to format relative time
  const formatRelativeTime = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 30) return `${diffDays}d ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return `${Math.floor(diffDays / 365)}y ago`;
  };

  // Helper function to format account age
  const formatAccountAge = (days?: number) => {
    if (!days) return 'New';
    
    if (days < 30) return `${days}d`;
    if (days < 365) return `${Math.floor(days / 30)}mo`;
    return `${Math.floor(days / 365)}y ${Math.floor((days % 365) / 30)}mo`;
  };

  const getSentimentBadge = (sentiment: string, rating: number) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      positive: "default",
      negative: "destructive",
      neutral: "secondary",
      mixed: "outline"
    };

    const colors: Record<string, string> = {
      positive: "bg-success hover:bg-success/80",
      negative: "bg-destructive hover:bg-destructive/80",
      neutral: "bg-secondary hover:bg-secondary/80",
      mixed: "bg-warning hover:bg-warning/80"
    };

    return (
      <div className="flex items-center gap-2">
        <Badge 
          variant={variants[sentiment] || "default"}
          className={colors[sentiment]}
        >
          {sentiment}
        </Badge>
        <span className="text-sm font-medium">{rating}/10</span>
      </div>
    );
  };

  const exportToCSV = () => {
    const headers = ['Username', 'Platform', 'Posts', 'Comments', 'Score', 'Sentiment', 'Rating', 'Topics', 'Summary', 'Reddit URL'];
    const rows = users.map(user => [
      user.username,
      user.platform || 'unknown',
      user.post_count,
      user.comment_count,
      user.total_score,
      user.platform_sentiment,
      user.platform_rating,
      user.main_topics.join(';'),
      user.summary,
      user.reddit_profile_url
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'reddit_users_analysis.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-12 w-48" />
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Reddit User Analysis</h2>
          <p className="text-muted-foreground mt-1">
            Analyze user sentiment and identify potential leads
          </p>
        </div>
        <Button onClick={exportToCSV} variant="outline">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export CSV
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <Input
            type="search"
            placeholder="Search users, topics, or summaries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="text-sm text-muted-foreground">
          Showing {sortedUsers.length} of {users.length} users
        </div>
      </div>

      <Card className="overflow-hidden">
        <Table>
          <TableCaption>
            {searchTerm ? `Showing ${sortedUsers.length} of ${users.length} users matching "${searchTerm}"` : `Total users analyzed: ${users.length}`} | Data from multiple platforms
          </TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead 
                className="w-[150px] cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('username')}
              >
                <div className="flex items-center gap-2">
                  User
                  <SortIcon field="username" />
                </div>
              </TableHead>
              <TableHead 
                className="text-center cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('accountAge')}
              >
                <div className="flex items-center justify-center gap-2">
                  Account Age
                  <SortIcon field="accountAge" />
                </div>
              </TableHead>
              <TableHead 
                className="text-center cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('lastActive')}
              >
                <div className="flex items-center justify-center gap-2">
                  Last Active
                  <SortIcon field="lastActive" />
                </div>
              </TableHead>
              <TableHead 
                className="text-center cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('activity')}
              >
                <div className="flex items-center justify-center gap-2">
                  Activity
                  <SortIcon field="activity" />
                </div>
              </TableHead>
              <TableHead 
                className="text-center cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('creator')}
              >
                <div className="flex items-center justify-center gap-2">
                  Creator %
                  <SortIcon field="creator" />
                </div>
              </TableHead>
              <TableHead 
                className="text-center cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('discussion')}
              >
                <div className="flex items-center justify-center gap-2">
                  Discussion
                  <SortIcon field="discussion" />
                </div>
              </TableHead>
              <TableHead className="text-center">Platform</TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('rating')}
              >
                <div className="flex items-center gap-2">
                  Platform View
                  <SortIcon field="rating" />
                </div>
              </TableHead>
              <TableHead 
                className="text-center cursor-pointer hover:bg-muted/50"
                onClick={() => handleSort('leadScore')}
              >
                <div className="flex items-center justify-center gap-2">
                  Lead Score
                  <SortIcon field="leadScore" />
                </div>
              </TableHead>
              <TableHead className="text-center">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedUsers.map((user) => (
              <TableRow key={user.user_id} className="hover:bg-muted/50">
                <TableCell className="font-medium">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold">{user.username}</p>
                      {user.account_status === 'suspended' && (
                        <Badge variant="destructive" className="text-xs">Suspended</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      {user.reddit_total_karma ? (
                        <span>{user.reddit_total_karma.toLocaleString()} karma</span>
                      ) : (
                        <span>{user.total_score} score</span>
                      )}
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-sm font-medium">
                    {formatAccountAge(user.reddit_account_age_days || user.account_age_days_in_data)}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <div className="text-sm">
                    <p className={user.is_active ? 'text-success' : ''}>
                      {formatRelativeTime(user.reddit_last_active || user.last_active_in_data)}
                    </p>
                    {user.is_active && (
                      <span className="text-xs text-success">Active</span>
                    )}
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex flex-col items-center gap-1">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-muted-foreground">P:</span>
                      <span className="font-medium">{user.post_count}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-muted-foreground">C:</span>
                      <span className="font-medium">{user.comment_count}</span>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <div className={`text-sm font-medium ${user.creator_likelihood > 50 ? 'text-primary' : ''}`}>
                    {user.creator_likelihood}%
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <div className="text-sm">
                    <p className="font-medium">{user.discussion_starter_score.toFixed(1)}</p>
                    <p className="text-xs text-muted-foreground">score</p>
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <Badge variant="outline" className="capitalize">
                    {user.platform || 'patreon'}
                  </Badge>
                </TableCell>
                <TableCell>
                  {getSentimentBadge(user.platform_sentiment, user.platform_rating)}
                </TableCell>
                <TableCell className="text-center">
                  <div className={`text-lg font-bold ${
                    user.lead_score >= 70 ? 'text-success' : 
                    user.lead_score >= 40 ? 'text-warning' : 
                    'text-muted-foreground'
                  }`}>
                    {user.lead_score ? Math.round(user.lead_score) : 0}
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    asChild
                  >
                    <a
                      href={user.reddit_profile_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      Profile
                    </a>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}