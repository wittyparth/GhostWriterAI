/**
 * Brand Profile Service
 * 
 * API functions for managing user brand profiles.
 */

import { authFetch } from './auth';

// ============ Types ============

export interface ContentPillar {
  id: string;
  name: string;
  description: string;
  color: string;
}

export interface VoiceTone {
  formality: number;
  humor: number;
  emotion: number;
  technicality: number;
}

export interface BrandProfile {
  profile_id: string;
  user_id: string;
  name: string;
  title?: string;
  bio?: string;
  content_pillars: ContentPillar[];
  target_audience?: string;
  voice_tone: VoiceTone;
  brand_colors: string[];
  created_at: string;
  updated_at?: string;
}

export interface BrandProfileInput {
  name?: string;
  title?: string;
  bio?: string;
  content_pillars?: ContentPillar[];
  target_audience?: string;
  voice_tone?: VoiceTone;
  brand_colors?: string[];
}

export interface ProfileSummary {
  has_profile: boolean;
  name?: string;
  content_pillars?: string[];
  target_audience?: string;
  voice_description?: string;
  summary?: string;
}

// ============ API Functions ============

/**
 * Get current user's brand profile
 */
export async function getBrandProfile(): Promise<BrandProfile | null> {
  return authFetch<BrandProfile | null>('/api/v1/brand-profile/');
}

/**
 * Create a new brand profile
 */
export async function createBrandProfile(data: BrandProfileInput): Promise<BrandProfile> {
  return authFetch<BrandProfile>('/api/v1/brand-profile/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update existing brand profile
 */
export async function updateBrandProfile(data: BrandProfileInput): Promise<BrandProfile> {
  return authFetch<BrandProfile>('/api/v1/brand-profile/', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Add a content pillar
 */
export async function addContentPillar(pillar: Omit<ContentPillar, 'id'>): Promise<{ pillar: ContentPillar; total_pillars: number }> {
  return authFetch('/api/v1/brand-profile/pillars', {
    method: 'POST',
    body: JSON.stringify(pillar),
  });
}

/**
 * Remove a content pillar
 */
export async function removeContentPillar(pillarId: string): Promise<{ message: string; remaining_pillars: number }> {
  return authFetch(`/api/v1/brand-profile/pillars/${pillarId}`, {
    method: 'DELETE',
  });
}

/**
 * Update voice/tone settings
 */
export async function updateVoiceSettings(voice: VoiceTone): Promise<{ message: string; voice_tone: VoiceTone }> {
  return authFetch('/api/v1/brand-profile/voice', {
    method: 'PATCH',
    body: JSON.stringify(voice),
  });
}

/**
 * Get profile summary for generation
 */
export async function getProfileSummary(): Promise<ProfileSummary> {
  return authFetch<ProfileSummary>('/api/v1/brand-profile/summary');
}
