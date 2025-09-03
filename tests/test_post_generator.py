"""
Unit tests for the LinkedIn Post Generator.
Tests core functionality and edge cases.
"""

import pytest
import json
from unittest.mock import Mock, patch
from src.schemas.post import Post, PostMetadata, PostEngagement, PostGenerationRequest
from src.utils.validators import (
    validate_post_text, 
    validate_hashtags, 
    calculate_post_quality_score,
    ValidationError
)


class TestPostModel:
    """Test cases for Post data model."""
    
    def test_post_creation(self):
        """Test basic post creation."""
        post = Post(
            id="test_001",
            text="This is a test post with some content."
        )
        
        assert post.id == "test_001"
        assert post.text == "This is a test post with some content."
        assert post.word_count > 0
        assert post.line_count > 0
    
    def test_post_with_metadata(self):
        """Test post creation with metadata."""
        metadata = PostMetadata(
            topic="AI & Tech",
            tone="professional",
            hashtags=["#AI", "#Tech"]
        )
        
        post = Post(
            id="test_002",
            text="AI is transforming the tech industry.",
            metadata=metadata
        )
        
        assert post.metadata.topic == "AI & Tech"
        assert post.metadata.tone == "professional"
        assert len(post.metadata.hashtags) == 2
    
    def test_post_length_category(self):
        """Test length category calculation."""
        short_post = Post(id="short", text="Short post.")
        medium_post = Post(id="medium", text="Line1\nLine2\nLine3\nLine4\nLine5")
        long_post = Post(id="long", text="Long post.\n" * 15)
        
        assert short_post.length_category == "Short"
        assert medium_post.length_category == "Medium"
        assert long_post.length_category == "Long"
    
    def test_post_engagement_properties(self):
        """Test engagement-related properties."""
        post = Post(
            id="test_003",
            text="This post has a question? And an exclamation!"
        )
        
        assert post.has_question is True
        assert post.has_exclamation is True
    
    def test_post_to_dict(self):
        """Test post serialization to dictionary."""
        post = Post(
            id="test_004",
            text="Test post content",
            metadata=PostMetadata(topic="Test")
        )
        
        post_dict = post.to_dict()
        
        assert post_dict["id"] == "test_004"
        assert post_dict["text"] == "Test post content"
        assert post_dict["metadata"]["topic"] == "Test"
    
    def test_post_from_dict(self):
        """Test post deserialization from dictionary."""
        post_data = {
            "id": "test_005",
            "text": "Test post from dict",
            "metadata": {
                "topic": "Test Topic",
                "hashtags": ["#Test"]
            },
            "engagement": {
                "likes": 10,
                "comments": 5,
                "shares": 2
            }
        }
        
        post = Post.from_dict(post_data)
        
        assert post.id == "test_005"
        assert post.text == "Test post from dict"
        assert post.metadata.topic == "Test Topic"
        assert post.engagement.likes == 10


class TestPostGenerationRequest:
    """Test cases for PostGenerationRequest validation."""
    
    def test_valid_request(self):
        """Test valid request creation."""
        request = PostGenerationRequest(
            length_category="Medium",
            language="English",
            tag="AI & Tech"
        )
        
        assert request.length_category == "Medium"
        assert request.language == "English"
        assert request.tag == "AI & Tech"
    
    def test_invalid_length_category(self):
        """Test invalid length category validation."""
        with pytest.raises(ValueError, match="Invalid length category"):
            PostGenerationRequest(
                length_category="ExtraLong",
                language="English",
                tag="Test"
            )
    
    def test_invalid_language(self):
        """Test invalid language validation."""
        with pytest.raises(ValueError, match="Invalid language"):
            PostGenerationRequest(
                length_category="Medium",
                language="Spanish",
                tag="Test"
            )
    
    def test_empty_tag(self):
        """Test empty tag validation."""
        with pytest.raises(ValueError, match="Tag cannot be empty"):
            PostGenerationRequest(
                length_category="Medium",
                language="English",
                tag=""
            )


class TestValidators:
    """Test cases for validation utilities."""
    
    def test_validate_post_text_valid(self):
        """Test valid post text validation."""
        valid_text = "This is a valid post with appropriate length and content."
        assert validate_post_text(valid_text) is True
    
    def test_validate_post_text_empty(self):
        """Test empty post text validation."""
        with pytest.raises(ValidationError, match="Post text cannot be empty"):
            validate_post_text("")
    
    def test_validate_post_text_too_short(self):
        """Test too short post text validation."""
        with pytest.raises(ValidationError, match="Post text must be at least 10 characters"):
            validate_post_text("Short")
    
    def test_validate_post_text_too_long(self):
        """Test too long post text validation."""
        long_text = "A" * 3001
        with pytest.raises(ValidationError, match="Post text cannot exceed 3000 characters"):
            validate_post_text(long_text)
    
    def test_validate_hashtags_valid(self):
        """Test valid hashtags validation."""
        valid_hashtags = ["#AI", "#Tech", "#Innovation"]
        assert validate_hashtags(valid_hashtags) is True
    
    def test_validate_hashtags_invalid_format(self):
        """Test invalid hashtag format validation."""
        invalid_hashtags = ["AI", "#", "#A"]
        with pytest.raises(ValidationError, match="must start with #"):
            validate_hashtags(invalid_hashtags)
    
    def test_calculate_post_quality_score(self):
        """Test post quality score calculation."""
        post = Post(
            id="quality_test",
            text="This is a quality post with a question? And some hashtags #AI #Tech!",
            metadata=PostMetadata(hashtags=["#AI", "#Tech"])
        )
        
        score = calculate_post_quality_score(post)
        
        assert 0 <= score <= 10
        assert score > 0  # Should have some positive score for this post


class TestIntegration:
    """Integration test cases."""
    
    @patch('src.services.llm_service.get_groq_client')
    def test_post_generation_integration(self, mock_llm):
        """Test post generation with mocked LLM."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "This is a generated LinkedIn post about AI and technology."
        mock_llm.return_value.invoke.return_value = mock_response
        
        # This would test the actual post generation function
        # For now, we'll just verify the mock is set up correctly
        assert mock_llm.called is False


if __name__ == "__main__":
    pytest.main([__file__]) 