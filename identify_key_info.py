import os
import json
import nltk
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def download_nltk_data_if_needed():
    """
    Checks if the NLTK tokenizer and its dependencies are available.
    If not, it explicitly downloads both required packages.
    """
    try:
        # Attempt to use the tokenizer to trigger a LookupError if anything is missing.
        nltk.sent_tokenize("This is a test sentence.")
    except LookupError:
        print("NLTK 'punkt' tokenizer or its dependencies not found. Explicitly downloading packages...")
        # The automatic download is failing to grab a dependency, so we download both parts manually.
        nltk.download('punkt')
        nltk.download('punkt_tab') # Explicitly download the missing dependency
        print("Download complete.")

def preprocess_text_to_numbered_sentences(raw_text: str) -> tuple[dict[str, str], str]:
    """
    Splits text into sentences, assigns a unique ID to each, and returns
    both a lookup map and a formatted string for the prompt.

    Args:
        raw_text: The original block of text.

    Returns:
        A tuple containing:
        - A dictionary mapping sentence IDs (e.g., "S1") to sentence text.
        - A single string with each sentence on a new line, prefixed by its ID.
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

    Args:
        formatted_text: The text with sentence IDs (e.g., "[S1] The cat sat.").
        client: An initialized OpenAI client.
        model: The OpenAI model to use.
        sentence_count: The approximate number of key sentences to extract.

    Returns:
        A list of key sentence IDs (e.g., ["S1", "S15", "S40"]).
    """
    prompt = f"""
    You are a highly skilled research assistant. Your task is to analyze the following text and identify the most important sentences that are critical for understanding the main points and arguments of the article.

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
            response_format={"type": "json_object"}, # Enable JSON Mode
            temperature=0.0 # Low temperature for deterministic, factual tasks
        )
        
        response_content = response.choices[0].message.content
        print("Successfully received response from API.")

        # Parse the JSON response
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
    
    # This will securely fetch the API key from your environment variables
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print("Error: Failed to initialize OpenAI client. Is your OPENAI_API_KEY environment variable set?")
        exit()

    # --- 2. Input Text ---
    # Using a snippet from your transcript for a realistic example
    long_text = """
    Okay, so in this video I want to go through Lang Extract, a new library that's come out of Google to help us basically do a lot of standard NLP tasks. So there are a whole bunch of standard NLP tasks that are not generative AI or not even generative uses of LLMs etc. I'm talking about simple things like text classification being able to do things like sentiment being able to say if a piece of text belongs to one class or one group as opposed to another. For a long time, a lot of these tasks were done with BERT models. So the BERT model came along at the end of 2018. The key thing here was that these BERT models were really good for fine-tuning for very specific NLP tasks. But then over the last say six months, I've started to see a whole new pattern emerge that a lot of big companies are just not using these models anymore because they're finding that they can just get the same results by wrapping the text in a prompt and then giving it to a GPT 40 Mini or a Gemini Flash or a model, something like that. Turns out this being much more efficient to actually use APIs and LLM as a service for doing these natural language processing tasks. And that's what brings us to Lang Extract. So Lang Extract is a library made by Google specifically to do these kinds of tasks with Gemini. The idea here is that it's not only going to give you those back, it's going to give you where they actually are in the text and allow you to run checks yourself to see that they're actually there.
    """

    # --- 3. Pre-process the text ---
    print("--- Step 1: Pre-processing Text ---")
    sentences_map, formatted_prompt_text = preprocess_text_to_numbered_sentences(long_text)
    print(f"Successfully split text into {len(sentences_map)} sentences.")
    # print("Formatted text for prompt:\n", formatted_prompt_text) # Uncomment to see the formatted text

    # --- 4. Identify Key Sentences using LLM ---
    print("\n--- Step 2: Extracting Key Sentence IDs with OpenAI ---")
    key_sentence_ids = extract_key_sentence_ids(formatted_prompt_text, client, sentence_count=5)
    
    if not key_sentence_ids:
        print("\nCould not extract key sentences. Exiting.")
    else:
        print(f"\nIdentified {len(key_sentence_ids)} key sentence IDs: {key_sentence_ids}")
        
        # --- 5. Verification Step (Crucial for the workflow) ---
        print("\n--- Step 3: Verifying and Displaying Key Sentences ---")
        print("This is the 'extractive' summary that will be used as the basis for the final step.")
        
        # This is the list of sentences you would pass to the final "generation" prompt
        key_sentences_to_summarize = []
        for sentence_id in key_sentence_ids:
            if sentence_id in sentences_map:
                sentence_text = sentences_map[sentence_id]
                print(f"  - [{sentence_id}] {sentence_text}")
                key_sentences_to_summarize.append(f"[{sentence_id}] {sentence_text}")
            else:
                print(f"  - Warning: Received an invalid sentence ID from the API: {sentence_id}")

        print("\nThis workflow is now ready for the final 'Generate Abstractive Summary' step.")