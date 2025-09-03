from llm_helper import get_groq_client
from services.few_shot import FewShotPosts

# Initialize FewShotPosts. It should ideally load from your processed_posts.json
# or have access to the data that has been processed by your `preprocess.py` script.
few_shot = FewShotPosts()


def get_length_str(length_category):
    """
    Maps a length category string to a numerical line range.
    Uses 'line_count' from your processed data.
    """
    if length_category == "Short":
        return "1 to 5 lines"
    elif length_category == "Medium":
        return "6 to 10 lines"
    elif length_category == "Long":
        return "11 to 15 lines"
    else:
        # Fallback for unexpected length categories, or you can raise an error
        return "5 to 10 lines"


def generate_post(length_category: str, language: str, tag: str) -> str:
    """
    Generates a LinkedIn post based on specified length, language, and tag.

    Args:
        length_category (str): The desired length of the post (e.g., "Short", "Medium", "Long").
        language (str): The desired language of the post (e.g., "English", "Hinglish").
                        Note: For your current dataset, 'English' is more accurate.
        tag (str): The unified topic/tag for the post.

    Returns:
        str: The generated LinkedIn post content.
    """
    # Validate language input to ensure it matches our known data or LLM capabilities
    if language not in ["English", "Hinglish"]:
        print(f"Warning: '{language}' is not a recognized language. Defaulting to 'English'.")
        language = "English"

    prompt = get_prompt(length_category, language, tag)
    print("Generating post with the following prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)

    try:
        response = get_groq_client().invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error generating post: {e}")
        return "Sorry, I couldn't generate a post at this time. Please try again later."


def get_prompt(length_category: str, language: str, tag: str) -> str:
    """
    Constructs the prompt for the LLM based on generation parameters and few-shot examples.
    """
    length_instruction = get_length_str(length_category)

    # Base instruction for the LLM
    prompt_parts = [
        "Generate a LinkedIn post using the below information. Follow all instructions carefully. Do not include any preamble, conversational text, or extraneous information, just the post content.",
        f"1) Topic: The core subject of the post should be '{tag}'.",
        f"2) Length: The post should be approximately {length_instruction}."
    ]

    # Language instruction. Based on your dataset being primarily English.
    # If 'Hinglish' is truly desired for *future* examples, the few-shot examples
    # in FewShotPosts would need to reflect actual Hinglish content.
    if language == "Hinglish":
        # Clarify Hinglish means a mix, but the script is English.
        # This might be tricky for the LLM if it doesn't have Hinglish examples.
        prompt_parts.append("3) Language: The post should be in Hinglish (a mix of Hindi and English words), but the primary script used must be English characters.")
    else: # Default to English
        prompt_parts.append("3) Language: The post should be entirely in English.")

    # Fetch few-shot examples from the processed dataset
    # few_shot.get_filtered_posts should now use 'unified_tags' and 'language' from your processed data
    examples = few_shot.get_filtered_posts(
        length_category=length_category,
        language=language, # This should match the language field in your processed data ('English')
        tag=tag # This should match 'unified_tags' in your processed data
    )

    if len(examples) > 0:
        prompt_parts.append("\n4) Adopt the writing style, tone, and structure from the following examples. These examples are real LinkedIn posts related to the topic and length you requested.")
        for i, post in enumerate(examples):
            # Ensure post_text is taken from the 'text' key of the post object
            post_text = post.get('text', 'No text available.')
            prompt_parts.append(f'\n--- Example {i+1} ---\n{post_text}')

            if i >= 1: # Use max two samples
                break
    else:
        print(f"No few-shot examples found for Length: {length_category}, Language: {language}, Tag: {tag}. Post will be generated without specific style guidance.")
        # Add a note to the prompt if no examples are found
        prompt_parts.append("\n4) No specific examples were provided. Generate the post in a professional LinkedIn style.")


    # Combine all parts of the prompt
    final_prompt = "\n\n".join(prompt_parts)
    return final_prompt


if __name__ == "__main__":
    # Example usage:
    # Based on your dataset, 'English' is the accurate language.
    # 'AI & Tech' would be a unified tag that the LLM would have created.
    # 'Startup' is another unified tag.

    # Try generating a post for a "Medium" length, "English" language, and "AI & Tech" tag
    print("--- Generating an AI & Tech post (Medium, English) ---")
    generated_ai_post = generate_post("Medium", "English", "AI & Tech")
    print("\nGenerated AI & Tech Post:\n", generated_ai_post)
    print("\n" + "="*80 + "\n")

    # Try generating a post for a "Short" length, "English" language, and "Startup" tag
    print("--- Generating a Startup post (Short, English) ---")
    generated_startup_post = generate_post("Short", "English", "Startup")
    print("\nGenerated Startup Post:\n", generated_startup_post)
    print("\n" + "="*80 + "\n")

    # Example for Hinglish (if your FewShotPosts *actually* contains Hinglish examples)
    # If get_filtered_posts doesn't return Hinglish examples, the LLM might struggle.
    # print("--- Generating a Hinglish post (Long, Hinglish) ---")
    # generated_hinglish_post = generate_post("Long", "Hinglish", "Personal Story")
    # print("\nGenerated Hinglish Post:\n", generated_hinglish_post)
    # print("\n" + "="*80 + "\n")