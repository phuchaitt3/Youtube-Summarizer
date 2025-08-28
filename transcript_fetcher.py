# transcript_fetcher.py

# First, ensure the library is installed:
# pip install youtube-transcript-api

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
import os

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

# This block allows you to run this file directly for testing purposes
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=t-53fouKqWI" 
    print(f"Testing transcript fetcher with URL: {test_url}\n")
    
    content = get_youtube_transcript(test_url)
    
    if content.startswith("Error:"):
        print(content)
    else:
        print("--- Transcript Fetched Successfully (first 200 chars) ---")
        print(content[:200] + "...")