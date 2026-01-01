import { motion } from "framer-motion";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Search,
  LayoutGrid,
  List,
  MoreHorizontal,
  Star,
  Copy,
  Trash2,
  Eye,
  Plus,
  FileText,
  Image,
  Video,
  ChevronLeft,
  ChevronRight,
  Clock,
  TrendingUp,
} from "lucide-react";
import { toast } from "sonner";
import { PostSummary } from "@/types/api";

// Mock data - would come from API
const mockPosts: PostSummary[] = [
  {
    post_id: "1",
    raw_idea: "3 lessons I learned from failing my first startup after 18 months",
    status: "completed",
    format: "text",
    quality_score: 8.5,
    created_at: "2024-01-15T10:30:00Z",
  },
  {
    post_id: "2",
    raw_idea: "Why I quit my $200K corporate job to pursue entrepreneurship",
    status: "completed",
    format: "carousel",
    quality_score: 9.2,
    created_at: "2024-01-14T15:45:00Z",
  },
  {
    post_id: "3",
    raw_idea: "The morning routine that changed my productivity forever",
    status: "processing",
    format: "text",
    created_at: "2024-01-14T09:20:00Z",
  },
  {
    post_id: "4",
    raw_idea: "5 books every entrepreneur should read in 2024",
    status: "completed",
    format: "carousel",
    quality_score: 7.8,
    created_at: "2024-01-13T14:00:00Z",
  },
  {
    post_id: "5",
    raw_idea: "How I built a $1M business with just a laptop",
    status: "failed",
    format: "video",
    created_at: "2024-01-12T11:30:00Z",
  },
  {
    post_id: "6",
    raw_idea: "The networking strategy nobody talks about",
    status: "completed",
    format: "text",
    quality_score: 8.9,
    created_at: "2024-01-11T16:15:00Z",
  },
];

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(date);
};

const getStatusConfig = (status: string) => {
  switch (status) {
    case "completed":
      return { variant: "success" as const, label: "Completed" };
    case "processing":
      return { variant: "processing" as const, label: "Processing" };
    case "pending":
      return { variant: "pending" as const, label: "Pending" };
    case "failed":
      return { variant: "failed" as const, label: "Failed" };
    default:
      return { variant: "secondary" as const, label: status };
  }
};

const getFormatConfig = (format?: string) => {
  switch (format) {
    case "carousel":
      return { icon: Image, label: "Carousel", color: "text-blue-500" };
    case "video":
      return { icon: Video, label: "Video", color: "text-purple-500" };
    default:
      return { icon: FileText, label: "Text", color: "text-emerald-500" };
  }
};

export default function PostHistoryPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [formatFilter, setFormatFilter] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [currentPage, setCurrentPage] = useState(1);
  const postsPerPage = 6;

  // Filter posts
  const filteredPosts = mockPosts.filter((post) => {
    const matchesSearch = post.raw_idea
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || post.status === statusFilter;
    const matchesFormat =
      formatFilter === "all" || post.format === formatFilter;
    return matchesSearch && matchesStatus && matchesFormat;
  });

  // Pagination
  const totalPages = Math.ceil(filteredPosts.length / postsPerPage);
  const paginatedPosts = filteredPosts.slice(
    (currentPage - 1) * postsPerPage,
    currentPage * postsPerPage
  );

  const handleCopy = (post: PostSummary) => {
    navigator.clipboard.writeText(post.raw_idea);
    toast.success("Post idea copied to clipboard!");
  };

  const handleDelete = (postId: string) => {
    toast.success("Post deleted successfully");
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Post History</h1>
          <p className="text-muted-foreground mt-1">
            View and manage all your generated posts
          </p>
        </div>
        <Link to="/app/generate">
          <Button size="lg">
            <Plus className="mr-2 h-4 w-4" /> Create New Post
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search posts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Status Filter */}
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full lg:w-[160px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>

          {/* Format Filter */}
          <Select value={formatFilter} onValueChange={setFormatFilter}>
            <SelectTrigger className="w-full lg:w-[160px]">
              <SelectValue placeholder="Format" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Formats</SelectItem>
              <SelectItem value="text">Text</SelectItem>
              <SelectItem value="carousel">Carousel</SelectItem>
              <SelectItem value="video">Video</SelectItem>
            </SelectContent>
          </Select>

          {/* View Mode Toggle */}
          <div className="flex border rounded-lg p-1 bg-muted/30">
            <Button
              variant={viewMode === "grid" ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setViewMode("grid")}
              className="h-8 px-3"
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === "list" ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setViewMode("list")}
              className="h-8 px-3"
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing <span className="font-medium text-foreground">{paginatedPosts.length}</span> of{" "}
          <span className="font-medium text-foreground">{filteredPosts.length}</span> posts
        </p>
      </div>

      {/* Posts Grid/List */}
      {paginatedPosts.length > 0 ? (
        <div
          className={
            viewMode === "grid"
              ? "grid md:grid-cols-2 xl:grid-cols-3 gap-5"
              : "flex flex-col gap-3"
          }
        >
          {paginatedPosts.map((post, index) => {
            const formatConfig = getFormatConfig(post.format);
            const statusConfig = getStatusConfig(post.status);
            const FormatIcon = formatConfig.icon;

            return (
              <motion.div
                key={post.post_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03, duration: 0.2 }}
              >
                {viewMode === "grid" ? (
                  /* Grid Card */
                  <Card className="group relative overflow-hidden hover:shadow-lg transition-all duration-300 hover:border-primary/20">
                    {/* Top accent bar based on format */}
                    <div className={`h-1 w-full ${
                      post.format === "carousel" ? "bg-blue-500" : 
                      post.format === "video" ? "bg-purple-500" : "bg-emerald-500"
                    }`} />
                    
                    <div className="p-5">
                      {/* Header with format and actions */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <div className={`h-8 w-8 rounded-lg bg-secondary/80 flex items-center justify-center ${formatConfig.color}`}>
                            <FormatIcon className="h-4 w-4" />
                          </div>
                          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            {formatConfig.label}
                          </span>
                        </div>
                        
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-40">
                            <DropdownMenuItem asChild>
                              <Link to={`/app/posts/${post.post_id}`} className="cursor-pointer">
                                <Eye className="mr-2 h-4 w-4" /> View Details
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleCopy(post)} className="cursor-pointer">
                              <Copy className="mr-2 h-4 w-4" /> Copy Idea
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => handleDelete(post.post_id)}
                              className="text-destructive cursor-pointer focus:text-destructive"
                            >
                              <Trash2 className="mr-2 h-4 w-4" /> Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>

                      {/* Title */}
                      <h3 className="font-medium text-foreground leading-snug line-clamp-2 mb-4 min-h-[2.75rem]">
                        {post.raw_idea}
                      </h3>

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-4 border-t border-border/50">
                        <div className="flex items-center gap-3">
                          <Badge variant={statusConfig.variant} className="text-xs">
                            {statusConfig.label}
                          </Badge>
                          {post.quality_score && (
                            <div className="flex items-center gap-1 text-sm">
                              <Star className="h-3.5 w-3.5 text-amber-500 fill-amber-500" />
                              <span className="font-medium">{post.quality_score}</span>
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {formatDate(post.created_at)}
                        </div>
                      </div>
                    </div>
                  </Card>
                ) : (
                  /* List Card */
                  <Card className="group hover:shadow-md transition-all duration-200 hover:border-primary/20">
                    <div className="flex items-center gap-4 p-4">
                      {/* Format indicator */}
                      <div className={`h-10 w-10 rounded-lg bg-secondary/80 flex items-center justify-center flex-shrink-0 ${formatConfig.color}`}>
                        <FormatIcon className="h-5 w-5" />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={statusConfig.variant} className="text-xs">
                            {statusConfig.label}
                          </Badge>
                          <span className="text-xs text-muted-foreground uppercase tracking-wide">
                            {formatConfig.label}
                          </span>
                        </div>
                        <h3 className="font-medium text-foreground truncate">
                          {post.raw_idea}
                        </h3>
                      </div>

                      {/* Meta */}
                      <div className="flex items-center gap-6 flex-shrink-0">
                        {post.quality_score && (
                          <div className="flex items-center gap-1.5 text-sm">
                            <Star className="h-4 w-4 text-amber-500 fill-amber-500" />
                            <span className="font-medium">{post.quality_score}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1.5 text-sm text-muted-foreground min-w-[80px]">
                          <Clock className="h-3.5 w-3.5" />
                          {formatDate(post.created_at)}
                        </div>
                        
                        {/* Actions */}
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-40">
                            <DropdownMenuItem asChild>
                              <Link to={`/app/posts/${post.post_id}`} className="cursor-pointer">
                                <Eye className="mr-2 h-4 w-4" /> View Details
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleCopy(post)} className="cursor-pointer">
                              <Copy className="mr-2 h-4 w-4" /> Copy Idea
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => handleDelete(post.post_id)}
                              className="text-destructive cursor-pointer focus:text-destructive"
                            >
                              <Trash2 className="mr-2 h-4 w-4" /> Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </Card>
                )}
              </motion.div>
            );
          })}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <div className="h-14 w-14 mx-auto mb-4 rounded-xl bg-muted flex items-center justify-center">
            <FileText className="h-7 w-7 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold mb-1">No posts found</h3>
          <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
            {searchQuery || statusFilter !== "all" || formatFilter !== "all"
              ? "Try adjusting your filters to find what you're looking for"
              : "Get started by creating your first post"}
          </p>
          <Link to="/app/generate">
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Create Post
            </Button>
          </Link>
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-1.5 pt-4">
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <Button
              key={page}
              variant={currentPage === page ? "default" : "outline"}
              size="icon"
              className="h-9 w-9"
              onClick={() => setCurrentPage(page)}
            >
              {page}
            </Button>
          ))}
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}