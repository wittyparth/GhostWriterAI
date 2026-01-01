import { authFetch } from "./auth";
import { PostListResponse } from "@/types/api";

export async function getPosts(limit = 20, offset = 0): Promise<PostListResponse> {
  return authFetch<PostListResponse>(`/api/v1/posts/?limit=${limit}&offset=${offset}`);
}

export async function deletePost(postId: string): Promise<void> {
  return authFetch<void>(`/api/v1/posts/${postId}`, { method: 'DELETE' });
}
