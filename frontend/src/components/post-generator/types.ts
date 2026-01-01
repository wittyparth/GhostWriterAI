import { LucideIcon } from "lucide-react";

export type AgentStatus = "idle" | "active" | "complete" | "error" | "skipped";

export interface Agent {
  id: string;
  name: string;
  icon: LucideIcon;
  description: string;
  color: "validator" | "strategist" | "writer" | "visual" | "optimizer";
}

export interface AgentState {
  status: AgentStatus;
  progress: number;
  thoughts: string[];
  score?: number;
  duration?: number;
  decision?: string;
}

export interface Hook {
  text: string;
  type: string;
  score: number;
  explanation?: string;
}

export interface GeneratedPost {
  hooks: Hook[];
  content: string;
  hashtags: string[];
  metrics: {
    qualityScore: number;
    hookStrength: number;
    brandAlignment: number;
    predictedImpressions: string;
    engagementRate: string;
  };
}

export type PostFormat = "auto" | "text" | "carousel" | "story";