"""
Validation utilities for the LinkedIn Post Generator.
Provides input validation and data quality checks.
"""

import re
from typing import List, Dict, Any, Optional
from src.schemas.post import Post, PostMetadata


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_post_text(text: str) -> bool:
    """
    Validate post text content.
    
    Args:
        text: The post text to validate
        
    Returns:
        bool: True if valid, raises ValidationError if not
        
    Raises:
        ValidationError: If text is invalid
    """
    if not text or not text.strip():
        raise ValidationError("Post text cannot be empty")
    
    if len(text.strip()) < 10:
        raise ValidationError("Post text must be at least 10 characters long")
    
    if len(text) > 3000:
        raise ValidationError("Post text cannot exceed 3000 characters")
    
    # Check for excessive hashtags
    hashtag_count = text.count('#')
    if hashtag_count > 10:
        raise ValidationError("Post cannot have more than 10 hashtags")
    
    return True


def validate_hashtags(hashtags: List[str]) -> bool:
    """
    Validate hashtag format and content.
    
    Args:
        hashtags: List of hashtags to validate
        
    Returns:
        bool: True if valid, raises ValidationError if not
    """
    if not isinstance(hashtags, list):
        raise ValidationError("Hashtags must be a list")
    
    for hashtag in hashtags:
        if not hashtag.startswith('#'):
            raise ValidationError(f"Hashtag '{hashtag}' must start with #")
        
        if len(hashtag) < 2:
            raise ValidationError(f"Hashtag '{hashtag}' is too short")
        
        if len(hashtag) > 50:
            raise ValidationError(f"Hashtag '{hashtag}' is too long")
        
        # Check for valid characters
        if not re.match(r'^#[a-zA-Z0-9_]+$', hashtag):
            raise ValidationError(f"Hashtag '{hashtag}' contains invalid characters")
    
    return True


def validate_post_metadata(metadata: PostMetadata) -> bool:
    """
    Validate post metadata.
    
    Args:
        metadata: PostMetadata object to validate
        
    Returns:
        bool: True if valid, raises ValidationError if not
    """
    if metadata.topic and len(metadata.topic) > 100:
        raise ValidationError("Topic cannot exceed 100 characters")
    
    if metadata.tone and metadata.tone not in [
        'professional', 'casual', 'formal', 'friendly', 'authoritative', 
        'conversational', 'inspirational', 'educational', 'analytical'
    ]:
        raise ValidationError(f"Invalid tone: {metadata.tone}")
    
    if metadata.estimated_engagement and metadata.estimated_engagement not in [
        'low', 'medium', 'high', 'very_high'
    ]:
        raise ValidationError(f"Invalid engagement level: {metadata.estimated_engagement}")
    
    if metadata.quality_score and not (0 <= metadata.quality_score <= 10):
        raise ValidationError("Quality score must be between 0 and 10")
    
    return True


def validate_post_quality(post: Post) -> Dict[str, Any]:
    """
    Perform comprehensive quality validation on a post.
    
    Args:
        post: Post object to validate
        
    Returns:
        Dict containing quality metrics and validation results
    """
    quality_metrics = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'score': 0.0,
        'metrics': {}
    }
    
    try:
        # Basic text validation
        validate_post_text(post.text)
        
        # Hashtag validation
        if post.metadata.hashtags:
            validate_hashtags(post.metadata.hashtags)
        
        # Metadata validation
        validate_post_metadata(post.metadata)
        
        # Quality scoring
        score = calculate_post_quality_score(post)
        quality_metrics['score'] = score
        
        # Additional metrics
        quality_metrics['metrics'] = {
            'word_count': post.word_count,
            'line_count': post.line_count,
            'hashtag_count': post.hashtag_count,
            'has_question': post.has_question,
            'has_exclamation': post.has_exclamation,
            'length_category': post.length_category
        }
        
        # Warnings for potential improvements
        if post.word_count < 50:
            quality_metrics['warnings'].append("Post is quite short - consider adding more content")
        
        if post.hashtag_count == 0:
            quality_metrics['warnings'].append("No hashtags found - consider adding relevant hashtags")
        
        if not post.has_question and not post.has_exclamation:
            quality_metrics['warnings'].append("Post lacks engagement elements - consider adding questions or exclamations")
        
        if post.word_count > 500:
            quality_metrics['warnings'].append("Post is quite long - consider breaking it into multiple posts")
            
    except ValidationError as e:
        quality_metrics['is_valid'] = False
        quality_metrics['errors'].append(str(e))
    
    return quality_metrics


def calculate_post_quality_score(post: Post) -> float:
    """
    Calculate a quality score for a post based on various metrics.
    
    Args:
        post: Post object to score
        
    Returns:
        float: Quality score between 0 and 10
    """
    score = 0.0
    
    # Length score (0-2 points)
    if 50 <= post.word_count <= 300:
        score += 2.0
    elif 30 <= post.word_count < 50 or 300 < post.word_count <= 500:
        score += 1.0
    
    # Engagement elements (0-2 points)
    if post.has_question:
        score += 1.0
    if post.has_exclamation:
        score += 0.5
    if post.hashtag_count > 0:
        score += 0.5
    
    # Hashtag quality (0-1 point)
    if 1 <= post.hashtag_count <= 5:
        score += 1.0
    elif post.hashtag_count > 5:
        score += 0.5
    
    # Structure score (0-2 points)
    if post.line_count >= 3:  # Multiple paragraphs
        score += 1.0
    if '\n\n' in post.text:  # Proper paragraph breaks
        score += 1.0
    
    # Content quality indicators (0-2 points)
    if any(word in post.text.lower() for word in ['because', 'however', 'therefore', 'meanwhile']):
        score += 0.5  # Logical connectors
    if any(word in post.text.lower() for word in ['think', 'believe', 'suggest', 'recommend']):
        score += 0.5  # Personal insights
    if any(word in post.text.lower() for word in ['experience', 'learned', 'discovered', 'found']):
        score += 0.5  # Personal experience
    if any(word in post.text.lower() for word in ['tips', 'advice', 'strategies', 'methods']):
        score += 0.5  # Actionable content
    
    # Professional tone (0-1 point)
    professional_words = ['professional', 'industry', 'business', 'career', 'leadership', 'strategy']
    if any(word in post.text.lower() for word in professional_words):
        score += 1.0
    
    return min(score, 10.0)  # Cap at 10


def sanitize_text(text: str) -> str:
    """
    Sanitize text input for safe processing.
    
    Args:
        text: Raw text input
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>]', '', text)
    
    return text


def validate_length_category(length_category: str) -> bool:
    """
    Validate length category input.
    
    Args:
        length_category: Length category to validate
        
    Returns:
        bool: True if valid
    """
    valid_categories = ['Short', 'Medium', 'Long']
    if length_category not in valid_categories:
        raise ValidationError(f"Invalid length category. Must be one of: {valid_categories}")
    return True


def validate_language(language: str) -> bool:
    """
    Validate language input.
    
    Args:
        language: Language to validate
        
    Returns:
        bool: True if valid
    """
    valid_languages = ['English', 'Hinglish']
    if language not in valid_languages:
        raise ValidationError(f"Invalid language. Must be one of: {valid_languages}")
    return True 