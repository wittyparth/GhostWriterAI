import { authFetch } from "./auth";
import { PostListResponse } from "@/types/api";

export async function getPosts(limit = 20, offset = 0): Promise<PostListResponse> {
  return authFetch<PostListResponse>(`/api/v1/posts/?limit=${limit}&offset=${offset}`);
}

export async function deletePost(postId: string): Promise<void> {
  return authFetch<void>(`/api/v1/posts/${postId}`, { method: 'DELETE' });
}
// ...

export interface AnalyticsData {
  total_posts: number;
  avg_quality_score: number;
  total_impressions: number;
  engagement_rate: number;
  format_distribution: { name: string; value: number }[];
  status_distribution: { status: string; count: number }[];
}

export async function getAnalytics(): Promise<AnalyticsData> {
  return authFetch<AnalyticsData>('/api/v1/posts/analytics');
}
