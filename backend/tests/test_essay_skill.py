"""
Tests for Ship 30 for 30 Essay Generation Skill
"""

import pytest
from app.providers.mock_provider import MockOfflineProvider
from app.agent.essay_skill import generate_ship30_essay


@pytest.mark.asyncio
async def test_essay_generation_anatomy():
    provider = MockOfflineProvider()
    topic = "Why retention eats acquisition in B2B SaaS"

    title, essay_md, citations, meta = await generate_ship30_essay(
        topic=topic,
        provider=provider,
        target_words=1250
    )

    # Validate structure
    assert "# " in essay_md  # Headline
    assert "## " in essay_md  # Subsections
    assert "**" in essay_md   # Selective bolding
    assert "*" in essay_md or "-" in essay_md  # Bullet lists
    assert "Golden Takeaway" in essay_md  # Actionable takeaway

    # Validate Word count
    words = essay_md.split()
    assert len(words) >= 400  # Fallback template provides rich structured essay
    assert meta["target_words"] == 1250
    assert "word_count" in meta
