import os
import json
import time
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from notion_client import Client
from plyer import notification
from dotenv import load_dotenv
import re

class YouTubeNotionSummarizer:
    def __init__(self):
        load_dotenv()
        
        # Load API keys and configuration
        self.notion_api_key = os.getenv('NOTION_API_KEY')
        self.notion_page_id = os.getenv('NOTION_PAGE_ID')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Initialize Notion client
        self.notion = Client(auth=self.notion_api_key)
        
        # YouTube channel configuration
        self.channel_id = "UCGq-a57w-aPwyi3pW7XLiHw"  # Diary of a CEO channel ID
        self.storage_file = "processed_videos.json"
        self.check_interval = 24 * 60 * 60  # 24 hours in seconds
        
        # Create transcripts directory if it doesn't exist
        self.transcripts_dir = "transcripts"
        os.makedirs(self.transcripts_dir, exist_ok=True)

    def get_latest_videos(self, limit=5):
        try:
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}"
            response = requests.get(rss_url)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            videos = []
            for entry in entries[:limit]:
                video = {
                    'title': entry.find('{http://www.w3.org/2005/Atom}title').text,
                    'published': entry.find('{http://www.w3.org/2005/Atom}published').text,
                    'video_id': entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text,
                    'url': f"https://www.youtube.com/watch?v={entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text}"
                }
                videos.append(video)
            
            return videos
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return []

    def save_transcript(self, video_id, title, transcript_data):
        try:
            # Clean the title to use as filename (remove special characters)
            clean_title = re.sub(r'[^\w\s-]', '', title)
            clean_title = re.sub(r'[-\s]+', '_', clean_title).strip('-_')
            
            # Create filename with video ID to ensure uniqueness
            filename = f"{clean_title}_{video_id}.txt"
            filepath = os.path.join(self.transcripts_dir, filename)
            
            # Extract and join only the text content, removing timestamps
            transcript_text = ' '.join(entry['text'] for entry in transcript_data)
            
            # Save the clean transcript
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            
            return transcript_text
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return None

    def get_transcript(self, video_id, title):
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            return self.save_transcript(video_id, title, transcript_data)
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {e}")
            return None

    def generate_summary(self, transcript):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Create a concise summary of this video transcript. Format your response exactly as follows:

1. Main Topic (one sentence)
2. Key Points (3-5 bullet points)
3. Notable Quotes (1-2 most impactful quotes)
4. Key Takeaways (2-3 practical insights)

Transcript:
{transcript}"""
            
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                raise Exception("No valid response from Gemini API")
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

    def create_notion_page(self, video_info, summary):
        try:
            # Split summary into chunks of 2000 characters or less
            summary_chunks = [summary[i:i+1900] for i in range(0, len(summary), 1900)]
            
            # Create the initial blocks with video info
            blocks = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": f"Video URL: {video_info['url']}"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": f"Published: {video_info['published']}"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                }
            ]
            
            # Add each chunk of the summary as a separate paragraph block
            for chunk in summary_chunks:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": chunk}}]
                    }
                })
            
            new_page = self.notion.pages.create(
                parent={"page_id": self.notion_page_id},
                properties={
                    "title": {
                        "title": [{"text": {"content": video_info['title']}}]
                    }
                },
                children=blocks
            )
            return new_page
        except Exception as e:
            print(f"Error creating Notion page: {e}")
            return None

    def load_processed_videos(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_processed_videos(self, videos):
        with open(self.storage_file, 'w') as f:
            json.dump(videos, f)

    def send_notification(self, title, message):
        try:
            # Use osascript for macOS notifications
            os.system(f"""
                osascript -e 'display notification "{message}" with title "{title}"'
            """)
            # Also print to console
            print(f"\n{title}")
            print(message)
        except Exception as e:
            print(f"Error sending notification: {e}")
            # Fallback to console output
            print(f"\n{title}")
            print(message)

    def process_video(self, video_info):
        print(f"\nProcessing video: {video_info['title']}")
        
        # Get transcript and generate summary
        transcript = self.get_transcript(video_info['video_id'], video_info['title'])
        if not transcript:
            return False
            
        summary = self.generate_summary(transcript)
        if not summary:
            return False
            
        # Create Notion page
        notion_page = self.create_notion_page(video_info, summary)
        if not notion_page:
            return False
            
        return True

    def process_new_videos(self):
        print(f"\nChecking for new videos at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get latest videos
        latest_videos = self.get_latest_videos(limit=5)
        if not latest_videos:
            return
            
        # Load processed videos
        processed_videos = self.load_processed_videos()
        processed_ids = [v['video_id'] for v in processed_videos]
        
        # Process new videos
        new_videos = [v for v in latest_videos if v['video_id'] not in processed_ids]
        
        if new_videos:
            for video in new_videos:
                if self.process_video(video):
                    processed_videos.append(video)
                    self.save_processed_videos(processed_videos)
                    self.send_notification(
                        "New Video Summary Added!",
                        f"Summary for '{video['title']}' has been added to Notion"
                    )
        else:
            print("No new videos to process")

    def run(self):
        print("YouTube to Notion summarizer service started!")
        print("Checking for new videos from Diary of a CEO every 24 hours...")
        print("Press Ctrl+C to stop")
        
        # Initial run to process the last 5 videos
        self.process_new_videos()
        
        # Continue checking for new videos
        while True:
            time.sleep(self.check_interval)
            self.process_new_videos()

if __name__ == "__main__":
    summarizer = YouTubeNotionSummarizer()
    summarizer.run() 