# youtube_transcript.py

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
    # Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
    match = re.search(r"watch\?v=([^&]+)", url)
    if match:
        return match.group(1)
    
    # Shortened youtu.be URL: https://youtu.be/VIDEO_ID
    match = re.search(r"youtu\.be/([^?]+)", url)
    if match:
        return match.group(1)
        
    # Shorts URL: https://www.youtube.com/shorts/VIDEO_ID
    match = re.search(r"shorts/([^?]+)", url)
    if match:
        return match.group(1)

    return None

def get_youtube_transcript(video_url):
    """
    Retrieves the full transcript for a given YouTube video URL.
    This version correctly handles the object-based output from the .fetch() method.
    """
    video_id = get_video_id(video_url)
    
    if not video_id:
        return "Error: Could not extract a valid video ID from the URL."

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id)
        
        # --- THIS IS THE FIX ---
        # Instead of using dictionary-style access (item['text']),
        # we now use attribute-style access (snippet.text) because the library
        # returns a list of objects, not dictionaries.
        full_transcript = " ".join([snippet.text for snippet in transcript_list])
        
        return full_transcript
        
    except TranscriptsDisabled:
        return f"Error: Transcripts are disabled for the video (ID: {video_id})."
    except NoTranscriptFound:
        return f"Error: No transcript could be found for the video (ID: {video_id})."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Example Usage ---
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=t-53fouKqWI" 
    
    # Define the output filename. You can change this.
    # A good practice is to use the video ID in the filename.
    video_id_for_filename = get_video_id(youtube_url)
    output_filename = f"{video_id_for_filename}_transcript.txt" # Or .md for markdown

    print(f"Fetching transcript for: {youtube_url}\n")
    
    transcript_content = get_youtube_transcript(youtube_url)
    
    if transcript_content.startswith("Error:"):
        print(transcript_content) # Print error if occurred
    else:
        # Save the transcript to a file
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(transcript_content)
            print(f"Transcript successfully saved to '{output_filename}'")
            # Optionally, print the path where it's saved
            print(f"Saved at: {os.path.abspath(output_filename)}")
        except IOError as e:
            print(f"Error saving file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving: {e}")