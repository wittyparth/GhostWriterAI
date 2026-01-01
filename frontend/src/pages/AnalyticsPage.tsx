import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart3, TrendingUp, FileText, Star, Calendar, PieChart, Activity } from "lucide-react";
import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart as RechartsPie, Pie, Cell,
} from "recharts";

const postsOverTimeData = [
  { date: "Jan 1", posts: 3 },
  { date: "Jan 5", posts: 5 },
  { date: "Jan 10", posts: 2 },
  { date: "Jan 15", posts: 7 },
  { date: "Jan 20", posts: 4 },
  { date: "Jan 25", posts: 6 },
  { date: "Jan 30", posts: 8 },
];

const qualityScoreData = [
  { date: "Jan 1", score: 7.5 },
  { date: "Jan 5", score: 8.0 },
  { date: "Jan 10", score: 7.8 },
  { date: "Jan 15", score: 8.5 },
  { date: "Jan 20", score: 8.2 },
  { date: "Jan 25", score: 8.7 },
  { date: "Jan 30", score: 9.0 },
];

const formatDistribution = [
  { name: "Text", value: 15, color: "hsl(234 62% 50%)" },
  { name: "Carousel", value: 8, color: "hsl(220 70% 60%)" },
  { name: "Video", value: 3, color: "hsl(152 60% 36%)" },
];

const statusDistribution = [
  { status: "Completed", count: 20 },
  { status: "Processing", count: 2 },
  { status: "Failed", count: 1 },
  { status: "Pending", count: 3 },
];

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("30d");

  const stats = [
    { label: "Total Posts", value: "26", icon: FileText, change: "+8 this month", changeType: "positive" },
    { label: "Avg. Quality", value: "8.3", icon: Star, change: "+0.5 vs last month", changeType: "positive" },
    { label: "Completed", value: "20", icon: Activity, change: "77% success rate", changeType: "neutral" },
    { label: "This Week", value: "5", icon: Calendar, change: "Posts generated", changeType: "neutral" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground mt-1">Track your content generation performance</p>
        </div>
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Time range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">Last 7 days</SelectItem>
            <SelectItem value="30d">Last 30 days</SelectItem>
            <SelectItem value="90d">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}>
            <Card>
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-3xl font-semibold mt-1 tracking-tight">{stat.value}</p>
                    <p className={`text-xs mt-2 ${stat.changeType === "positive" ? "text-success" : "text-muted-foreground"}`}>{stat.change}</p>
                  </div>
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <stat.icon className="h-5 w-5 text-primary" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2 mb-6">
                <BarChart3 className="h-5 w-5 text-muted-foreground" />
                <h3 className="font-semibold">Posts Generated</h3>
              </div>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={postsOverTimeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                    <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px" }} />
                    <Bar dataKey="posts" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2 mb-6">
                <TrendingUp className="h-5 w-5 text-muted-foreground" />
                <h3 className="font-semibold">Quality Score Trend</h3>
              </div>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={qualityScoreData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                    <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} domain={[0, 10]} />
                    <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px" }} />
                    <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ fill: "hsl(var(--primary))", strokeWidth: 0 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid lg:grid-cols-3 gap-6">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2 mb-6">
                <PieChart className="h-5 w-5 text-muted-foreground" />
                <h3 className="font-semibold">Format Distribution</h3>
              </div>
              <div className="h-[180px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPie>
                    <Pie data={formatDistribution} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={5} dataKey="value">
                      {formatDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px" }} />
                  </RechartsPie>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-4">
                {formatDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-muted-foreground">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2 mb-6">
                <Activity className="h-5 w-5 text-muted-foreground" />
                <h3 className="font-semibold">Status Breakdown</h3>
              </div>
              <div className="space-y-4">
                {statusDistribution.map((item) => (
                  <div key={item.status}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-muted-foreground">{item.status}</span>
                      <span className="font-medium">{item.count}</span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${item.status === "Completed" ? "bg-success" : item.status === "Processing" ? "bg-primary" : item.status === "Pending" ? "bg-warning" : "bg-destructive"}`} style={{ width: `${(item.count / 26) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">Top Performing</h3>
              <div className="space-y-3">
                {[
                  { idea: "3 lessons from failing...", score: 9.2 },
                  { idea: "Why I quit my corporate...", score: 8.9 },
                  { idea: "The networking strategy...", score: 8.7 },
                ].map((post, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <div className="h-8 w-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center text-sm font-bold">#{index + 1}</div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{post.idea}</p>
                    </div>
                    <div className="flex items-center gap-1 text-success">
                      <Star className="h-3.5 w-3.5" />
                      <span className="text-sm font-medium">{post.score}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
