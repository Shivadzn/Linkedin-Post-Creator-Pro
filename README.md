# LinkedIn Post Generator 🚀

An AI-powered LinkedIn post generator that creates engaging, professional content using few-shot learning and advanced language models.

## ✨ Features

- **AI-Powered Generation**: Uses Groq's LLM for high-quality post creation
- **Few-Shot Learning**: Learns from existing posts to match your style
- **Customizable Parameters**: Choose length, language, and topics
- **Web Interface**: Beautiful Streamlit UI for easy interaction
- **Smart Preprocessing**: Automatic metadata extraction and tag unification
- **Quality Assurance**: Built-in validation and quality checks

## 🎥 Demo

Watch a quick demo:

[![Watch the demo on YouTube](https://i.ytimg.com/an_webp/WjqpQQlDJ3M/mqdefault_6s.webp?du=3000&sqp=COzf4cUG&rs=AOn4CLCyzglAcJbSbLf1GBcC3at2JhJGDA)](https://youtu.be/WjqpQQlDJ3M)

## 🏗️ Architecture

```
linkedin_post_generator/
├── src/
│   ├── main.py              # Streamlit web interface
│   ├── post_generator.py    # Core post generation logic
│   ├── few_shot.py          # Few-shot learning implementation
│   ├── preprocess.py        # Data preprocessing pipeline
│   └── llm_helper.py        # LLM client configuration
├── data/
│   ├── raw_post.json        # Raw LinkedIn posts data
│   └── processed_posts.json # Processed and enriched data
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <https://github.com/Shivadzn/Linkedin-Post-Creator-Pro.git>
   cd linkedin_post_generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GROQ_API_KEY=your_api_key_here" > .env
   ```

5. **Preprocess your data**
   ```bash
   python src/preprocess.py
   ```

6. **Run the application**
   ```bash
   streamlit run src/main.py
   ```

## 📖 Usage

### Web Interface

1. Open your browser to `http://localhost:8501`
2. Select your desired topic, length, and language
3. Click "Generate My Post!"
4. Copy the generated post and use it on LinkedIn

### Programmatic Usage

```python
from src.post_generator import generate_post

# Generate a post
post = generate_post(
    length_category="Medium",
    language="English", 
    tag="AI & Tech"
)
print(post)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |
| `GROQ_MODEL` | LLM model to use | No (default: llama3-8b-8192) |

### Data Format

The system expects LinkedIn posts in the following JSON format:

```json
{
  "dataset_info": {
    "name": "LinkedIn Posts Training Dataset",
    "categories": ["AI/Tech", "Startup", "Career"]
  },
  "posts": [
    {
      "id": "post_001",
      "text": "Your post content here...",
      "metadata": {
        "topic": "AI/Tech",
        "hashtags": ["#AI", "#Tech"],
        "tone": "professional"
      }
    }
  ]
}
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📊 Data Processing Pipeline

1. **Raw Data Loading**: Loads LinkedIn posts from JSON
2. **Metadata Extraction**: Extracts topics, hashtags, and engagement metrics
3. **Tag Unification**: Uses LLM to standardize and unify tags
4. **Quality Enhancement**: Adds line counts, language detection, and engagement fields
5. **Few-Shot Preparation**: Prepares data for few-shot learning

## 🎯 Quality Features

- **Input Validation**: Validates all user inputs
- **Error Handling**: Graceful error handling with user-friendly messages
- **Quality Scoring**: Automatic post quality assessment
- **Rate Limiting**: Prevents API abuse
- **Caching**: Improves performance with response caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

- [ ] Advanced post templates
- [ ] Multi-language support
- [ ] Post scheduling integration
- [ ] Analytics dashboard
- [ ] A/B testing capabilities
- [ ] Team collaboration features


**Made with ❤️ for LinkedIn professionals** 
