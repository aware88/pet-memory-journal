import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_latest_video():
    try:
        # The RSS feed URL for the channel
        channel_id = "UCGq-a57w-aPwyi3pW7XLiHw"  # Diary of a CEO channel ID
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        # Get the RSS feed
        response = requests.get(rss_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ET.fromstring(response.content)
        
        # Find the first (most recent) entry
        latest_entry = root.find('{http://www.w3.org/2005/Atom}entry')
        
        if latest_entry is not None:
            # Extract information
            title = latest_entry.find('{http://www.w3.org/2005/Atom}title').text
            published = latest_entry.find('{http://www.w3.org/2005/Atom}published').text
            video_id = latest_entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Convert published time to datetime
            pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
            
            # Format the output
            print("\nLatest video from Diary of a CEO:")
            print(f"Title: {title}")
            print(f"Published: {pub_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"URL: {url}")
        else:
            print("No videos found")
            
    except Exception as e:
        print(f"Error fetching video information: {e}")

if __name__ == "__main__":
    get_latest_video() 