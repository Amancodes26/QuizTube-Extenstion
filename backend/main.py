from yt_dlp import YoutubeDL
import requests
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not ASSEMBLYAI_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing API keys in .env file")

# AssemblyAI API settings
ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
ASSEMBLYAI_TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def youtube_to_mp3(url, output_path='.'):
    try:
        # Options for yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best quality audio
            'postprocessors': [{  # Extract audio and convert to MP3
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Output file name
            'verbose': True,  # Print detailed logs
        }

        # Download and convert
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info_dict).replace(".webm", ".mp3")

        print(f"Audio downloaded: {audio_file}")
        return audio_file

    except Exception as e:
        print(f"An error occurred during download: {str(e)}")
        return None

def upload_to_assemblyai(audio_file):
    """Upload the audio file to AssemblyAI and return the upload URL."""
    try:
        headers = {
            'Authorization': ASSEMBLYAI_API_KEY  # Changed from 'authorization' to 'Authorization'
        }
        
        print("Uploading with API key:", ASSEMBLYAI_API_KEY[:8] + "...")  # Debug print
        
        with open(audio_file, 'rb') as f:
            response = requests.post(
                ASSEMBLYAI_UPLOAD_URL,
                headers=headers,
                data=f.read()  # Send the file content directly
            )
            
        print(f"Upload response status: {response.status_code}")  # Debug print
        print(f"Response content: {response.text}")  # Debug print
            
        if response.status_code == 200:
            return response.json()['upload_url']
        else:
            print(f"Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred during upload: {str(e)}")
        return None

def transcribe_with_assemblyai(audio_url):
    """Transcribe the audio file using AssemblyAI and return the transcript."""
    try:
        headers = {
            'Authorization': ASSEMBLYAI_API_KEY,  # Changed from 'authorization' to 'Authorization'
            'Content-Type': 'application/json'    # Changed from 'content-type' to 'Content-Type'
        }
        data = {
            'audio_url': audio_url,
        }
        response = requests.post(ASSEMBLYAI_TRANSCRIPT_URL, headers=headers, json=data)
        if response.status_code == 200:
            transcript_id = response.json()['id']
            print(f"Transcription started. Transcript ID: {transcript_id}")
            return transcript_id
        else:
            print(f"Transcription request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred during transcription request: {str(e)}")
        return None

def get_transcription_result(transcript_id):
    """Poll AssemblyAI for the transcription result."""
    try:
        headers = {
            'Authorization': ASSEMBLYAI_API_KEY  # Changed from 'authorization' to 'Authorization'
        }
        while True:
            response = requests.get(f"{ASSEMBLYAI_TRANSCRIPT_URL}/{transcript_id}", headers=headers)
            if response.status_code == 200:
                status = response.json()['status']
                if status == 'completed':
                    return response.json()['text']
                elif status == 'error':
                    print("Transcription failed.")
                    return None
                else:
                    print(f"Transcription status: {status}. Waiting...")
                    time.sleep(10)  # Wait 10 seconds before polling again
            else:
                print(f"Failed to check transcription status: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"An error occurred while checking transcription status: {str(e)}")
        return None

def generate_quiz_with_gemini(transcript):
    """Generate a quiz from the transcript using Gemini API."""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro')

        # Prompt for quiz generation
        prompt = f"""
        Generate a quiz based on the following transcript. The quiz should include 5 multiple-choice questions with 4 options each. Provide the correct answer for each question.

        Transcript:
        {transcript}
        """

        # Generate quiz
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred during quiz generation: {str(e)}")
        return None

if __name__ == "__main__":
    # Step 1: Download audio from YouTube
    url = input("Enter YouTube video URL: ")
    audio_file = youtube_to_mp3(url)
    
    if audio_file:
        # Step 2: Upload audio to AssemblyAI
        print("Uploading audio to AssemblyAI...")
        audio_url = upload_to_assemblyai(audio_file)
        
        if audio_url:
            # Step 3: Transcribe audio
            print("Starting transcription...")
            transcript_id = transcribe_with_assemblyai(audio_url)
            
            if transcript_id:
                # Step 4: Get transcription result
                print("Waiting for transcription to complete...")
                transcript = get_transcription_result(transcript_id)
                
                if transcript:
                    print("\nTranscript:")
                    print(transcript)

                    # Step 5: Generate quiz using Gemini API
                    print("\nGenerating quiz...")
                    quiz = generate_quiz_with_gemini(transcript)
                    
                    if quiz:
                        print("\nQuiz:")
                        print(quiz)
                    else:
                        print("Failed to generate quiz.")
                else:
                    print("Failed to retrieve transcript.")
            else:
                print("Failed to start transcription.")
        else:
            print("Failed to upload audio.")
    else:
        print("Failed to download audio.")