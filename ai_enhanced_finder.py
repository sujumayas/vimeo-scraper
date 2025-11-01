#!/usr/bin/env python3
"""
AI-Enhanced Vimeo Movie Finder
Uses Claude API to filter and classify old movies from Vimeo
"""

import requests
import csv
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AIEnhancedMovieFinder:
    def __init__(self, vimeo_token: str = None, claude_api_key: str = None):
        """
        Initialize with API tokens
        
        Args:
            vimeo_token: Vimeo API token
            claude_api_key: Anthropic Claude API key (optional)
        """
        self.vimeo_token = vimeo_token
        self.claude_api_key = claude_api_key
        self.vimeo_base_url = "https://api.vimeo.com"
        self.claude_base_url = "https://api.anthropic.com/v1/messages"
        
    def search_vimeo(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search Vimeo using API"""
        if not self.vimeo_token:
            print("⚠️  No Vimeo API token provided")
            return []
        
        headers = {
            "Authorization": f"Bearer {self.vimeo_token}",
            "Accept": "application/vnd.vimeo.*+json;version=3.4"
        }
        
        videos = []
        page = 1
        
        print(f"🔍 Searching Vimeo for: '{query}'...")
        
        while len(videos) < max_results:
            try:
                params = {
                    "query": query,
                    "per_page": min(25, max_results - len(videos)),
                    "page": page
                }
                
                response = requests.get(
                    f"{self.vimeo_base_url}/videos",
                    headers=headers,
                    params=params
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                
                if not data.get("data"):
                    break
                
                for video in data["data"]:
                    videos.append({
                        "title": video.get("name", ""),
                        "url": video.get("link", ""),
                        "description": video.get("description", ""),
                        "duration": video.get("duration", 0),
                        "created_time": video.get("created_time", ""),
                        "views": video.get("stats", {}).get("plays", 0),
                        "user": video.get("user", {}).get("name", "")
                    })
                
                page += 1
                
            except Exception as e:
                print(f"Error: {e}")
                break
        
        return videos[:max_results]
    
    def classify_with_ai(self, videos: List[Dict]) -> List[Dict]:
        """
        Use Claude AI to classify and enhance video information
        
        This will:
        - Determine the approximate era/decade
        - Classify genre (horror, comedy, drama, etc.)
        - Estimate if it's actually an old/classic film
        - Add quality/relevance score
        """
        if not self.claude_api_key:
            print("⚠️  No Claude API key provided. Skipping AI classification.")
            return videos
        
        print("\n🤖 Using AI to classify videos...")
        
        # Process videos in batches
        batch_size = 10
        enhanced_videos = []
        
        for i in range(0, len(videos), batch_size):
            batch = videos[i:i+batch_size]
            
            # Prepare video info for AI
            video_info = []
            for v in batch:
                video_info.append({
                    "title": v["title"],
                    "description": v["description"][:300] if v["description"] else "",
                    "year": v.get("created_time", "")[:4]
                })
            
            # Create prompt for Claude
            prompt = f"""Analyze these videos and determine which are genuinely old/classic films (pre-1970) or compilations/restorations of old film content.
For each video, provide:
- is_old_movie: true/false (is this actually a classic/old film or restoration/compilation of old film footage?)
- estimated_era: decade like "1920s", "1940s", or "modern" (based on the FILM CONTENT, not upload date)
- genre: primary genre (horror, comedy, drama, western, sci-fi, etc.)
- relevance_score: 1-10 (how relevant is this to someone searching for old movies? Give higher scores to actual old film content, restorations, and compilations)

Videos:
{json.dumps(video_info, indent=2)}

Respond with ONLY a JSON array of objects, one per video, in the same order.
Example format:
[
  {{"is_old_movie": true, "estimated_era": "1920s", "genre": "comedy", "relevance_score": 9}},
  {{"is_old_movie": false, "estimated_era": "modern", "genre": "documentary", "relevance_score": 3}}
]"""

            try:
                headers = {
                    "x-api-key": self.claude_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                
                data = {
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                
                response = requests.post(
                    self.claude_base_url,
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    classifications = json.loads(result["content"][0]["text"])
                    
                    # Merge classifications with original videos
                    for video, classification in zip(batch, classifications):
                        enhanced_video = {**video, **classification}
                        enhanced_videos.append(enhanced_video)
                    
                    print(f"  Processed {len(enhanced_videos)}/{len(videos)} videos...")
                else:
                    print(f"  API error: {response.status_code}")
                    # Return unenhanced videos
                    enhanced_videos.extend(batch)
                    
            except Exception as e:
                print(f"  Error classifying batch: {e}")
                enhanced_videos.extend(batch)
        
        return enhanced_videos
    
    def filter_by_relevance(self, videos: List[Dict], min_score: int = 6) -> List[Dict]:
        """Filter videos by relevance score"""
        if not videos or 'relevance_score' not in videos[0]:
            return videos
        
        filtered = [v for v in videos if v.get('relevance_score', 0) >= min_score]
        print(f"\n✂️  Filtered: {len(videos)} → {len(filtered)} videos (min score: {min_score})")
        return filtered
    
    def save_to_csv(self, videos: List[Dict], filename: str = "vimeo_movies_ai_enhanced.csv"):
        """Save to CSV"""
        import os

        if not videos:
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

        print(f"\n✅ Saved to {output_path}")
        return output_path


def main():
    """Main execution"""

    # Load API keys from environment variables
    VIMEO_TOKEN = os.getenv("VIMEO_API_TOKEN")
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    print("=" * 70)
    print("🎬 AI-ENHANCED VIMEO MOVIE FINDER")
    print("=" * 70)
    print()

    # Check for required Vimeo token
    if not VIMEO_TOKEN:
        print("❌ Error: VIMEO_API_TOKEN not found in environment variables")
        print("📝 Please create a .env file with your API tokens")
        print("   See .env.example for the template")
        return

    # Check for Claude API key (optional but recommended)
    if not CLAUDE_API_KEY:
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment variables")
        print("   AI classification will be skipped. Add it to .env for full functionality")
        print()

    # Initialize
    finder = AIEnhancedMovieFinder(
        vimeo_token=VIMEO_TOKEN,
        claude_api_key=CLAUDE_API_KEY
    )
    
    # Search Vimeo with broader queries
    queries = [
        # Era-based
        "1920s movies",
        "1930s movies",
        "1940s movies",
        "1950s movies",
        "1960s movies",
        # Style-based
        "classic films",
        "silent movies",
        "silent films",
        "vintage cinema",
        "old movies",
        "black and white films",
        # Genre-based
        "old horror movies",
        "film noir",
        "classic western",
        "vintage comedy",
        "old sci-fi films",
        # General
        "public domain films",
        "classic hollywood",
        "golden age cinema"
    ]

    all_videos = []
    seen_urls = set()

    for query in queries:
        videos = finder.search_vimeo(query, max_results=50)
        
        for video in videos:
            if video["url"] not in seen_urls:
                all_videos.append(video)
                seen_urls.add(video["url"])
    
    print(f"\n✅ Found {len(all_videos)} unique videos from Vimeo")

    # Classify with AI
    if CLAUDE_API_KEY:
        enhanced_videos = finder.classify_with_ai(all_videos)
        
        # Filter for high relevance (lowered threshold to be more inclusive)
        filtered_videos = finder.filter_by_relevance(enhanced_videos, min_score=5)
    else:
        print("\n⚠️  Skipping AI classification (no API key)")
        filtered_videos = all_videos
    
    # Save results
    if filtered_videos:
        finder.save_to_csv(filtered_videos)
        
        # Print sample
        print("\n📋 Sample results:")
        print("-" * 70)
        for i, video in enumerate(filtered_videos[:5], 1):
            print(f"{i}. {video['title']}")
            print(f"   {video['url']}")
            if 'is_old_movie' in video:
                print(f"   Era: {video.get('estimated_era')} | Genre: {video.get('genre')} | Score: {video.get('relevance_score')}/10")
            print()
    
    print("\n💡 Tips:")
    print("   - Add your Claude API key for AI classification")
    print("   - Adjust min_score in filter_by_relevance() to change filtering")
    print("   - Modify search queries to find different types of content")


if __name__ == "__main__":
    main()
