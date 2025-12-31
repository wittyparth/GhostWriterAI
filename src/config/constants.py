"""
Application constants and configuration values.

These are hardcoded values that don't change based on environment.
"""

# ========== LinkedIn Post Constraints ==========
LINKEDIN_MAX_POST_CHARS = 3000
LINKEDIN_OPTIMAL_MIN_CHARS = 600
LINKEDIN_OPTIMAL_MAX_CHARS = 1200
LINKEDIN_HOOK_MAX_LINES = 2
LINKEDIN_OPTIMAL_HASHTAGS = (3, 5)  # min, max

# ========== Agent Names ==========
AGENT_VALIDATOR = "validator"
AGENT_STRATEGIST = "strategist"
AGENT_WRITER = "writer"
AGENT_VISUAL = "visual"
AGENT_OPTIMIZER = "optimizer"

# ========== Post Formats ==========
FORMAT_TEXT = "text"
FORMAT_CAROUSEL = "carousel"
FORMAT_VIDEO = "video"

POST_FORMATS = [FORMAT_TEXT, FORMAT_CAROUSEL, FORMAT_VIDEO]

# ========== Structure Types ==========
STRUCTURE_STORY = "story_post"
STRUCTURE_LIST = "list_post"
STRUCTURE_FRAMEWORK = "framework_post"
STRUCTURE_DATA = "data_post"
STRUCTURE_QUESTION = "question_post"
STRUCTURE_ACHIEVEMENT = "achievement_post"
STRUCTURE_CONTRARIAN = "contrarian_post"

STRUCTURE_TYPES = [
    STRUCTURE_STORY,
    STRUCTURE_LIST,
    STRUCTURE_FRAMEWORK,
    STRUCTURE_DATA,
    STRUCTURE_QUESTION,
    STRUCTURE_ACHIEVEMENT,
    STRUCTURE_CONTRARIAN,
]

# ========== Hook Types ==========
HOOK_DATA_SHOCK = "data_shock"
HOOK_PERSONAL_STORY = "personal_story"
HOOK_CONTRARIAN = "contrarian"
HOOK_QUESTION = "question"
HOOK_PATTERN_INTERRUPT = "pattern_interrupt"
HOOK_VULNERABILITY = "vulnerability"

HOOK_TYPES = [
    HOOK_DATA_SHOCK,
    HOOK_PERSONAL_STORY,
    HOOK_CONTRARIAN,
    HOOK_QUESTION,
    HOOK_PATTERN_INTERRUPT,
    HOOK_VULNERABILITY,
]

# ========== Psychological Triggers ==========
TRIGGER_CURIOSITY_GAP = "curiosity_gap"
TRIGGER_SOCIAL_PROOF = "social_proof"
TRIGGER_LOSS_AVERSION = "loss_aversion"
TRIGGER_RECIPROCITY = "reciprocity"
TRIGGER_AUTHORITY = "authority"
TRIGGER_SCARCITY = "scarcity"

PSYCHOLOGICAL_TRIGGERS = [
    TRIGGER_CURIOSITY_GAP,
    TRIGGER_SOCIAL_PROOF,
    TRIGGER_LOSS_AVERSION,
    TRIGGER_RECIPROCITY,
    TRIGGER_AUTHORITY,
    TRIGGER_SCARCITY,
]

# ========== Tone Types ==========
TONE_CONVERSATIONAL = "conversational"
TONE_AUTHORITATIVE = "authoritative"
TONE_PROVOCATIVE = "provocative"
TONE_SUPPORTIVE = "supportive"
TONE_ANALYTICAL = "analytical"

TONE_TYPES = [
    TONE_CONVERSATIONAL,
    TONE_AUTHORITATIVE,
    TONE_PROVOCATIVE,
    TONE_SUPPORTIVE,
    TONE_ANALYTICAL,
]

# ========== Validator Decisions ==========
DECISION_APPROVE = "APPROVE"
DECISION_REFINE = "REFINE"
DECISION_REJECT = "REJECT"

VALIDATOR_DECISIONS = [DECISION_APPROVE, DECISION_REFINE, DECISION_REJECT]

# ========== Quality Thresholds ==========
MIN_QUALITY_SCORE_APPROVE = 7.0
MIN_QUALITY_SCORE_REFINE = 5.0
MAX_HOOK_SCORE = 10.0

# ========== Performance Multipliers ==========
FORMAT_MULTIPLIERS = {
    FORMAT_TEXT: 1.0,
    FORMAT_CAROUSEL: 1.4,
    FORMAT_VIDEO: 1.2,
}

# ========== Carousel Constraints ==========
CAROUSEL_MIN_SLIDES = 8
CAROUSEL_MAX_SLIDES = 12
CAROUSEL_OPTIMAL_SLIDES = 10
CAROUSEL_CHARS_PER_SLIDE = 150

# ========== RAG Configuration ==========
RAG_TOP_K_DEFAULT = 10
RAG_SIMILARITY_THRESHOLD = 0.7
RAG_NAMESPACE_REFERENCE = "reference_posts"
RAG_NAMESPACE_USER = "user_posts"
RAG_NAMESPACE_HOOKS = "hooks"
RAG_NAMESPACE_STRUCTURES = "structures"

# ========== Token Limits ==========
GEMINI_CONTEXT_LIMIT = 1_048_576
GEMINI_OUTPUT_LIMIT = 65_536
EMBEDDING_DIMENSION = 768  # text-embedding-004

# ========== Cost Tracking (USD per 1M tokens) ==========
# Gemini 3 Flash Preview pricing (approximate)
COST_INPUT_PER_MILLION = 0.075
COST_OUTPUT_PER_MILLION = 0.30
COST_EMBEDDING_PER_MILLION = 0.00005
