import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
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
} from "lucide-react";
import { motion } from "framer-motion";

const stats = [
  { label: "Total Posts", value: "24", icon: FileText, trend: "+3 this week" },
  { label: "Avg Score", value: "8.5", icon: Star, trend: "+0.3 vs last month" },
  { label: "This Week", value: "4", icon: TrendingUp, trend: "On track" },
];

const recentPosts = [
  {
    id: "1",
    idea: "3 lessons I learned from failing my first startup after 18 months",
    status: "completed",
    createdAt: "2 hours ago",
    score: 9.2,
    format: "text",
  },
  {
    id: "2",
    idea: "Why I quit my $300K job at Google to build a startup",
    status: "completed",
    createdAt: "1 day ago",
    score: 8.7,
    format: "carousel",
  },
  {
    id: "3",
    idea: "The 5-minute morning routine that 10x'd my productivity",
    status: "processing",
    createdAt: "2 days ago",
    score: null,
    format: "text",
  },
];

export default function DashboardPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Good morning, Alex</h1>
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
