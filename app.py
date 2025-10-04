# Render - Exotel Call Processor Web Service (No Zapier Required)
from flask import Flask, request, jsonify
import json
import requests
from datetime import datetime, timedelta
import asyncio
import aiohttp
import os
import threading
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Your API credentials
EXOTEL_SID = os.getenv('EXOTEL_SID', 'abc6862')
EXOTEL_API_KEY = os.getenv('EXOTEL_API_KEY', '119f006d2b474e28bb0f8cf0c50d7aa832730aef0cd962e8')
EXOTEL_API_TOKEN = os.getenv('EXOTEL_API_TOKEN', '5b6e0ba111cc82717ffa89cc376d4a6d8e98aff852d03258')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', 'xoxb-9603666278855-9651417565664-e3ojaluTEZRHumWwXwwLSl5k')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', 'C09K19DFXT2')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK', 'https://hooks.slack.com/services/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')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', '8ee5702190b142447a7ae419e66b4450dcfeae4c')

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Global processor instance
processor = None

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Exotel Call Processor (No Zapier)',
        'version': '2.0.0',
        'scheduler_status': 'active' if scheduler.running else 'inactive',
        'endpoints': {
            'trigger': '/trigger',
            'health': '/',
            'status': '/status',
            'scheduler': '/scheduler',
            'logs': '/logs'
        }
    })

@app.route('/trigger', methods=['POST', 'GET'])
def trigger_processing():
    """Manual trigger endpoint for call processing"""
    try:
        global processor
        if not processor:
            processor = MultiAgentCallProcessor()
        
        # Run the monitoring cycle
        result = processor.run_single_cycle()
        
        return jsonify({
            'success': True,
            'message': 'Call processing triggered successfully',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Trigger processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Call processing failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status')
def status():
    """Detailed status endpoint"""
    global processor
    return jsonify({
        'status': 'healthy',
        'uptime': 'running',
        'scheduler_running': scheduler.running,
        'processor_initialized': processor is not None,
        'last_check': datetime.now().isoformat(),
        'environment': {
            'exotel_sid': EXOTEL_SID,
            'slack_channel': SLACK_CHANNEL,
            'slack_webhook_configured': bool(SLACK_WEBHOOK)
        }
    })

@app.route('/scheduler')
def scheduler_status():
    """Scheduler management endpoint"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': str(job.next_run_time) if job.next_run_time else None,
            'trigger': str(job.trigger)
        })
    
    return jsonify({
        'scheduler_running': scheduler.running,
        'jobs': jobs,
        'job_count': len(jobs)
    })

@app.route('/logs')
def get_logs():
    """Get recent processing logs"""
    # In production, you'd want to implement proper log storage
    return jsonify({
        'message': 'Logs endpoint - implement log storage for production',
        'suggestion': 'Use a logging service like LogDNA or Papertrail'
    })

def scheduled_call_processing():
    """Scheduled function to process calls automatically"""
    try:
        logger.info("=== SCHEDULED CALL PROCESSING STARTED ===")
        global processor
        if not processor:
            processor = MultiAgentCallProcessor()
        
        result = processor.run_single_cycle()
        logger.info(f"Scheduled processing completed: {result}")
        
    except Exception as e:
        logger.error(f"Scheduled processing error: {str(e)}")

# Schedule the call processing job to run every 5 minutes
scheduler.add_job(
    func=scheduled_call_processing,
    trigger=IntervalTrigger(minutes=5),
    id='call_processing_job',
    name='Call Processing Job',
    replace_existing=True
)

# Shutdown scheduler when app exits
atexit.register(lambda: scheduler.shutdown())

class MultiAgentCallProcessor:
    def __init__(self):
        # Your API credentials
        self.exotel_sid = EXOTEL_SID
        self.exotel_api_key = EXOTEL_API_KEY
        self.exotel_api_token = EXOTEL_API_TOKEN
        self.slack_bot_token = SLACK_BOT_TOKEN
        self.slack_channel = SLACK_CHANNEL
        self.slack_webhook = SLACK_WEBHOOK
        self.deepgram_api_key = DEEPGRAM_API_KEY
        
        # Agent configuration
        self.agents = {
            '+919631084471': {
                'name': 'Prateek Raj',
                'slack_handle': '<@U09HRKLA3KR>',
                'department': 'Customer Success',
                'full_name': 'Prateek Raj'
            }
        }
        
        # Track processed calls (in production, use a database)
        self.processed_calls = set()
        logger.info("MultiAgentCallProcessor initialized")
    
    def run_single_cycle(self):
        """Run a single monitoring cycle"""
        try:
            logger.info("=== STARTING CALL PROCESSING CYCLE ===")
            
            # Fetch latest calls
            calls = self.fetch_latest_calls()
            if not calls:
                return {
                    'success': True,
                    'message': 'No new calls to process',
                    'calls_processed': 0
                }
            
            # Process each call
            results = []
            for call in calls:
                result = self.process_single_call(call)
                results.append(result)
            
            return {
                'success': True,
                'message': f'Processed {len(calls)} calls',
                'calls_processed': len(calls),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Call processing cycle failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Call processing cycle failed'
            }
    
    def fetch_latest_calls(self):
        """Fetch latest calls from Exotel API"""
        try:
            logger.info("=== FETCHING CALLS FROM EXOTEL ===")
            api_url = f"https://api.exotel.com/v1/Accounts/{self.exotel_sid}/Calls.json"
            
            auth = requests.auth.HTTPBasicAuth(self.exotel_api_key, self.exotel_api_token)
            api_response = requests.get(api_url, auth=auth, params={'PageSize': 10, 'Page': 0}, timeout=30)
            
            logger.info(f"API Response: {api_response.status_code}")
            
            if api_response.status_code != 200:
                logger.error(f"API Error: {api_response.status_code}")
                return []
            
            calls_data = api_response.json()
            calls = calls_data.get('Calls', [])
            logger.info(f"Found {len(calls)} calls")
            
            # Filter for completed calls with recordings
            completed_calls = []
            for call in calls:
                if (call.get('Status') == 'completed' and 
                    call.get('RecordingUrl') and
                    call.get('Sid') not in self.processed_calls):
                    completed_calls.append(call)
                    self.processed_calls.add(call.get('Sid'))
            
            logger.info(f"Found {len(completed_calls)} new calls to process")
            return completed_calls
            
        except Exception as e:
            logger.error(f"Error fetching calls: {str(e)}")
            return []
    
    def process_single_call(self, call):
        """Process a single call"""
        try:
            call_sid = call.get('Sid')
            recording_url = call.get('RecordingUrl')
            from_number = call.get('From', 'Unknown')
            to_number = call.get('To', 'Unknown')
            duration = call.get('Duration', 0)
            start_time = call.get('StartTime', 'Unknown')
            
            logger.info(f"Processing call: {call_sid}")
            
            # Convert UTC to IST
            start_time_ist = self.convert_to_ist(start_time)
            
            # Determine call direction
            call_direction, support_number, customer_number = self.determine_call_direction(from_number, to_number)
            
            # Upload voice recording
            voice_result = self.upload_voice_to_slack(call_sid, recording_url, from_number, to_number, duration, start_time_ist)
            
            # Transcribe audio
            transcript = self.transcribe_audio(recording_url)
            
            # Analyze concern
            concern_analysis = self.analyze_concern(transcript)
            
            # Post to Slack
            slack_result = self.post_to_slack(
                call_sid, from_number, to_number, duration, start_time_ist,
                transcript, concern_analysis, call_direction, support_number,
                customer_number, voice_result
            )
            
            return {
                'call_id': call_sid,
                'voice_uploaded': voice_result.get('success', False),
                'transcript': transcript,
                'concern': concern_analysis.get('concern', 'General Inquiry'),
                'mood': concern_analysis.get('mood', 'Neutral'),
                'slack_posted': slack_result.get('success', False)
            }
            
        except Exception as e:
            logger.error(f"Error processing call: {str(e)}")
            return {
                'call_id': call.get('Sid', 'unknown'),
                'error': str(e)
            }
    
    def convert_to_ist(self, start_time):
        """Convert UTC time to IST"""
        try:
            if 'T' in start_time:
                utc_time = datetime.strptime(start_time.split('T')[0] + ' ' + start_time.split('T')[1].split('.')[0], '%Y-%m-%d %H:%M:%S')
            else:
                utc_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            ist_time = utc_time + timedelta(hours=5, minutes=30)
            return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')
        except:
            return start_time + ' IST'
    
    def determine_call_direction(self, from_number, to_number):
        """Determine call direction and roles"""
        prateek_number = '+919631084471'
        if from_number == prateek_number:
            return 'OUTBOUND', from_number, to_number
        else:
            return 'INBOUND', prateek_number, from_number
    
    def upload_voice_to_slack(self, call_sid, recording_url, from_number, to_number, duration, start_time):
        """Upload voice recording to Slack"""
        try:
            logger.info(f"=== UPLOADING VOICE RECORDING FOR {call_sid} ===")
            
            # Download the recording with Exotel authentication
            auth = requests.auth.HTTPBasicAuth(self.exotel_api_key, self.exotel_api_token)
            audio_response = requests.get(recording_url, auth=auth, timeout=30)
            if audio_response.status_code != 200:
                logger.error(f"Failed to download recording: {audio_response.status_code}")
                return {'success': False, 'error': 'Failed to download recording'}
            
            audio_data = audio_response.content
            logger.info(f"Downloaded {len(audio_data)} bytes of audio")
            
            # Get upload URL
            upload_url_response = requests.post(
                'https://slack.com/api/files.getUploadURLExternal',
                headers={'Authorization': f'Bearer {self.slack_bot_token}'},
                data={
                    'filename': f'call_{call_sid}.mp3',
                    'length': len(audio_data),
                    'alt_txt': f'Call Recording - {call_sid}',
                    'snippet_type': 'audio'
                },
                timeout=30
            )
            
            if upload_url_response.status_code == 200:
                upload_data = upload_url_response.json()
                if upload_data.get('ok'):
                    upload_url = upload_data['upload_url']
                    file_id = upload_data['file_id']
                    
                    # Upload the file
                    upload_response = requests.post(
                        upload_url,
                        files={'file': ('call_recording.mp3', audio_data, 'audio/mp3')},
                        timeout=60
                    )
                    
                    if upload_response.status_code == 200:
                        # Complete upload
                        complete_response = requests.post(
                            'https://slack.com/api/files.completeUploadExternal',
                            headers={'Authorization': f'Bearer {self.slack_bot_token}'},
                            data={
                                'files': json.dumps([{
                                    'id': file_id,
                                    'title': f'Call Recording - {call_sid}',
                                    'channels': self.slack_channel,
                                    'initial_comment': f'🎧 **Call Recording - {call_sid}**\n📞 Duration: {duration//60}m {duration%60}s | From: {from_number} to {to_number}'
                                }])
                            },
                            timeout=30
                        )
                        
                        if complete_response.status_code == 200:
                            logger.info("✅ Voice recording uploaded successfully")
                            return {'success': True, 'file_id': file_id}
            
            logger.error("❌ Voice recording upload failed")
            return {'success': False, 'error': 'Upload failed'}
            
        except Exception as e:
            logger.error(f"Voice upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def transcribe_audio(self, recording_url):
        """Transcribe audio using Deepgram"""
        try:
            logger.info("=== TRANSCRIBING AUDIO ===")
            deepgram_api_key = self.deepgram_api_key
            
            headers = {
                'Authorization': f'Token {deepgram_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': recording_url,
                'model': 'nova-2',
                'language': 'en-US',
                'punctuate': True,
                'smart_format': True
            }
            
            response = requests.post(
                'https://api.deepgram.com/v1/listen',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
                logger.info("✅ Transcription successful")
                return transcript.strip() if transcript else "Transcription unavailable"
            else:
                logger.error(f"Transcription failed: {response.status_code}")
                return f"Transcription failed - API error {response.status_code}"
                
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return f"Transcription failed - {str(e)}"
    
    def analyze_concern(self, transcript):
        """Analyze concern from transcript"""
        if not transcript or "Transcription failed" in transcript:
            return {'concern': 'General Inquiry', 'mood': 'Neutral', 'priority': 'Normal'}
        
        transcript_lower = transcript.lower()
        
        # Enhanced concern detection
        concerns = {
            'Background Verification': ['background verification', 'background check', 'verification', 'documents'],
            'Document Submission': ['document submission', 'documents', 'submit', 'requirements'],
            'Billing Issue': ['bill', 'payment', 'charge', 'invoice', 'amount', 'cost'],
            'Technical Problem': ['not working', 'error', 'broken', 'issue', 'problem'],
            'General Inquiry': ['hello', 'thank you', 'time', 'call']
        }
        
        detected_concern = 'General Inquiry'
        for concern_type, keywords in concerns.items():
            if any(keyword in transcript_lower for keyword in keywords):
                detected_concern = concern_type
                break
        
        # Mood analysis
        mood = 'Neutral'
        if 'thank you' in transcript_lower:
            mood = 'Friendly'
        elif any(word in transcript_lower for word in ['angry', 'frustrated', 'upset']):
            mood = 'Negative'
        
        return {
            'concern': detected_concern,
            'mood': mood,
            'priority': 'Normal'
        }
    
    def post_to_slack(self, call_sid, from_number, to_number, duration, start_time, 
                     transcript, concern_analysis, call_direction, support_number, 
                     customer_number, voice_upload_result):
        """Post complete message to Slack"""
        try:
            logger.info("=== POSTING TO SLACK ===")
            
            # Format duration
            minutes = duration // 60
            seconds = duration % 60
            duration_formatted = f"{minutes}m {seconds}s"
            
            # Create the complete message
            message = f"""🆕 NEW Call Summary - Customer ({customer_number})

📞 Support Number: {support_number}                    📱 Customer Number: {customer_number}

📞 EXOPHONE: 09513886363                    ⚡ Flow: abc6862 Landing Flow

🎯 Concern: {concern_analysis['concern']} from SpringVerified (Tone: {concern_analysis['mood']})                    👤 CS Agent: <@U09HRKLA3KR> <{support_number}>

🏢 Department: Customer Success                    🕐 Timestamp: {start_time}

👤 Assigned To: Prateek                    📋 Status: Open

📊 Call Metadata:
• Call ID: {call_sid}
• Duration: {duration_formatted}
• Direction: {call_direction}
• EXOPHONE: 09513886363
• Status: Completed

📝 Full Transcription:
{transcript}

🎧 Recording/Voice Note:
{"Voice message posted above" if voice_upload_result.get('success') else "Recording upload failed"}

👤 Agent: <@U09HRKLA3KR>"""

            # Post to Slack
            payload = {
                "text": message,
                "username": "Exotel Multi-Agent Processor",
                "icon_emoji": ":telephone_receiver:"
            }
            
            response = requests.post(
                self.slack_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack message posted successfully")
                return {'success': True}
            else:
                logger.error(f"❌ Slack post failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            logger.error(f"Slack post error: {str(e)}")
            return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Exotel Call Processor on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
