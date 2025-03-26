import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
import time
from plyer import notification

class YouTubeNotifier:
    def __init__(self):
        self.channel_id = "UCGq-a57w-aPwyi3pW7XLiHw"  # Diary of a CEO channel ID
        self.storage_file = "last_video.json"
        self.check_interval = 24 * 60 * 60  # 24 hours in seconds

    def get_latest_video(self):
        try:
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}"
            response = requests.get(rss_url)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            latest_entry = root.find('{http://www.w3.org/2005/Atom}entry')
            
            if latest_entry is not None:
                return {
                    'title': latest_entry.find('{http://www.w3.org/2005/Atom}title').text,
                    'published': latest_entry.find('{http://www.w3.org/2005/Atom}published').text,
                    'video_id': latest_entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text,
                    'url': f"https://www.youtube.com/watch?v={latest_entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text}"
                }
            return None
        except Exception as e:
            print(f"Error fetching video information: {e}")
            return None

    def load_last_video(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_last_video(self, video_info):
        with open(self.storage_file, 'w') as f:
            json.dump(video_info, f)

    def send_notification(self, video_info):
        notification.notify(
            title='New Video from Diary of a CEO!',
            message=f"{video_info['title']}\nClick to watch!",
            app_icon=None,  # You can add an icon path here
            timeout=10
        )
        print(f"\nNew video detected!")
        print(f"Title: {video_info['title']}")
        print(f"URL: {video_info['url']}")

    def check_for_new_videos(self):
        print(f"\nChecking for new videos at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        latest_video = self.get_latest_video()
        last_known_video = self.load_last_video()

        if latest_video:
            if not last_known_video or latest_video['video_id'] != last_known_video['video_id']:
                self.send_notification(latest_video)
                self.save_last_video(latest_video)
            else:
                print("No new videos found")

    def run(self):
        print("YouTube notification service started!")
        print("Checking for new videos from Diary of a CEO every 24 hours...")
        print("Press Ctrl+C to stop")
        
        while True:
            self.check_for_new_videos()
            time.sleep(self.check_interval)

if __name__ == "__main__":
    notifier = YouTubeNotifier()
    notifier.run() 