from flask import Flask, request, jsonify
from flask_cors import CORS
from main import youtube_to_mp3, upload_to_assemblyai, transcribe_with_assemblyai, get_transcription_result, generate_quiz_with_gemini

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'})

        # Step 1: Download audio
        print(f"Processing URL: {url}")
        audio_file = youtube_to_mp3(url)
        
        if not audio_file:
            return jsonify({'success': False, 'error': 'Failed to download audio'})

        # Step 2: Upload to AssemblyAI
        audio_url = upload_to_assemblyai(audio_file)
        if not audio_url:
            return jsonify({'success': False, 'error': 'Failed to upload audio'})

        # Step 3: Transcribe
        transcript_id = transcribe_with_assemblyai(audio_url)
        if not transcript_id:
            return jsonify({'success': False, 'error': 'Failed to start transcription'})

        # Step 4: Get transcription
        transcript = get_transcription_result(transcript_id)
        if not transcript:
            return jsonify({'success': False, 'error': 'Failed to get transcript'})

        # Step 5: Generate quiz
        quiz = generate_quiz_with_gemini(transcript)
        if not quiz:
            return jsonify({'success': False, 'error': 'Failed to generate quiz'})

        return jsonify({
            'success': True,
            'data': {
                'quiz': quiz
            }
        })

    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")  # Add logging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500  # Return 500 status code for server errors

if __name__ == '__main__':
    app.run(debug=True)
