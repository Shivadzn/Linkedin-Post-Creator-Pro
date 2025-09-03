# few_shot.py (Hypothetical/Recommended implementation)
import json
import os

class FewShotPosts:
    def __init__(self, data_path="data/processed_posts.json"):
        self.data_path = data_path
        self.posts = []
        self.categories = []
        self._load_data()

    def _load_data(self):
        """Loads the processed data from the specified JSON file."""
        if not os.path.exists(self.data_path):
            # If the file doesn't exist, raise an error or handle gracefully
            # For robustness, we'll initialize with empty lists and let the app.py handle the error/fallback
            print(f"Warning: Data file not found at {self.data_path}. Few-shot examples will be empty.")
            return

        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                loaded_json = json.load(f)

            # Check the structure of the loaded JSON
            if isinstance(loaded_json, list):
                # If it's a direct list of posts (from an earlier preprocess iteration)
                self.posts = loaded_json
                # No dataset_info or categories in this structure
                self.categories = []
            elif isinstance(loaded_json, dict) and 'posts' in loaded_json:
                # If it's the full structured dataset (from the latest preprocess iteration)
                self.posts = loaded_json['posts']
                self.categories = loaded_json.get('dataset_info', {}).get('categories', [])
            else:
                print(f"Warning: Unexpected data structure in {self.data_path}. Expected list or dict with 'posts'.")
                self.posts = []
                self.categories = []

            print(f"Successfully loaded {len(self.posts)} posts from {self.data_path}.")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {self.data_path}: {e}")
            self.posts = []
            self.categories = []
        except Exception as e:
            print(f"An unexpected error occurred while loading data: {e}")
            self.posts = []
            self.categories = []


    def get_tags(self):
        """
        Extracts all unique unified tags from the loaded posts and dataset categories.
        """
        all_tags = set(self.categories) # Start with categories from dataset_info

        for post in self.posts:
            if 'metadata' in post and 'unified_tags' in post['metadata']:
                for tag in post['metadata']['unified_tags']:
                    all_tags.add(tag)
        return sorted(list(all_tags))

    def get_filtered_posts(self, length_category, language, tag, max_examples=2):
        """
        Filters posts based on length, language, and unified tag for few-shot examples.
        """
        filtered = []
        for post in self.posts:
            meta = post.get('metadata', {})
            post_unified_tags = meta.get('unified_tags', [])
            post_language = meta.get('language', 'English') # Default to English

            # Check for tag match (case-insensitive for robustness)
            tag_matches = tag.lower() in [t.lower() for t in post_unified_tags]

            # Check for language match
            language_matches = post_language.lower() == language.lower()

            # Check for length category match (approximate line count)
            line_count = meta.get('line_count', 0)
            length_matches = False
            if length_category == "Short" and 1 <= line_count <= 5:
                length_matches = True
            elif length_category == "Medium" and 6 <= line_count <= 10:
                length_matches = True
            elif length_category == "Long" and 11 <= line_count <= 15:
                length_matches = True
            # Add logic for other length categories if you have them

            if tag_matches and language_matches and length_matches:
                filtered.append(post)
                if len(filtered) >= max_examples:
                    break # Stop if we have enough examples

        return filtered

# Example usage (for testing few_shot.py)
if __name__ == "__main__":
    # Create a dummy processed_posts.json for testing if it doesn't exist
    dummy_processed_data = {
        "dataset_info": {
            "categories": ["AI & Tech", "Startup", "Career"]
        },
        "posts": [
            {
                "id": "p1",
                "text": "This is a short AI post. #AI",
                "metadata": {"line_count": 3, "language": "English", "unified_tags": ["AI & Tech"]}
            },
            {
                "id": "p2",
                "text": "This is a medium Startup post. #startup",
                "metadata": {"line_count": 7, "language": "English", "unified_tags": ["Startup"]}
            },
            {
                "id": "p3",
                "text": "This is another short AI post. AI is great.",
                "metadata": {"line_count": 4, "language": "English", "unified_tags": ["AI & Tech"]}
            },
            {
                "id": "p4",
                "text": "This is a long career development post.\nIt has multiple lines and advice.",
                "metadata": {"line_count": 12, "language": "English", "unified_tags": ["Career"]}
            }
        ]
    }
    dummy_file_path = "data/processed_posts.json"
    os.makedirs("data", exist_ok=True)
    with open(dummy_file_path, "w", encoding="utf-8") as f:
        json.dump(dummy_processed_data, f, indent=4)
    print(f"Dummy processed_posts.json created at {dummy_file_path}")

    fs = FewShotPosts()
    print("\nAll Tags:", fs.get_tags())
    print("\nFiltered for Short, English, AI & Tech:", fs.get_filtered_posts("Short", "English", "AI & Tech"))
    print("\nFiltered for Medium, English, Startup:", fs.get_filtered_posts("Medium", "English", "Startup"))
    print("\nFiltered for Long, English, Career:", fs.get_filtered_posts("Long", "English", "Career"))