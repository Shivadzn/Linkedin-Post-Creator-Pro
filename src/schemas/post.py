"""
Data models for LinkedIn posts and related entities.
Provides type safety and validation for post data structures.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


@dataclass
class PostMetadata:
    """Metadata for a LinkedIn post."""
    
    topic: Optional[str] = None
    tone: Optional[str] = None
    post_type: Optional[str] = None
    word_count: Optional[int] = None
    estimated_engagement: Optional[str] = None
    target_audience: Optional[str] = None
    best_posting_time: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    structure: Optional[str] = None
    engagement_drivers: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    virality_potential: Optional[str] = None
    emotional_tone: Optional[str] = None
    call_to_action: Optional[str] = None
    line_count: Optional[int] = None
    language: Optional[str] = None
    unified_tags: List[str] = field(default_factory=list)


@dataclass
class PostEngagement:
    """Engagement metrics for a LinkedIn post."""
    
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: Optional[int] = None
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement."""
        return self.likes + self.comments + self.shares


@dataclass
class Post:
    """A LinkedIn post with all its associated data."""
    
    id: str
    text: str
    metadata: PostMetadata = field(default_factory=PostMetadata)
    engagement: PostEngagement = field(default_factory=PostEngagement)
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.created_at is None:
            self.created_at = datetime.now()
        
        # Auto-calculate line_count if not provided
        if self.metadata.line_count is None:
            self.metadata.line_count = len(self.text.split('\n'))
        
        # Auto-calculate word_count if not provided
        if self.metadata.word_count is None:
            self.metadata.word_count = len(self.text.split())
    
    @property
    def line_count(self) -> int:
        """Get the line count of the post."""
        return self.metadata.line_count or len(self.text.split('\n'))
    
    @property
    def word_count(self) -> int:
        """Get the word count of the post."""
        return self.metadata.word_count or len(self.text.split())
    
    @property
    def hashtag_count(self) -> int:
        """Get the number of hashtags in the post."""
        return len(self.metadata.hashtags)
    
    @property
    def has_question(self) -> bool:
        """Check if the post contains a question."""
        return '?' in self.text
    
    @property
    def has_exclamation(self) -> bool:
        """Check if the post contains an exclamation."""
        return '!' in self.text
    
    @property
    def length_category(self) -> str:
        """Get the length category based on line count."""
        if self.line_count < 5:
            return "Short"
        elif 5 <= self.line_count <= 10:
            return "Medium"
        else:
            return "Long"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert post to dictionary format."""
        return {
            "id": self.id,
            "text": self.text,
            "metadata": {
                "topic": self.metadata.topic,
                "tone": self.metadata.tone,
                "post_type": self.metadata.post_type,
                "word_count": self.metadata.word_count,
                "estimated_engagement": self.metadata.estimated_engagement,
                "target_audience": self.metadata.target_audience,
                "best_posting_time": self.metadata.best_posting_time,
                "hashtags": self.metadata.hashtags,
                "structure": self.metadata.structure,
                "engagement_drivers": self.metadata.engagement_drivers,
                "quality_score": self.metadata.quality_score,
                "virality_potential": self.metadata.virality_potential,
                "emotional_tone": self.metadata.emotional_tone,
                "call_to_action": self.metadata.call_to_action,
                "line_count": self.metadata.line_count,
                "language": self.metadata.language,
                "unified_tags": self.metadata.unified_tags
            },
            "engagement": {
                "likes": self.engagement.likes,
                "comments": self.engagement.comments,
                "shares": self.engagement.shares,
                "views": self.engagement.views
            },
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Post':
        """Create a Post instance from dictionary data."""
        metadata = PostMetadata(**data.get('metadata', {}))
        engagement = PostEngagement(**data.get('engagement', {}))
        
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        return cls(
            id=data['id'],
            text=data['text'],
            metadata=metadata,
            engagement=engagement,
            created_at=created_at
        )


class PostGenerationRequest(BaseModel):
    """Request model for post generation."""
    
    length_category: str
    language: str
    tag: str
    max_retries: int = 3
    
    @field_validator('length_category')
    def validate_length_category(cls, v):
        if v not in ['Short', 'Medium', 'Long']:
            raise ValueError('Invalid length category. Must be Short, Medium, or Long.')
        return v
    
    @field_validator('language')
    def validate_language(cls, v):
        if v not in ['English', 'Hinglish']:
            raise ValueError('Invalid language. Must be English or Hinglish.')
        return v
    
    @field_validator('tag')
    def validate_tag(cls, v):
        if not v or not v.strip():
            raise ValueError('Tag cannot be empty.')
        return v.strip()


class PostQualityAssessment(BaseModel):
    """Quality assessment for a generated post."""
    
    score: float
    reasoning: str
    strengths: List[str]
    improvements: List[str]
    
    @field_validator('score')
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Score must be between 1 and 10.')
        return v 