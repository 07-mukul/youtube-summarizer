from flask import Flask, jsonify, request
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, InvalidVideoId
from youtube_transcript_api._errors import IpBlocked, TranscriptsDisabled
from flask_cors import CORS
import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import time
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Simple cache for summaries: {video_id: {"summary": ..., "language": ..., timestamp: ...}}
summary_cache = {}
CACHE_DURATION = 86400  # Cache for 24 hours to avoid YouTube rate limiting

# Request throttling - track last request time
last_request_time = {}
MIN_REQUEST_INTERVAL = 5  # Minimum 5 seconds between requests for same video

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "API is running",
        "endpoints": {
            "GET /": "This message",
            "GET /health": "Health check",
            "GET /summary?url=YOUTUBE_URL": "Summarize YouTube video from URL"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "active", "message": "Service is running"}), 200

def extract_video_id(youtube_url):
    """Extract video ID from YouTube URL"""
    # Handle youtu.be short URLs
    if 'youtu.be/' in youtube_url:
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', youtube_url)
        if match:
            return match.group(1)
    
    # Handle youtube.com URLs
    if 'youtube.com' in youtube_url:
        parsed = urlparse(youtube_url)
        video_id = parse_qs(parsed.query).get('v', [None])[0]
        if video_id and len(video_id) == 11:
            return video_id
    
    # Check if it's already a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', youtube_url):
        return youtube_url
    
    return None

@app.route('/summary', methods=['GET'])
def youtube_summarizer():
    youtube_url = request.args.get('url', '').strip()
    demo_mode = request.args.get('demo', 'false').lower() == 'true'
    
    # Demo mode for testing without API calls
    if demo_mode:
        return jsonify({
            "data": """Here is a 10-point summary of the YouTube video based on its transcript:

1. The video begins with an engaging introduction and overview of the main topic
2. Key concepts are explained with clear examples and visual demonstrations
3. The presenter discusses the historical context and background information
4. Practical applications and real-world use cases are presented
5. Technical details are broken down into understandable segments
6. Common misconceptions and myths are addressed and clarified
7. Expert insights and tips for success are shared throughout
8. The content transitions smoothly between different interconnected topics
9. Concluding remarks summarize the main takeaways effectively
10. The video ends with a call-to-action or invitation for further engagement""",
            "error": False,
            "language": "🇬🇧 English",
            "available_languages": ["en", "es", "fr"],
            "demo": True
        }), 200
    
    # Validate URL is provided
    if not youtube_url:
        return jsonify({
            "data": "Missing YouTube URL. Please provide 'url' query parameter (e.g., https://youtube.com/watch?v=... or https://youtu.be/...)",
            "error": True
        }), 400
    
    # Extract video ID from URL
    video_id = extract_video_id(youtube_url)
    
    if not video_id:
        return jsonify({
            "data": "Invalid YouTube URL or Video ID. Please provide a valid YouTube link or video ID (11 characters)",
            "error": True
        }), 400
    
    # Check cache first (only for successful results)
    if video_id in summary_cache:
        cached_data = summary_cache[video_id]
        if time.time() - cached_data['timestamp'] < CACHE_DURATION:
            print(f"Cache hit for video {video_id}")
            return jsonify({
                "data": cached_data['summary'],
                "error": False,
                "language": cached_data['language'],
                "available_languages": cached_data.get('available_languages', []),
                "cached": True
            }), 200
        else:
            # Cache expired, remove it
            del summary_cache[video_id]
    
    try:
        transcript_data = get_transcript(video_id)
        summary = generate_summary(transcript_data['text'], transcript_data['language'])
        
        # Cache the result
        summary_cache[video_id] = {
            'summary': summary,
            'language': transcript_data.get('language', 'Unknown'),
            'available_languages': transcript_data.get('available_languages', []),
            'timestamp': time.time()
        }
        
    except NoTranscriptFound:
        return jsonify({"data": "No Subtitles found. Try videos with English or Hindi subtitles.", "error": True}), 404
    except InvalidVideoId:
        return jsonify({"data": "Invalid Video Id", "error": True}), 400
    except Exception as e:
        print(f"Error: {e}")
        error_msg = str(e)
        
        # Handle specific YouTube errors
        if "blocking" in error_msg.lower() or "ip blocked" in error_msg.lower():
            return jsonify({
                "data": "YouTube is blocking your IP due to too many requests. Solutions: 1) Wait 15-30 minutes, 2) Switch VPN server, 3) Try a different video. Cached results will be available immediately.",
                "error": True,
                "error_type": "ip_blocking",
                "solutions": [
                    "Wait 15-30 minutes for YouTube to unblock your IP",
                    "Switch to a different VPN server",
                    "Try summarizing a different video",
                    "Ensure VPN is properly connected"
                ]
            }), 429
        elif "no transcripts" in error_msg.lower() or "transcripts disabled" in error_msg.lower():
            return jsonify({"data": "This video does not have subtitles available.", "error": True}), 404
        elif "No transcripts available" in error_msg:
            return jsonify({"data": "No Subtitles found. Try videos with English or Hindi subtitles.", "error": True}), 404
        elif "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({
                "data": "API Rate limit exceeded. Please try again in a few moments.",
                "error": True,
                "error_type": "rate_limit"
            }), 429
        
        return jsonify({"data": f"Unable to Summarize the video: {error_msg}", "error": True}), 500

    return jsonify({
        "data": summary, 
        "error": False,
        "language": transcript_data.get('language', 'Unknown'),
        "available_languages": transcript_data.get('available_languages', []),
        "cached": False
    }), 200


def get_transcript(video_id):
    """Fetch transcript using Webshare proxy to avoid YouTube IP blocking"""
    
    # Build proxy URL from environment variables
    proxy_host = os.getenv("WEBSHARE_PROXY_HOST")
    proxy_port = os.getenv("WEBSHARE_PROXY_PORT")
    proxy_username = os.getenv("WEBSHARE_PROXY_USERNAME")
    proxy_password = os.getenv("WEBSHARE_PROXY_PASSWORD")
    
    # Construct proxy URL: http://username:password@host:port
    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    proxies = {
        'http': proxy_url,
        'https': proxy_url,
    }
    
    max_retries = 2
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} - Using Webshare proxy {proxy_host}:{proxy_port}")
            
            # Create requests session with proxy configuration
            session = requests.Session()
            session.proxies.update(proxies)
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Create YouTubeTranscriptApi instance and pass session with proxy
            yt_api = YouTubeTranscriptApi(http_client=session)
            
            # List all available transcripts
            transcript_list = yt_api.list(video_id)
            
            # Get all available language codes
            available_langs = set()
            available_langs.update(transcript_list._generated_transcripts.keys())
            available_langs.update(transcript_list._manually_created_transcripts.keys())
            available_langs = list(available_langs)
            
            print(f"Available languages: {available_langs}")
            
            # Try English first
            language_used = None
            transcript_response = None
            
            # Check for English (en)
            if any(lang.startswith('en') for lang in available_langs):
                try:
                    transcript_response = yt_api.fetch(video_id, languages=['en'])
                    language_used = '🇬🇧 English'
                    print(f"✅ Using English transcript")
                except Exception as e:
                    print(f"Failed to fetch English: {e}")
            
            # Try Hindi (hi) if English not available
            if transcript_response is None and any(lang.startswith('hi') for lang in available_langs):
                try:
                    transcript_response = yt_api.fetch(video_id, languages=['hi'])
                    language_used = '🇮🇳 Hindi'
                    print(f"✅ Using Hindi transcript")
                except Exception as e:
                    print(f"Failed to fetch Hindi: {e}")
            
            # Try any available language as fallback
            if transcript_response is None and available_langs:
                try:
                    first_lang = available_langs[0]
                    transcript_response = yt_api.fetch(video_id, languages=[first_lang])
                    language_used = f'Language: {first_lang}'
                    print(f"✅ Using {first_lang} transcript")
                except Exception as e:
                    print(f"Failed to fetch {first_lang}: {e}")
            
            if transcript_response is None:
                raise Exception(f"No transcripts available. Available languages: {available_langs}")
            
            # Extract text from FetchedTranscriptSnippet objects
            transcript_text = ' '.join([snippet.text for snippet in transcript_response])
            
            print(f"✅ Successfully fetched transcript with {len(transcript_text)} characters")
            
            # Success! Return the transcript
            return {
                'text': transcript_text,
                'language': language_used,
                'available_languages': available_langs
            }
            
        except InvalidVideoId as e:
            print(f"Invalid video ID: {e}")
            raise e
        except IpBlocked as e:
            print(f"Attempt {attempt + 1}/{max_retries} - IP/Proxy Blocked by YouTube: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise Exception("Proxy is blocked. YouTube is blocking requests. Please wait 15-30 minutes and try again.")
        except TranscriptsDisabled as e:
            print(f"Transcripts disabled: {e}")
            raise Exception("This video does not have transcripts available.")
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} - Transcript fetch failed: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

def generate_summary(transcript, language='English'):
    # Get all available API keys from environment
    api_keys = [
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3")
    ]
    
    # Filter out None values
    api_keys = [key for key in api_keys if key]
    
    model_name = "gemini-2.0-flash"
    
    # Adjust prompt based on language
    if 'Hindi' in language:
        prompt = f"You have to summarize a YouTube video using its Hindi transcript in 10 points. Transcript: {transcript}"
    else:
        prompt = f"You have to summarize a YouTube video using its transcript in 10 points. Transcript: {transcript}"
    
    # Try each API key
    last_error = None
    for key_index, api_key in enumerate(api_keys, 1):
        try:
            print(f"🔑 Attempting with API Key {key_index}/{len(api_keys)}")
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt, request_options={"timeout": 60})
            print(f"✅ Summary generated successfully with Key {key_index}")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            last_error = e
            print(f"❌ Key {key_index} failed: {type(e).__name__}")
            
            # Check if it's a quota error
            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"⚠️  Quota exceeded for Key {key_index}, trying next key...")
                if key_index < len(api_keys):
                    continue
                else:
                    break
            else:
                # Other errors are not quota-related, re-raise
                raise Exception(f"Unable to generate summary: {error_msg}")
    
    # All keys exhausted
    raise Exception(f"Unable to generate summary: All {len(api_keys)} API keys quota exceeded. Please try again in a few moments.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
