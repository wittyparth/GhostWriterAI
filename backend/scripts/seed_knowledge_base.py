"""
Knowledge base seeder script.

Seeds the vector database with sample LinkedIn posts, hooks, and structures.
"""

import asyncio
from src.rag import get_retriever
from src.config.constants import (
    STRUCTURE_STORY,
    STRUCTURE_LIST,
    STRUCTURE_FRAMEWORK,
    HOOK_PERSONAL_STORY,
    HOOK_DATA_SHOCK,
    HOOK_CONTRARIAN,
    HOOK_QUESTION,
)

# Sample reference posts for seeding
SAMPLE_POSTS = [
    {
        "content": """I failed 3 startups before I was 30.

Each one taught me something irreplaceable:

1. Startup #1: Don't build what YOU want
   → Build what customers will PAY for

2. Startup #2: Co-founder alignment matters more than skills
   → Values > capabilities

3. Startup #3: Speed beats perfection
   → Ship fast, iterate faster

The 4th startup? We hit $1M ARR in 8 months.

Not because I got smarter.
Because I got humbler.

What's your biggest startup lesson?""",
        "metadata": {
            "format": "text",
            "structure_type": STRUCTURE_LIST,
            "hook_type": HOOK_PERSONAL_STORY,
            "niche": "startups",
            "engagement_rate": 0.065,
            "impressions": 45000,
        }
    },
    {
        "content": """93% of hiring managers admit they've rejected qualified candidates for "culture fit."

But here's what they really mean:

→ "Too old" = won't work overtime
→ "Not a fit" = asked about work-life balance  
→ "Overqualified" = might want more money later

The secret to getting hired in 2024:

Mirror their energy in interviews.
Match their communication style.
Research who's interviewing you on LinkedIn.

Controversial? Maybe.
Effective? Absolutely.

What's the strangest reason you've been rejected?""",
        "metadata": {
            "format": "text",
            "structure_type": STRUCTURE_FRAMEWORK,
            "hook_type": HOOK_DATA_SHOCK,
            "niche": "career",
            "engagement_rate": 0.082,
            "impressions": 78000,
        }
    },
    {
        "content": """Unpopular opinion: Hustle culture is dead.

And I say this as someone who worked 80-hour weeks for 5 years.

Here's what I learned:

The best performers I know:
• Sleep 8 hours
• Take real vacations
• Say "no" more than "yes"
• Work intensely for 4-5 hours max

The struggling ones:
• Glorify being busy
• Check email at midnight
• Mistake activity for progress

Your productivity isn't measured in hours.
It's measured in outcomes.

Agree or disagree?""",
        "metadata": {
            "format": "text",
            "structure_type": STRUCTURE_CONTRARIAN,
            "hook_type": HOOK_CONTRARIAN,
            "niche": "productivity",
            "engagement_rate": 0.091,
            "impressions": 92000,
        }
    },
]

# Sample hooks for the knowledge base
SAMPLE_HOOKS = [
    {"text": "I got fired on my birthday. Best thing that ever happened.", "hook_type": HOOK_PERSONAL_STORY, "score": 9.2},
    {"text": "78% of employees quit their boss, not their job.", "hook_type": HOOK_DATA_SHOCK, "score": 8.8},
    {"text": "Hot take: Your morning routine doesn't matter.", "hook_type": HOOK_CONTRARIAN, "score": 8.5},
    {"text": "What if everything you know about networking is wrong?", "hook_type": HOOK_QUESTION, "score": 8.1},
    {"text": "I said no to a $500K offer. Here's why:", "hook_type": HOOK_PERSONAL_STORY, "score": 9.0},
]

# Sample structure templates
SAMPLE_STRUCTURES = [
    {
        "template": "Story Arc: Hook → Setup → Conflict → Resolution → Lesson → CTA",
        "metadata": {"structure_type": STRUCTURE_STORY, "best_for": ["personal experiences", "lessons learned"]},
    },
    {
        "template": "List Format: Bold claim → Numbered list → Summary → Question CTA",
        "metadata": {"structure_type": STRUCTURE_LIST, "best_for": ["actionable tips", "frameworks"]},
    },
    {
        "template": "Framework: Problem → Common belief → Reality check → New framework → Application",
        "metadata": {"structure_type": STRUCTURE_FRAMEWORK, "best_for": ["thought leadership", "methodology"]},
    },
]


async def seed_knowledge_base():
    """Seed the knowledge base with sample data."""
    retriever = get_retriever()
    
    print("🌱 Seeding knowledge base...")
    
    # Add reference posts
    for i, post in enumerate(SAMPLE_POSTS):
        doc_id = await retriever.add_reference_post(
            content=post["content"],
            metadata=post["metadata"],
        )
        print(f"  ✓ Added post {i+1}: {doc_id[:8]}...")
    
    # Add hooks
    for hook in SAMPLE_HOOKS:
        await retriever.add_hook_example(
            hook_text=hook["text"],
            metadata={"hook_type": hook["hook_type"], "score": hook["score"]},
        )
    print(f"  ✓ Added {len(SAMPLE_HOOKS)} hook examples")
    
    # Add structures
    for struct in SAMPLE_STRUCTURES:
        await retriever.add_structure_template(
            template=struct["template"],
            metadata=struct["metadata"],
        )
    print(f"  ✓ Added {len(SAMPLE_STRUCTURES)} structure templates")
    
    print("\n✅ Knowledge base seeded successfully!")
    print(f"   Posts: {len(SAMPLE_POSTS)}")
    print(f"   Hooks: {len(SAMPLE_HOOKS)}")
    print(f"   Structures: {len(SAMPLE_STRUCTURES)}")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
