import json
import re
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.services.llm_service import get_groq_client
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import time # Import time for adding a delay

def extract_json_from_text(text):
    """
    Extracts the first JSON object from a given text.
    """
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return match.group(0)
    return text  # fallback: return as is

def process_posts(raw_file_path, processed_file_path=None):
    """
    Processes LinkedIn posts by leveraging pre-existing metadata from the corrected dataset.
    It retains all original data and adds refined/calculated fields.
    Assumes raw_file_path contains a direct list of post objects.
    """
    with open(raw_file_path, encoding='utf-8') as file:
        # Load the content. If it's a list directly, `data` will be that list.
        # If it's a dictionary with a 'posts' key, we will adjust the code below.
        data = json.load(file)

    # --- IMPORTANT ADJUSTMENT HERE ---
    # Check if 'data' is a list of posts or a dictionary containing 'posts'
    if isinstance(data, list):
        original_posts = data # `data` is already the list of posts
        dataset_info_categories = [] # No dataset_info, so no categories from there
        print("Raw JSON detected as a direct list of posts.")
    elif isinstance(data, dict) and 'posts' in data:
        original_posts = data['posts']
        dataset_info_categories = data.get('dataset_info', {}).get('categories', [])
        print("Raw JSON detected as a dictionary with a 'posts' key.")
    else:
        raise ValueError("Unsupported raw_post.json structure. Expected a list of posts or a dictionary with a 'posts' key.")

    enriched_posts = []

    # Collect all unique topics and hashtags to unify them across the entire dataset
    all_unique_tags_for_unification = set()
    all_unique_tags_for_unification.update(dataset_info_categories) # Add categories if available

    for post in original_posts:
        if 'metadata' in post and 'topic' in post['metadata']:
            all_unique_tags_for_unification.add(post['metadata']['topic'].strip().title()) # Add topic
        if 'metadata' in post and 'hashtags' in post['metadata']:
            for ht in post['metadata']['hashtags']:
                all_unique_tags_for_unification.add(ht.replace('#', '').strip().title()) # Add cleaned hashtags

    # Only call LLM if there are tags to unify
    unified_tags_mapping = {}
    if all_unique_tags_for_unification:
        print(f"Calling LLM for tag unification mapping for {len(all_unique_tags_for_unification)} unique tags...")
        unified_tags_mapping = get_unified_tags(list(all_unique_tags_for_unification))
        print("LLM tag unification mapping received.")
        time.sleep(1) # Small delay after LLM call
    else:
        print("No unique tags found for unification. Skipping LLM call.")


    for post in original_posts:
        # Start with a copy of the original post to retain all existing fields
        current_post = post.copy()

        # Ensure 'metadata' exists, if not, initialize it
        if 'metadata' not in current_post:
            current_post['metadata'] = {}

        # Calculate line_count and add to metadata
        current_post['metadata']['line_count'] = len(current_post['text'].split('\n'))

        # Hardcode language as 'English' based on your dataset's content
        # (This is more reliable than LLM inference for your specific dataset)
        current_post['metadata']['language'] = "English"

        # Process and apply unified tags
        post_specific_tags_to_unify = set()
        if 'topic' in current_post['metadata']:
            post_specific_tags_to_unify.add(current_post['metadata']['topic'].strip().title())
        if 'hashtags' in current_post['metadata']:
            for ht in current_post['metadata']['hashtags']:
                post_specific_tags_to_unify.add(ht.replace('#', '').strip().title())

        processed_tags_for_post = []
        for tag in post_specific_tags_to_unify:
            # Apply the unified mapping, or keep original if no mapping exists
            unified_version = unified_tags_mapping.get(tag, tag)
            processed_tags_for_post.append(unified_version)

        # Remove duplicates and store as a new 'unified_tags' field in metadata
        current_post['metadata']['unified_tags'] = list(dict.fromkeys(processed_tags_for_post))

        # Add default engagement fields if they don't exist
        # This will only add if the key 'engagement' is NOT at the top level of the post
        if 'engagement' not in current_post:
            current_post['engagement'] = {"likes": 0, "comments": 0, "shares": 0}

        enriched_posts.append(current_post)

    # --- IMPORTANT ADJUSTMENT HERE FOR OUTPUT STRUCTURE ---
    # Reassemble the full data structure for output.
    # If original input was a list, output a list.
    # If original input was a dictionary with 'posts', output that dictionary structure.
    if isinstance(data, list):
        output_data = enriched_posts # Output is just the list of processed posts
    else: # It was a dictionary with 'posts', 'dataset_info', 'training_labels'
        output_data = data.copy() # Start with a copy of the original structure
        output_data['posts'] = enriched_posts # Replace with enriched posts
        # If dataset_info or training_labels were missing, they remain missing.
        # This preserves the original top-level structure.


    if processed_file_path:
        with open(processed_file_path, mode="w", encoding='utf-8') as outfile:
            json.dump(output_data, outfile, indent=4)
        print(f"Processed data saved to {processed_file_path}")
    else:
        print(json.dumps(output_data, indent=4))

# extract_metadata is not called by process_posts directly for this dataset,
# but remains for other potential uses.
def extract_metadata(post_text):
    """
    Extracts metadata from a LinkedIn post using an LLM.
    This function is kept for backward compatibility but is no longer
    called by process_posts for the provided dataset.
    """
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble.
    2. JSON object should have exactly three keys: line_count, language and tags.
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)

    Here is the actual post on which you need to perform this task:
    {post_text}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | get_groq_client()
    response = chain.invoke(input={"post_text": post_text})

    try:
        json_parser = JsonOutputParser()
        try:
            res = json_parser.parse(response.content)
        except OutputParserException:
            json_str = extract_json_from_text(response.content)
            res = json.loads(json_str)
    except Exception as e:
        print(f"Failed to parse metadata: {e}")
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res

def get_unified_tags(tags_list_or_set):
    """
    Unifies tags using an LLM. This function is retained as tag unification
    can be a complex task that benefits from LLM intelligence, especially
    if new tags appear. It now takes a list/set of unique tags or categories.
    """
    # Ensure input is a string for the prompt
    unique_tags_str = ','.join(sorted(list(set(tags_list_or_set))))

    template = '''I will give you a list of tags. You need to unify tags with the following requirements:
    1. Tags should be unified and merged to create a shorter list.
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search".
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
       Example 5: "AI/Tech" should be mapped to "AI & Tech" or "AI/Tech" if that is the preferred term.
       Example 6: "Startup" should be mapped to "Startup".
       Example 7: "Career" should be mapped to "Career".
       Example 8: "Personal Story" should be mapped to "Personal Story".
       Example 9: "Industry Insights" should be mapped to "Industry Insights".
       Example 10: "Leadership" should be mapped to "Leadership".
       Example 11: "Productivity" should be mapped to "Productivity".
       Example 12: "Marketing" should be mapped to "Marketing".
       Example 13: "YCombinator" should be mapped to "Startup".
       Example 14: "Startup Ecosystem" should be mapped to "Startup".
       Example 15: "DataMonetization" should be mapped to "Data Monetization".
       Example 16: "ContentCreation" should be mapped to "Content Creation".
       Example 17: "TechStrategy" should be mapped to "Tech Strategy".
       Example 18: "TalentRetention" should be mapped to "Talent Retention".
       Example 19: "FutureOfWork" should be mapped to "Future Of Work".
       Example 20: "WorkCulture" should be mapped to "Work Culture".
       Example 21: "Management" should be mapped to "Leadership".
       Example 22: "ProfessionalDevelopment" should be mapped to "Career Growth".
       Example 23: "WorkLifeBalance" should be mapped to "Work-Life Balance".
       Example 24: "Mindfulness" should be mapped to "Productivity".
       Example 25: "CareerDecisions" should be mapped to "Career".
       Example 26: "Values" should be mapped to "Personal Growth".
       Example 27: "ContentStrategy" should be mapped to "Marketing".
       Example 28: "PersonalBranding" should be mapped to "Career Growth".
       Example 29: "RelationshipBuilding" should be mapped to "Networking".
       Example 30: "TimeManagement" should be mapped to "Productivity".
       Example 31: "EnergyManagement" should be mapped to "Productivity".
       Example 32: "FailureToSuccess" should be mapped to "Personal Growth".
       Example 33: "Resilience" should be mapped to "Personal Growth".


    2. Each tag should follow title case convention. For example: "Motivation", "Job Search".
    3. Output should be a JSON object, with no preamble.
    4. The output JSON should have a mapping of original tag and the unified tag.
       For example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search", "Motivation": "Motivation"}}

    Here is the list of tags:
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | get_groq_client()
    try:
        response = chain.invoke(input={"tags": unique_tags_str})
        json_parser = JsonOutputParser()
        try:
            res = json_parser.parse(response.content)
        except OutputParserException:
            json_str = extract_json_from_text(response.content)
            res = json.loads(json_str)
        return res
    except Exception as e:
        print(f"Failed to parse unified tags from LLM: {e}. Returning fallback mapping.")
        # Fallback: create a mapping where each tag maps to itself, but title-cased
        return {tag: tag.title() for tag in tags_list_or_set}

if __name__ == "__main__":
    # This block is for ensuring a raw_post.json exists for testing.
    # In a real scenario, ensure your full corrected dataset is saved at this path.
    import os
    if not os.path.exists("data/raw_post.json"):
        os.makedirs("data", exist_ok=True)
        # Using a snippet of your full corrected data for the dummy file
        dummy_data_list_format = [
            {
               "id": "post_001",
               "text": "Zuck is not playing around anymore.\n\nAt first, Meta tried to block the wins of OpenAI, Apple, and Google by going open-source with models like LLaMA trying to shape the game by being the open alternative.\n\nBut now, it's clear: Zuck knows that if Meta has to lead in the AI race, just shipping open-source models won't cut it.\n\nThey're losing the edge in product quality. LLaMA, Instagram's AI features, anything Meta's shipped, it's nowhere close to GPT, Claude, or even Perplexity.\n\nWhat does Zuck do next?\n\nHe does what he's always done: hires.\n\nBrings in ex-OpenAI engineers. Builds a Superintelligence team.\n\nAnd yes, he's going all-in.\n\nMeanwhile, Apple's reportedly in talks to buy Perplexity.\n\nThis isn't just OpenAI vs Google anymore.\n\nIt's Apple vs Meta again. The same battle, a new arena.\n\nHonestly, watching Zuck's evolution over the last few years from the metaverse rabbit hole to now being super calculated and public-facing in AI is fascinating. He's grown. He's adapting.\n\nThis AI race isn't just about models anymore. It's about:\n\n-Teams.\n\n-Distribution.\n\n-Interfaces.\n\nAnd most interestingly, who builds the first AI-first social platform.\n\nI do believe one will exist.\n\nI don't know what it will look like yet because if I did, I'd be building it already.\n\nBut I'll be watching. And if I get any signal, I'm jumping in.\n\nLet the game begin. 🧠🔥",
               "metadata": {
                 "topic": "AI/Tech",
                 "tone": "analytical",
                 "post_type": "industry_insight",
                 "word_count": 267,
                 "estimated_engagement": "high",
                 "target_audience": "Tech professionals, entrepreneurs, AI enthusiasts",
                 "best_posting_time": "Tuesday 9-11 AM",
                 "hashtags": ["#AI", "#Meta", "#TechStrategy"],
                 "structure": "hook → analysis",
                 "engagement_drivers": ["controversial_take"],
                 "quality_score": 8.5,
                 "virality_potential": "high",
                 "emotional_tone": "excitement",
                 "call_to_action": "implicit_engagement"
               }
            },
            {
               "id": "post_002",
               "text": "AI companies scraped the internet for free. Cloudflare just dropped the invoice.\n\nEvery crawl. Every request. Every byte of data now has a price.\n\nCloudflare just announced that AI bots will now be blocked by default, unless they pay to crawl.\n\nThis is huge.\n\nUntil now, AI companies scraped the open web like a buffet training models on everyone's work without permission or pay.\n\nBut that era is ending.\n\nWith 'Pay Per Crawl,' Cloudflare is shifting the power back to content owners.\n\nNow, websites can charge AI companies like OpenAI, Google, Meta, and others every time they crawl their data.\n\nThis is the beginning of the monetization layer for the knowledge web.\n\nWe're entering a new phase of the internet:\n\nFrom 'open by default' to 'licensed by default'\n\nFrom 'scrape now, ask later' to 'pay to play'\n\nFrom 'free training data' to 'premium AI fuel'\n\nWhy this matters??\nWhether you're a solo creator, a startup, or a media giant your data has value in this AI-driven world.\n\nAnd this move from Cloudflare could be the first domino in a wave of content compensation systems.\n\nAs AI becomes the UI of the internet, the fight over who owns and monetizes data will define the next decade.\n\nSmart founders and operators will:\n\n- Build with content licensing in mind\n\n- Rethink data strategy and defensibility\n\n- Anticipate a world where every digital action has a cost (and revenue)\n\nThe web just got more expensive and maybe, more fair.",
               "metadata": {
                 "topic": "AI/Tech",
                 "tone": "analytical",
                 "post_type": "industry_insight",
                 "word_count": 285,
                 "estimated_engagement": "high",
                 "target_audience": "Tech entrepreneurs, content creators, business leaders",
                 "best_posting_time": "Wednesday 10 AM - 12 PM",
                 "hashtags": ["#AI", "#DataMonetization", "#ContentCreation"],
                 "structure": "breaking_news",
                 "engagement_drivers": ["breaking_news"],
                 "quality_score": 9.0,
                 "virality_potential": "high",
                 "emotional_tone": "informative",
                 "call_to_action": "implicit_strategy"
               }
            },
            {
                "id": "post_005",
                "text": "This was us at AIC-GIM Foundation in early 2024, thinking of applying for the YC summer batch; what followed is surely a story.\n\nBack then, we were in our final year of college, exactly before the YC deadlines, when we had exams, submissions, and a lot of things going on simultaneously.\n\nFast forward to August, by the time we were done with the exam, it was too late, so we did a trip to Bangalore with a friend and mentor to get the understanding. That was my 1st time experiencing that city, and yes, it was amazing.\n\nWhen I was back in Goa, I was super pumped, energised, and was with full hunger to kill it, focused next 2 months building a significantly good product.\n\nGuess what? it had a lot of go-to-market issues, spent the next 4-5 months in self-doubt, understanding what else to build, and still trying to make it work.\n\nNow, cut to April 2025, we have little light of hope. We saw potential with the problem to solve, but the solution we had built back then was still a major issue, so we thought to change the way we solved this.\n\nBy May end, we had a network of 50000+ creators across India, with interest from a few brands to test and use it.\n\nYes, it felt like a win, and I wanted to tell everyone that I am the next big thing that has happened to the startup ecosystem.\n\nBut that's exactly not where the story ends with a happy ending. What happens next is a good question to have, and you will have the answer to it in my next post. Till then, keep building, keep doing crazy stuff",
                "metadata": {
                    "topic": "Startup",
                    "tone": "storytelling",
                    "post_type": "personal_story",
                    "word_count": 298,
                    "estimated_engagement": "medium",
                    "target_audience": "Startup founders, college students, entrepreneurs",
                    "best_posting_time": "Monday 8-10 AM",
                    "hashtags": ["#StartupJourney", "#YCombinator", "#Entrepreneurship"],
                    "structure": "context",
                    "engagement_drivers": ["personal_journey"],
                    "quality_score": 7.2,
                    "virality_potential": "medium",
                    "emotional_tone": "reflective",
                    "call_to_action": "explicit_followup"
                }
            }
        ]
        with open("data/raw_post.json", "w", encoding='utf-8') as f:
            json.dump(dummy_data_list_format, f, indent=4)
        print("Dummy data created at data/raw_post.json. Please replace it with your full corrected dataset.")

    process_posts("data/raw_post.json", "data/processed_posts.json")