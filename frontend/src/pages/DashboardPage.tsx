import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Sparkles,
  FileText,
  TrendingUp,
  ArrowRight,
  Clock,
  Star,
  History,
  User,
  Zap,
  Loader2,
} from "lucide-react";
import { motion } from "framer-motion";
import { useAuthStore } from "@/stores/authStore";
import { getHistoryList } from "@/services/api";

// Helper to format time ago
const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString();
};

export default function DashboardPage() {
  const { user } = useAuthStore();
  
  // Fetch recent generations
  const { data: historyData, isLoading } = useQuery({
    queryKey: ['dashboardHistory'],
    queryFn: () => getHistoryList(5, 0),
    staleTime: 60000, // 1 minute
  });

  // Calculate stats from history
  const histories = historyData?.histories || [];
  const totalPosts = historyData?.total || 0;
  const completedPosts = histories.filter(h => h.status === "completed");
  const avgScore = completedPosts.length > 0 
    ? completedPosts.reduce((sum, h) => sum + (h.quality_score || 0), 0) / completedPosts.length 
    : 0;
  const thisWeekCount = histories.filter(h => {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return new Date(h.started_at) > weekAgo;
  }).length;

  const stats = [
    { label: "Total Posts", value: String(totalPosts), icon: FileText, trend: `${thisWeekCount} this week` },
    { label: "Avg Score", value: avgScore ? avgScore.toFixed(1) : "N/A", icon: Star, trend: "Quality rating" },
    { label: "This Week", value: String(thisWeekCount), icon: TrendingUp, trend: thisWeekCount >= 3 ? "On track" : "Keep going!" },
  ];

  // Format recent posts for display
  const recentPosts = histories.slice(0, 3).map(h => ({
    id: h.history_id,
    idea: h.raw_idea,
    status: h.status,
    createdAt: formatTimeAgo(h.started_at),
    score: h.quality_score,
    format: h.format || "text",
  }));

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{getGreeting()}, {user?.name?.split(' ')[0] || "there"}</h1>
          <p className="text-muted-foreground mt-1">
            Here's what's happening with your content
          </p>
        </div>
        <Button asChild size="lg">
          <Link to="/app/generate">
            <Sparkles className="mr-2 h-4 w-4" />
            Create Post
          </Link>
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-3xl font-semibold mt-1 tracking-tight">{stat.value}</p>
                    <p className="text-xs text-success mt-1">{stat.trend}</p>
                  </div>
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <stat.icon className="h-6 w-6 text-primary" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link to="/app/generate">
            <Card className="hover:border-primary/30 hover:shadow-sm transition-all cursor-pointer h-full">
              <CardContent className="p-5 flex flex-col items-center text-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-medium">New Post</h3>
                  <p className="text-sm text-muted-foreground">Create content</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link to="/app/generations">
            <Card className="hover:border-primary/30 hover:shadow-sm transition-all cursor-pointer h-full">
              <CardContent className="p-5 flex flex-col items-center text-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center">
                  <History className="h-6 w-6 text-secondary-foreground" />
                </div>
                <div>
                  <h3 className="font-medium">Generations</h3>
                  <p className="text-sm text-muted-foreground">View history</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link to="/app/brand-profile">
            <Card className="hover:border-primary/30 hover:shadow-sm transition-all cursor-pointer h-full">
              <CardContent className="p-5 flex flex-col items-center text-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center">
                  <User className="h-6 w-6 text-secondary-foreground" />
                </div>
                <div>
                  <h3 className="font-medium">Brand Profile</h3>
                  <p className="text-sm text-muted-foreground">Define voice</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link to="/app/analytics">
            <Card className="hover:border-primary/30 hover:shadow-sm transition-all cursor-pointer h-full">
              <CardContent className="p-5 flex flex-col items-center text-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center">
                  <Zap className="h-6 w-6 text-secondary-foreground" />
                </div>
                <div>
                  <h3 className="font-medium">Analytics</h3>
                  <p className="text-sm text-muted-foreground">Track performance</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>

      {/* Recent Posts */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Recent Posts</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/app/posts">
              View All <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
        <div className="space-y-3">
          {recentPosts.map((post, index) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.05 }}
            >
              <Link to={`/app/generations/${post.id}`}>
                <Card className="hover:border-primary/20 hover:shadow-sm transition-all cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge
                            variant={
                              post.status === "completed"
                                ? "success"
                                : post.status === "processing"
                                ? "processing"
                                : "pending"
                            }
                          >
                            {post.status}
                          </Badge>
                          <Badge variant="outline">{post.format}</Badge>
                        </div>
                        <h3 className="font-medium text-sm line-clamp-1">
                          {post.idea}
                        </h3>
                        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {post.createdAt}
                          </span>
                        </div>
                      </div>
                      {post.score && (
                        <div className="flex items-center gap-1 bg-success/10 text-success px-2 py-1 rounded-md">
                          <Star className="h-3.5 w-3.5" />
                          <span className="text-sm font-semibold">{post.score}</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
