#!/usr/bin/env python3
"""
Vimeo Old Movies Finder
Searches for old/classic movies on Vimeo and exports results to CSV
"""

import requests
import csv
import json
import os
from datetime import datetime
from typing import List, Dict
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class VimeoMovieFinder:
    def __init__(self, access_token: str = None):
        """
        Initialize the Vimeo finder
        
        Args:
            access_token: Vimeo API access token (get from https://developer.vimeo.com/)
        """
        self.access_token = access_token
        self.base_url = "https://api.vimeo.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.vimeo.*+json;version=3.4"
        } if access_token else {}
        
    def search_videos(self, query: str, per_page: int = 50, max_results: int = 50) -> List[Dict]:
        """
        Search for videos on Vimeo
        
        Args:
            query: Search query
            per_page: Results per page
            max_results: Maximum number of results to return
            
        Returns:
            List of video dictionaries
        """
        if not self.access_token:
            print("⚠️  No API token provided. Please get one from https://developer.vimeo.com/")
            return []
        
        videos = []
        page = 1
        
        print(f"🔍 Searching Vimeo for: '{query}'...")
        
        while len(videos) < max_results:
            try:
                url = f"{self.base_url}/videos"
                params = {
                    "query": query,
                    "per_page": min(per_page, max_results - len(videos)),
                    "page": page,
                    "sort": "relevant",
                    "filter": "CC"  # Creative Commons filter for old/public domain content
                }
                
                response = requests.get(url, headers=self.headers, params=params)
                
                if response.status_code == 401:
                    print("❌ Authentication failed. Please check your API token.")
                    break
                elif response.status_code != 200:
                    print(f"❌ API request failed with status {response.status_code}")
                    break
                
                data = response.json()
                
                if not data.get("data"):
                    print(f"✓ No more results found. Got {len(videos)} videos total.")
                    break
                
                for video in data["data"]:
                    # Extract tags
                    tags = []
                    if video.get("tags"):
                        tags = [tag.get("name", "") for tag in video.get("tags", [])]

                    # Extract categories
                    categories = []
                    if video.get("categories"):
                        categories = [cat.get("name", "") for cat in video.get("categories", [])]

                    videos.append({
                        "title": video.get("name", "Untitled"),
                        "url": video.get("link", ""),
                        "description": video.get("description", "") if video.get("description") else "",  # Full description
                        "description_short": video.get("description", "")[:200] if video.get("description") else "",  # Truncated for display
                        "duration": video.get("duration", 0),
                        "duration_formatted": self._format_duration(video.get("duration", 0)),
                        "created_date": video.get("created_time", ""),
                        "views": video.get("stats", {}).get("plays", 0),
                        "likes": video.get("metadata", {}).get("connections", {}).get("likes", {}).get("total", 0),
                        "comments": video.get("metadata", {}).get("connections", {}).get("comments", {}).get("total", 0),
                        "user": video.get("user", {}).get("name", "Unknown"),
                        "user_url": video.get("user", {}).get("link", ""),
                        "tags": tags,
                        "categories": categories,
                    })
                    
                    if len(videos) >= max_results:
                        break
                
                print(f"  Found {len(videos)}/{max_results} videos...")
                
                # Check if there are more pages
                if not data.get("paging", {}).get("next"):
                    break
                    
                page += 1
                time.sleep(0.5)  # Be nice to the API
                
            except Exception as e:
                print(f"❌ Error during search: {e}")
                break
        
        return videos[:max_results]
    
    def search_multiple_queries(self, queries: List[str], per_query: int = 10) -> List[Dict]:
        """
        Search multiple queries and combine results
        """
        all_videos = []
        seen_urls = set()
        
        for query in queries:
            videos = self.search_videos(query, per_page=per_query, max_results=per_query)
            
            # Deduplicate
            for video in videos:
                if video["url"] not in seen_urls:
                    all_videos.append(video)
                    seen_urls.add(video["url"])
            
            time.sleep(1)  # Rate limiting
        
        return all_videos
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def save_to_csv(self, videos: List[Dict], filename: str = "vimeo_old_movies.csv"):
        """Save videos to CSV file"""
        import os

        if not videos:
            print("❌ No videos to save.")
            return

        # Create outputs directory if it doesn't exist
        output_dir = "outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, filename)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=videos[0].keys())
            writer.writeheader()
            writer.writerows(videos)

        print(f"✅ Saved {len(videos)} videos to {output_path}")
        return output_path
    
    def save_to_json(self, videos: List[Dict], filename: str = "vimeo_old_movies.json"):
        """Save videos to JSON file"""
        import os

        if not videos:
            print("❌ No videos to save.")
            return

        # Create outputs directory if it doesn't exist
        output_dir = "outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved {len(videos)} videos to {output_path}")
        return output_path


def main():
    """Main execution function"""

    # Load API token from environment variables
    # Get your API token from https://developer.vimeo.com/
    # 1. Create a free account
    # 2. Go to https://developer.vimeo.com/apps
    # 3. Create a new app
    # 4. Generate an access token with "public" and "private" scopes
    # 5. Add it to your .env file as VIMEO_API_TOKEN

    API_TOKEN = os.getenv("VIMEO_API_TOKEN")

    if not API_TOKEN:
        print("❌ Error: VIMEO_API_TOKEN not found in environment variables")
        print("📝 Please create a .env file with your Vimeo API token")
        print("   See .env.example for the template")
        return

    # Initialize finder
    finder = VimeoMovieFinder(access_token=API_TOKEN)
    
    # Search queries for old movies
    search_queries = [
        "classic films",
        "old movies 1920s",
        "silent films",
        "vintage cinema",
        "public domain films",
        "classic hollywood",
        "old westerns",
        "film noir",
        "early cinema",
        "1930s movies"
    ]
    
    print("=" * 60)
    print("🎬 VIMEO OLD MOVIES FINDER")
    print("=" * 60)
    print()
    
    # Option 1: Single query search
    # videos = finder.search_videos("classic films", max_results=50)
    
    # Option 2: Multiple queries (recommended for variety)
    videos = finder.search_multiple_queries(search_queries, per_query=5)
    
    if videos:
        print()
        print(f"✅ Found {len(videos)} unique videos!")
        print()
        
        # Save to CSV
        csv_path = finder.save_to_csv(videos, "vimeo_old_movies.csv")
        
        # Also save to JSON for backup
        json_path = finder.save_to_json(videos, "vimeo_old_movies.json")
        
        # Print first few results
        print()
        print("📋 Sample results:")
        print("-" * 60)
        for i, video in enumerate(videos[:5], 1):
            print(f"{i}. {video['title']}")
            print(f"   URL: {video['url']}")
            print(f"   Duration: {video['duration_formatted']} | Views: {video['views']}")
            print()
    else:
        print("❌ No videos found. Make sure you set your API token!")
        print()
        print("📝 To get your Vimeo API token:")
        print("   1. Go to https://developer.vimeo.com/apps")
        print("   2. Create a new app (free)")
        print("   3. Generate an access token")
        print("   4. Replace 'YOUR_VIMEO_API_TOKEN_HERE' in this script")


if __name__ == "__main__":
    main()
