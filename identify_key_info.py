# idenfity_key_info.py

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
import os
import json
import nltk
from openai import OpenAI
from dotenv import load_dotenv
# from pytube import YouTube

# Load environment variables from .env file
load_dotenv()

def get_video_id(url):
    """
    Extracts the video ID from various YouTube URL formats.
    """
    match = re.search(r"watch\?v=([^&]+)", url)
    if match:
        return match.group(1)
    
    match = re.search(r"youtu\.be/([^?]+)", url)
    if match:
        return match.group(1)
        
    match = re.search(r"shorts/([^?]+)", url)
    if match:
        return match.group(1)

    return None

def get_youtube_transcript(video_url: str) -> str:
    """
    Retrieves the full transcript for a given YouTube video URL using the
    instance-based .fetch() method for maximum compatibility.
    Returns the transcript as a string, or an error message starting with "Error:".
    """
    video_id = get_video_id(video_url)
    
    if not video_id:
        return "Error: Could not extract a valid video ID from the URL."

    try:
        # Use the instance-based method that we confirmed works.
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id, languages=['en'])
        
        # .fetch() returns a list of objects, so we access the text via the .text attribute.
        full_transcript = " ".join([snippet.text for snippet in transcript_list])
        
        # Replace newlines and excessive whitespace for cleaner processing by the LLM
        full_transcript = full_transcript.replace('\n', ' ').replace('  ', ' ')
        
        return full_transcript
        
    except TranscriptsDisabled:
        return f"Error: Transcripts are disabled for the video (ID: {video_id})."
    except NoTranscriptFound:
        return f"Error: No English transcript could be found for the video (ID: {video_id})."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

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

def determine_sentence_count(total_sentences: int) -> int:
    """
    Dynamically determines the number of key sentences to extract based on the
    total length of the transcript.

    Args:
        total_sentences: The total number of sentences in the text.

    Returns:
        The ideal number of sentences for the summary.
    """
    # --- Tunable Parameters ---
    MIN_SENTENCES = 7      # The absolute minimum sentences for any summary.
    MAX_SENTENCES = 40     # The absolute maximum sentences for any summary.
    RATIO = 0.15           # We'll aim for about 15% of the total sentences.

    # Calculate the proportional count
    proportional_count = int(total_sentences * RATIO)
    
    # Enforce the min and max caps
    final_count = max(MIN_SENTENCES, min(proportional_count, MAX_SENTENCES))
    
    return final_count

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

def generate_abstractive_summary(
    key_sentences: list[str],
    client: OpenAI,
    model: str = "gpt-4.1-nano"
) -> str:
    """
    Generates a final, abstractive summary from a list of key sentences,
    ensuring every new sentence includes citations to the original source sentences.

    Args:
        key_sentences: A list of the key sentences, formatted with their IDs.
        client: An initialized OpenAI client.
        model: The OpenAI model to use.

    Returns:
        A string containing the final, cited summary, or an empty string on error.
    """
    # Join the list of key sentences into a single block of text for the prompt
    key_sentences_text = "\n".join(key_sentences)

    prompt = f"""
    You are a skilled writer and editor. Your task is to synthesize the following collection of key transcribed sentences from a video into a smooth, easy-to-read summary paragraph.

    **CRITICAL INSTRUCTIONS:**
    1.  You MUST base your summary ONLY on the information provided in the "Key Sentences to Rewrite" below. Do not add any outside knowledge or information.
    2.  At the end of EACH new sentence you write in your summary, you MUST cite the original sentence number(s) it is based on, like `[S1]` or `[S5, S12]`.
    3.  Every claim in your summary must be traceable to one or more of the provided sentences.
    4.  Combine related ideas into cohesive sentences to ensure the summary flows naturally.

    **Key Sentences to Rewrite:**
    ---
    {key_sentences_text}
    ---

    **Final Summary:**
    """

    try:
        print(f"\nSending request to '{model}' to generate the final abstractive summary...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a skilled writer who follows citation rules perfectly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5 # A little creativity is good for writing style, but not too much
        )
        
        summary = response.choices[0].message.content
        print("Successfully received summary from API.")
        return summary.strip()

    except Exception as e:
        print(f"An unexpected error occurred during final summary generation: {e}")
        return ""

def sanitize_filename(title: str) -> str:
    """
    Cleans a string to be a valid filename.
    - Removes illegal characters
    - Replaces spaces with underscores
    - Truncates to a reasonable length
    """
    # Remove characters that are illegal in most file systems
    sanitized = re.sub(r'[\\/*?:"<>|]', "", title)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Truncate the filename to avoid issues with path length limits
    return sanitized[:100] # Keep the first 100 characters

if __name__ == "__main__":
    # --- 1. Setup ---
    download_nltk_data_if_needed()
    
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print("Error: Failed to initialize OpenAI client. Is your OPENAI_API_KEY environment variable set?")
        exit()

    # Define the output directory
    OUTPUT_DIR = "summaries"
    # Create the output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- 2. Input from YouTube ---
    youtube_url = input("Please enter the YouTube URL: ")
    print(f"--- Step 1: Fetching Transcript from YouTube URL ---")
    # print(f"URL: {youtube_url}")
    
    # Fetch the video title using pytube
    # try:
    #     yt = YouTube(youtube_url)
    #     video_title = yt.title
    #     print(f"Successfully fetched video title: \"{video_title}\"")
    # except Exception as e:
    #     print(f"Warning: Could not fetch video title: {e}. Using video ID as a fallback.")
    #     video_title = "" # Fallback to an empty title
    
    long_text = get_youtube_transcript(youtube_url)
    
    # Check if the transcript fetcher returned an error
    if long_text.startswith("Error:"):
        print(long_text)
        exit() # Stop the script if we can't get the transcript
        
    print(f"Successfully fetched transcript ({len(long_text)} characters).")

    # --- 3. Pre-process the fetched text ---
    print("\n--- Step 2: Pre-processing Text ---")
    sentences_map, formatted_prompt_text = preprocess_text_to_numbered_sentences(long_text)
    total_sentence_count = len(sentences_map) # Get the total number of sentences
    print(f"Successfully split text into {len(sentences_map)} sentences.")
    
    # --- 4. Dynamically Determine the Count ---  <- NEW STEP
    dynamic_count = determine_sentence_count(total_sentence_count)
    print(f"Dynamically determined summary sentence count: {dynamic_count}")
    
    # --- 5. Identify Key Sentences using LLM ---
    print("\n--- Step 3: Extracting Key Sentence IDs with OpenAI ---")
    key_sentence_ids = extract_key_sentence_ids(formatted_prompt_text, client, sentence_count=dynamic_count)

    if not key_sentence_ids:
        print("\nCould not extract key sentences. Exiting.")
    else:
        print(f"\nIdentified {len(key_sentence_ids)} key sentence IDs: {key_sentence_ids}")
        
        # --- 6. Verification Step (Crucial for the workflow) ---
        print("\n--- Step 4: Verifying and Displaying Key Sentences ---")
        
        # Generate a unique filename for the output file
        video_id = get_video_id(youtube_url)
        output_filename = os.path.join(OUTPUT_DIR, f"{video_id}.md")
        # if video_title:
        #     sanitized_title = sanitize_filename(video_title)
        #     output_filename = f"{sanitized_title}.md"
        # else:
        #     # Fallback to just the ID if the title could not be fetched
        #     output_filename = f"error_no_title.md"

        # Prepare the content for the Markdown file
        markdown_content = []
        markdown_content.append(f"# Extractive Summary for YouTube Video\n")
        markdown_content.append(f"**Source URL:** {youtube_url}\n")
        markdown_content.append("---")
        markdown_content.append("\nBelow are the most important sentences identified from the transcript. These sentences form the basis for the final abstractive summary.\n")

        key_sentences_to_summarize = []
        for sentence_id in key_sentence_ids:
            if sentence_id in sentences_map:
                sentence_text = sentences_map[sentence_id]
                # Format as a Markdown list item with the ID bolded
                markdown_content.append(f"* **`{sentence_id}`**: {sentence_text}")
                key_sentences_to_summarize.append(f"[{sentence_id}] {sentence_text}")
            else:
                # Still print warnings to the terminal if an ID is invalid
                print(f"  - Warning: Received an invalid sentence ID from the API: {sentence_id}")
        
        # Join all the parts into a single string
        final_markdown = "\n".join(markdown_content)

        # Save the formatted content to the Markdown file
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
            print(f"\n✅ Extractive summary successfully saved to: '{output_filename}'")
        except IOError as e:
            print(f"\n❌ Error saving file: {e}")

        # --- Step 5: Generate and Append Final Abstractive Summary ---
        print("\n--- Step 5: Generating and Appending Final Abstractive Summary ---")
        
        final_summary = generate_abstractive_summary(key_sentences_to_summarize, client)
        
        if final_summary:
            # Append the final summary to the SAME file
            try:
                with open(output_filename, 'a', encoding='utf-8') as f:
                    f.write("\n\n---\n")
                    f.write("## Part 2: Final Summary (Abstractive with Citations)\n")
                    f.write(final_summary)
                print(f"✅ Abstractive summary successfully appended to: '{output_filename}'")
            except IOError as e:
                print(f"\n❌ Error appending final summary to file: {e}")
        else:
            print("\nCould not generate the final abstractive summary.")