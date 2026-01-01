/**
 * Custom hook for post generation with streaming API integration
 */

import { useCallback, useRef } from 'react';
import { useGenerationStore } from '@/stores/generationStore';
import { streamGeneration, streamAnswers, StreamCallbacks } from '@/services/streaming';

type AgentName = 'validator' | 'strategist' | 'writer' | 'visual' | 'optimizer';

export function useGeneration() {
  const store = useGenerationStore();
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Start Phase 1: Generate post and get clarifying questions
   */
  const startGeneration = useCallback(() => {
    const { rawIdea, preferredFormat, setCurrentStep, updateAgentExecution, 
            addAgentThought, setValidatorOutput, setStrategistOutput,
            setPostId, setIsGenerating, setError, resetGeneration } = store;

    if (!rawIdea.trim()) {
      setError('Please enter an idea to generate a post');
      return;
    }

    // Reset previous state
    resetGeneration();
    store.setRawIdea(rawIdea);
    store.setPreferredFormat(preferredFormat);
    
    setCurrentStep('validator');
    setIsGenerating(true);
    setError(null);

    const callbacks: StreamCallbacks = {
      onPostId: (postId) => {
        setPostId(postId);
      },
      
      onAgentStart: (agentName, message, progress) => {
        const agent = agentName as AgentName;
        if (['validator', 'strategist', 'writer', 'visual', 'optimizer'].includes(agent)) {
          updateAgentExecution(agent, { 
            status: 'active', 
            progress: 0, 
            thoughts: [],
            started_at: Date.now() 
          });
          addAgentThought(agent, message);
          
          // Update current step based on agent
          if (agent === 'validator') setCurrentStep('validator');
          else if (agent === 'strategist') setCurrentStep('strategist');
        }
      },
      
      onAgentComplete: (agentName, data, executionTimeMs, progress) => {
        const agent = agentName as AgentName;
        
        if (agent === 'validator' && data.output) {
          updateAgentExecution('validator', { 
            status: 'success', 
            progress: 100,
            execution_time_ms: executionTimeMs 
          });
          setValidatorOutput(data.output);
          addAgentThought('validator', `Decision: ${data.decision} | Quality: ${data.score}/10`);
        }
        
        if (agent === 'strategist' && data.output) {
          updateAgentExecution('strategist', { 
            status: 'success', 
            progress: 100,
            execution_time_ms: executionTimeMs 
          });
          setStrategistOutput(data.output);
          addAgentThought('strategist', `Format: ${data.output.recommended_format} | Questions: ${data.output.clarifying_questions?.length || 0}`);
        }
      },
      
      onAgentError: (agentName, error, attempt) => {
        const agent = agentName as AgentName;
        if (['validator', 'strategist'].includes(agent)) {
          addAgentThought(agent as AgentName, `Error: ${error}${attempt ? ` (attempt ${attempt})` : ''}`);
        }
      },
      
      onStatusUpdate: (message, progress) => {
        console.log('Status update:', message, progress);
      },
      
      onComplete: (data) => {
        setIsGenerating(false);
        
        if (data.status === 'awaiting_answers') {
          // Phase 1 complete - show questions
          setCurrentStep('questions');
          
          // Set strategist output with questions if not already set
          if (data.questions && !store.strategistOutput) {
            setStrategistOutput({
              recommended_format: 'text',
              format_reasoning: '',
              structure_type: '',
              hook_types: [],
              psychological_triggers: [],
              tone: '',
              clarifying_questions: data.questions,
              similar_posts: [],
            });
          }
        } else if (data.status === 'rejected') {
          setError(`Idea rejected: ${data.reason || 'The idea did not meet quality requirements'}`);
          setCurrentStep('input');
        }
      },
      
      onError: (error) => {
        setIsGenerating(false);
        setError(error.message || 'An error occurred during generation');
        console.error('Generation error:', error);
      },
    };

    abortControllerRef.current = streamGeneration(
      { raw_idea: rawIdea, preferred_format: preferredFormat },
      callbacks
    );
  }, [store]);

  /**
   * Start Phase 2: Submit answers and complete generation
   */
  const submitAnswers = useCallback(() => {
    const { postId, questionAnswers, setCurrentStep, updateAgentExecution,
            addAgentThought, setWriterOutput, setOptimizerOutput, setVisualOutput,
            setFinalPost, setIsGenerating, setError, strategistOutput } = store;

    if (!postId) {
      setError('No active generation session');
      return;
    }

    setCurrentStep('writer');
    setIsGenerating(true);
    setError(null);

    // Skip visual agent if not carousel
    if (!strategistOutput || strategistOutput.recommended_format !== 'carousel') {
      updateAgentExecution('visual', { status: 'skipped' });
    }

    const callbacks: StreamCallbacks = {
      onAgentStart: (agentName, message, progress) => {
        const agent = agentName as AgentName;
        if (['writer', 'visual', 'optimizer'].includes(agent)) {
          updateAgentExecution(agent, { 
            status: 'active', 
            progress: 0,
            thoughts: [],
            started_at: Date.now() 
          });
          addAgentThought(agent, message);
          
          // Update current step
          if (agent === 'writer') setCurrentStep('writer');
          else if (agent === 'visual') setCurrentStep('visual');
          else if (agent === 'optimizer') setCurrentStep('optimizer');
        }
      },
      
      onAgentComplete: (agentName, data, executionTimeMs, progress) => {
        const agent = agentName as AgentName;
        
        if (agent === 'writer' && data.output) {
          updateAgentExecution('writer', { 
            status: 'success', 
            progress: 100,
            execution_time_ms: executionTimeMs 
          });
          setWriterOutput(data.output);
          const hookCount = data.output.hooks?.length || 0;
          addAgentThought('writer', `Generated ${hookCount} hook variations`);
        }
        
        if (agent === 'visual' && data.output) {
          updateAgentExecution('visual', { 
            status: 'success', 
            progress: 100,
            execution_time_ms: executionTimeMs 
          });
          setVisualOutput(data.output);
          addAgentThought('visual', 'Visual specs generated');
        }
        
        if (agent === 'optimizer' && data.output) {
          updateAgentExecution('optimizer', { 
            status: 'success', 
            progress: 100,
            execution_time_ms: executionTimeMs 
          });
          setOptimizerOutput(data.output);
          addAgentThought('optimizer', `Decision: ${data.decision} | Quality: ${data.score}/10`);
        }
      },
      
      onAgentError: (agentName, error, attempt) => {
        const agent = agentName as AgentName;
        if (['writer', 'visual', 'optimizer'].includes(agent)) {
          addAgentThought(agent as AgentName, `Error: ${error}`);
        }
      },
      
      onComplete: (data) => {
        setIsGenerating(false);
        
        if (data.status === 'completed' && data.final_post) {
          const post = data.final_post;
          
          // Build final post object
          const finalPost = {
            format: post.format || 'text',
            hook: post.hook || (post.hooks?.[0]) || { version: 1, text: '', hook_type: '', score: 0, reasoning: '' },
            body: post.body || post.body_content || '',
            cta: post.cta || '',
            hashtags: post.hashtags || [],
            visual_specs: post.visual_specs || null,
            quality_score: post.quality_score || data.quality_score || 0,
            predicted_impressions: post.predicted_impressions || [0, 0] as [number, number],
          };
          
          setFinalPost(finalPost);
          setCurrentStep('review');
        } else if (data.status === 'failed') {
          setError(data.error_message || 'Generation failed');
        }
      },
      
      onError: (error) => {
        setIsGenerating(false);
        setError(error.message || 'An error occurred');
        console.error('Answers error:', error);
      },
    };

    abortControllerRef.current = streamAnswers(postId, questionAnswers, callbacks);
  }, [store]);

  /**
   * Cancel ongoing generation
   */
  const cancelGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    store.setIsGenerating(false);
  }, [store]);

  /**
   * Reset and start over
   */
  const startOver = useCallback(() => {
    cancelGeneration();
    store.resetGeneration();
  }, [cancelGeneration, store]);

  return {
    // State
    currentStep: store.currentStep,
    rawIdea: store.rawIdea,
    isGenerating: store.isGenerating,
    error: store.error,
    postId: store.postId,
    agents: store.agents,
    validatorOutput: store.validatorOutput,
    strategistOutput: store.strategistOutput,
    writerOutput: store.writerOutput,
    visualOutput: store.visualOutput,
    optimizerOutput: store.optimizerOutput,
    questionAnswers: store.questionAnswers,
    finalPost: store.finalPost,
    selectedHookIndex: store.selectedHookIndex,
    
    // Actions
    setRawIdea: store.setRawIdea,
    setPreferredFormat: store.setPreferredFormat,
    setQuestionAnswer: store.setQuestionAnswer,
    setSelectedHookIndex: store.setSelectedHookIndex,
    
    // Generation actions
    startGeneration,
    submitAnswers,
    cancelGeneration,
    startOver,
  };
}
