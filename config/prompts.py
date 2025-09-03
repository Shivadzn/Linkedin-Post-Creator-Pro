"""
Prompt templates for the LinkedIn Post Generator.
Centralizes all LLM prompts for easy maintenance and consistency.
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates used throughout the application."""
    
    # Post generation prompt
    POST_GENERATION = """
Generate a LinkedIn post using the below information. Follow all instructions carefully. 
Do not include any preamble, conversational text, or extraneous information, just the post content.

1) Topic: The core subject of the post should be '{topic}'.
2) Length: The post should be approximately {length_instruction}.
3) Language: The post should be entirely in {language}.

{examples_section}

{style_guidance}
"""

    # Tag unification prompt
    TAG_UNIFICATION = """
I will give you a list of tags. You need to unify tags with the following requirements:

1. Tags should be unified and merged to create a shorter list.
   Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search".
   Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
   Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
   Example 4: "AI/Tech" should be mapped to "AI & Tech" or "AI/Tech" if that is the preferred term.
   Example 5: "Startup" should be mapped to "Startup".
   Example 6: "Career" should be mapped to "Career".
   Example 7: "Personal Story" should be mapped to "Personal Story".
   Example 8: "Industry Insights" should be mapped to "Industry Insights".
   Example 9: "Leadership" should be mapped to "Leadership".
   Example 10: "Productivity" should be mapped to "Productivity".
   Example 11: "Marketing" should be mapped to "Marketing".

2. Each tag should follow title case convention. For example: "Motivation", "Job Search".
3. Output should be a JSON object, with no preamble.
4. The output JSON should have a mapping of original tag and the unified tag.
   For example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search", "Motivation": "Motivation"}}

Here is the list of tags:
{tags}
"""

    # Metadata extraction prompt
    METADATA_EXTRACTION = """
You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
1. Return a valid JSON. No preamble.
2. JSON object should have exactly three keys: line_count, language and tags.
3. tags is an array of text tags. Extract maximum two tags.
4. Language should be English or Hinglish (Hinglish means hindi + english)

Here is the actual post on which you need to perform this task:
{post_text}
"""

    # Quality assessment prompt
    QUALITY_ASSESSMENT = """
Assess the quality of this LinkedIn post and provide a score from 1-10 with reasoning.

Post: {post_text}

Please provide your assessment in JSON format:
{{
    "score": <1-10>,
    "reasoning": "<explanation>",
    "strengths": ["<strength1>", "<strength2>"],
    "improvements": ["<improvement1>", "<improvement2>"]
}}
"""


def get_post_generation_prompt(
    topic: str,
    length_instruction: str,
    language: str,
    examples: list = None,
    style_guidance: str = "Generate the post in a professional LinkedIn style."
) -> str:
    """Generate the post generation prompt with examples."""
    
    examples_section = ""
    if examples and len(examples) > 0:
        examples_section = "\n4) Adopt the writing style, tone, and structure from the following examples. These examples are real LinkedIn posts related to the topic and length you requested."
        for i, post in enumerate(examples):
            post_text = post.get('text', 'No text available.')
            examples_section += f'\n\n--- Example {i+1} ---\n{post_text}'
            if i >= 1:  # Use max two samples
                break
    else:
        examples_section = "\n4) No specific examples were provided."
    
    return PromptTemplates.POST_GENERATION.format(
        topic=topic,
        length_instruction=length_instruction,
        language=language,
        examples_section=examples_section,
        style_guidance=style_guidance
    )


def get_tag_unification_prompt(tags: str) -> str:
    """Generate the tag unification prompt."""
    return PromptTemplates.TAG_UNIFICATION.format(tags=tags)


def get_metadata_extraction_prompt(post_text: str) -> str:
    """Generate the metadata extraction prompt."""
    return PromptTemplates.METADATA_EXTRACTION.format(post_text=post_text)


def get_quality_assessment_prompt(post_text: str) -> str:
    """Generate the quality assessment prompt."""
    return PromptTemplates.QUALITY_ASSESSMENT.format(post_text=post_text) 