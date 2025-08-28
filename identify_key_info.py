# idenfity_key_info.py

import os
import json
import nltk
from openai import OpenAI
from transcript_fetcher import get_youtube_transcript # <-- IMPORT THE FUNCTION
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def download_nltk_data_if_needed():
    """
    Checks if the NLTK tokenizer and its dependencies are available.
    If not, it explicitly downloads both required packages.
    """
    try:
        nltk.sent_tokenize("This is a test sentence.")
    except LookupError:
        print("NLTK 'punkt' tokenizer or its dependencies not found. Explicitly downloading packages...")
        nltk.download('punkt')
        nltk.download('punkt_tab')
        print("Download complete.")

def preprocess_text_to_numbered_sentences(raw_text: str) -> tuple[dict[str, str], str]:
    """
    Splits text into sentences, assigns a unique ID to each, and returns
    both a lookup map and a formatted string for the prompt.
    """
    sentences = nltk.sent_tokenize(raw_text)
    
    numbered_sentences_map = {}
    formatted_text_lines = []
    
    for i, sentence in enumerate(sentences):
        sentence_id = f"S{i+1}"
        numbered_sentences_map[sentence_id] = sentence
        formatted_text_lines.append(f"[{sentence_id}] {sentence}")
        
    return numbered_sentences_map, "\n".join(formatted_text_lines)

def extract_key_sentence_ids(
    formatted_text: str,
    client: OpenAI,
    model: str = "gpt-4.1-nano",
    sentence_count: int = 10
) -> list[str]:
    """
    Uses an LLM to identify the most important sentences from a pre-numbered text.
    """
    prompt = f"""
    You are a highly skilled research assistant. Your task is to analyze the following text from a video transcript and identify the most important sentences that are critical for understanding the main points and arguments.

    **Instructions:**
    1.  Read the entire text carefully.
    2.  Identify approximately {sentence_count} sentences that best summarize the core information.
    3.  Do NOT summarize, rephrase, or explain. Your ONLY output must be a single, valid JSON object.
    4.  The JSON object must have a single key named "key_sentence_ids" which contains an array of the sentence IDs you have chosen.

    **Example Output Format:**
    {{
      "key_sentence_ids": ["S5", "S12", "S25", "S45", "S60"]
    }}

    **Numbered Text to Analyze:**
    ---
    {formatted_text}
    ---
    """

    try:
        print(f"\nSending request to '{model}' to identify key sentences...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful research assistant that outputs only JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        response_content = response.choices[0].message.content
        print("Successfully received response from API.")

        data = json.loads(response_content)
        key_ids = data.get("key_sentence_ids", [])
        
        if not isinstance(key_ids, list):
            raise ValueError("The 'key_sentence_ids' key in the JSON response is not a list.")

        return key_ids

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the API response.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

if __name__ == "__main__":
    # --- 1. Setup ---
    download_nltk_data_if_needed()
    
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print("Error: Failed to initialize OpenAI client. Is your OPENAI_API_KEY environment variable set?")
        exit()

    # --- 2. Input from YouTube ---
    youtube_url = "https://www.youtube.com/watch?v=t-53fouKqWI"
    print(f"--- Step 1: Fetching Transcript from YouTube URL ---")
    print(f"URL: {youtube_url}")
    
    long_text = get_youtube_transcript(youtube_url)
    
    # Check if the transcript fetcher returned an error
    if long_text.startswith("Error:"):
        print(long_text)
        exit() # Stop the script if we can't get the transcript
        
    print(f"Successfully fetched transcript ({len(long_text)} characters).")

    # --- 3. Pre-process the fetched text ---
    print("\n--- Step 2: Pre-processing Text ---")
    sentences_map, formatted_prompt_text = preprocess_text_to_numbered_sentences(long_text)
    print(f"Successfully split text into {len(sentences_map)} sentences.")
    
    # --- 4. Identify Key Sentences using LLM ---
    print("\n--- Step 3: Extracting Key Sentence IDs with OpenAI ---")
    key_sentence_ids = extract_key_sentence_ids(formatted_prompt_text, client, sentence_count=15) # Increased count for a long video
    
    if not key_sentence_ids:
        print("\nCould not extract key sentences. Exiting.")
    else:
        print(f"\nIdentified {len(key_sentence_ids)} key sentence IDs: {key_sentence_ids}")
        
        # --- 5. Verification Step (Crucial for the workflow) ---
        print("\n--- Step 4: Verifying and Displaying Key Sentences ---")
        print("This is the 'extractive' summary that will be used as the basis for the final step.")
        
        key_sentences_to_summarize = []
        for sentence_id in key_sentence_ids:
            if sentence_id in sentences_map:
                sentence_text = sentences_map[sentence_id]
                print(f"  - [{sentence_id}] {sentence_text}")
                key_sentences_to_summarize.append(f"[{sentence_id}] {sentence_text}")
            else:
                print(f"  - Warning: Received an invalid sentence ID from the API: {sentence_id}")

        print("\nThis workflow is now ready for the final 'Generate Abstractive Summary' step.")