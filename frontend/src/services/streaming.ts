/**
 * SSE Streaming Service for real-time agent updates
 * 
 * Handles Server-Sent Events from the backend streaming API
 */

import { IdeaInput } from './api';
import { API_BASE_URL } from './config';
import { getAccessToken } from './auth';

// ============ Types for Streaming ============

export interface AgentEvent {
  event_type: 'agent_start' | 'agent_complete' | 'agent_error' | 'status_update' | 'complete';
  agent_name: string;
  message: string;
  timestamp: string;
  execution_time_ms: number;
  data: Record<string, any>;
  progress_percent: number;
}

export interface StreamCallbacks {
  onAgentStart?: (agentName: string, message: string, progress: number) => void;
  onAgentComplete?: (agentName: string, output: any, executionTimeMs: number, progress: number) => void;
  onAgentError?: (agentName: string, error: string, attempt?: number) => void;
  onStatusUpdate?: (message: string, progress: number) => void;
  onComplete?: (data: any) => void;
  onError?: (error: Error) => void;
  onPostId?: (postId: string) => void;
}

// ============ SSE Parsing ============

function parseSSEMessage(data: string): AgentEvent | null {
  try {
    return JSON.parse(data) as AgentEvent;
  } catch (e) {
    console.warn('Failed to parse SSE message:', data);
    return null;
  }
}

// ============ Streaming Functions ============

/**
 * Stream post generation with real-time agent updates
 * 
 * @param input - The idea input
 * @param callbacks - Event callbacks for agent updates
 * @returns AbortController to cancel the stream
 */
export function streamGeneration(
  input: IdeaInput,
  callbacks: StreamCallbacks
): AbortController {
  const controller = new AbortController();
  
  const startStream = async () => {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };
      
      const token = getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/posts/generate/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify(input),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      // Get post_id from header if available
      const postId = response.headers.get('X-Post-ID');
      if (postId && callbacks.onPostId) {
        callbacks.onPostId(postId);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            const event = parseSSEMessage(data);
            if (event) {
              handleEvent(event, callbacks);
            }
          }
        }
      }
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        console.log('Stream aborted');
        return;
      }
      callbacks.onError?.(error as Error);
    }
  };

  startStream();
  return controller;
}

/**
 * Stream answers submission with real-time agent updates (Phase 2)
 * 
 * @param postId - The post ID from Phase 1
 * @param answers - User answers to clarifying questions
 * @param callbacks - Event callbacks for agent updates
 * @returns AbortController to cancel the stream
 */
export function streamAnswers(
  postId: string,
  answers: Record<string, string>,
  callbacks: StreamCallbacks
): AbortController {
  const controller = new AbortController();
  
  const startStream = async () => {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };
      
      const token = getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/posts/${postId}/answers/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify(answers),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            const event = parseSSEMessage(data);
            if (event) {
              handleEvent(event, callbacks);
            }
          }
        }
      }
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        console.log('Stream aborted');
        return;
      }
      callbacks.onError?.(error as Error);
    }
  };

  startStream();
  return controller;
}

// ============ Event Handler ============

function handleEvent(event: AgentEvent, callbacks: StreamCallbacks): void {
  switch (event.event_type) {
    case 'agent_start':
      callbacks.onAgentStart?.(
        event.agent_name,
        event.message,
        event.progress_percent
      );
      break;

    case 'agent_complete':
      callbacks.onAgentComplete?.(
        event.agent_name,
        event.data,
        event.execution_time_ms,
        event.progress_percent
      );
      break;

    case 'agent_error':
      callbacks.onAgentError?.(
        event.agent_name,
        event.data?.error || event.message,
        event.data?.attempt
      );
      break;

    case 'status_update':
      callbacks.onStatusUpdate?.(
        event.message,
        event.progress_percent
      );
      break;

    case 'complete':
      callbacks.onComplete?.(event.data);
      break;

    default:
      console.warn('Unknown event type:', event.event_type);
  }
}

// ============ Utility ============

/**
 * Check if EventSource is supported (for fallback)
 */
export function isSSESupported(): boolean {
  return typeof EventSource !== 'undefined';
}
