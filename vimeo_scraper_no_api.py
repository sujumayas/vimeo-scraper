#!/usr/bin/env python3
"""
Vimeo Old Movies Scraper (No API Required)
Scrapes Vimeo search results for old movies
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from urllib.parse import urljoin, quote
from typing import List, Dict
import re

class VimeoScraper:
    def __init__(self):
        self.base_url = "https://vimeo.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_videos(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Scrape Vimeo search results
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of video dictionaries
        """
        videos = []
        page = 1
        
        print(f"🔍 Searching Vimeo for: '{query}'...")
        print("⚠️  Note: Web scraping may be limited. Consider using the API version for better results.")
        
        while len(videos) < max_results:
            try:
                # Vimeo search URL
                search_url = f"{self.base_url}/search?q={quote(query)}&page={page}"
                
                print(f"  Fetching page {page}...")
                response = requests.get(search_url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"  ⚠️  Status code {response.status_code}, stopping...")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find video links (this is approximate and may need adjustment)
                # Vimeo's structure may change, so this is a best-effort approach
                video_links = soup.find_all('a', href=re.compile(r'^/\d+'))
                
                if not video_links:
                    print(f"  No more videos found on page {page}")
                    break
                
                for link in video_links:
                    if len(videos) >= max_results:
                        break
                    
                    video_id = link.get('href', '').strip('/')
                    if video_id.isdigit() and len(video_id) > 5:
                        video_url = f"{self.base_url}/{video_id}"
                        
                        # Try to get title from the link text or nearby elements
                        title = link.get_text(strip=True) or link.get('title', '') or f"Video {video_id}"
                        
                        # Check for duplicates
                        if not any(v['url'] == video_url for v in videos):
                            videos.append({
                                "title": title,
                                "url": video_url,
                                "video_id": video_id,
                                "description": "",
                                "duration": "",
                                "views": "",
                                "user": ""
                            })
                
                print(f"  Found {len(videos)}/{max_results} videos so far...")
                
                if len(videos) >= max_results:
                    break
                
                page += 1
                time.sleep(2)  # Be respectful with scraping
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                break
        
        return videos[:max_results]
    
    def get_video_details(self, video_id: str) -> Dict:
        """
        Get detailed information about a specific video
        """
        try:
            url = f"{self.base_url}/{video_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to extract title and other info
                title_tag = soup.find('h1')
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                # Try to find description
                desc_tag = soup.find('meta', {'name': 'description'})
                description = desc_tag.get('content', '') if desc_tag else ""
                
                return {
                    "title": title,
                    "description": description
                }
        except Exception as e:
            print(f"  Error fetching details for {video_id}: {e}")
        
        return {}
    
    def search_multiple_queries(self, queries: List[str], per_query: int = 10) -> List[Dict]:
        """
        Search multiple queries and combine results
        """
        all_videos = []
        seen_urls = set()
        
        for query in queries:
            print()
            videos = self.search_videos(query, max_results=per_query)
            
            # Deduplicate
            for video in videos:
                if video["url"] not in seen_urls:
                    all_videos.append(video)
                    seen_urls.add(video["url"])
            
            time.sleep(3)  # Rate limiting
        
        return all_videos
    
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


def generate_search_queries() -> List[str]:
    """Generate diverse search queries for old movies"""
    return [
        "classic films 1920s",
        "silent movies",
        "charlie chaplin",
        "buster keaton",
        "1930s hollywood",
        "film noir",
        "classic westerns",
        "old horror movies",
        "vintage cartoons",
        "public domain films",
        "1940s cinema",
        "classic comedies",
        "old sci-fi movies",
        "vintage documentaries",
        "golden age hollywood"
    ]


def main():
    """Main execution"""
    
    print("=" * 70)
    print("🎬 VIMEO OLD MOVIES SCRAPER")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT: Web scraping is limited and may not work perfectly.")
    print("   For best results, use the API version with a free Vimeo API token.")
    print("   Get one at: https://developer.vimeo.com/apps")
    print()
    
    scraper = VimeoScraper()
    
    # Generate search queries
    queries = generate_search_queries()
    
    print(f"🔍 Will search {len(queries)} different queries...")
    print(f"   Targeting ~50 total unique videos")
    print()
    
    # Search (adjust per_query to control results per search term)
    videos = scraper.search_multiple_queries(queries[:10], per_query=5)
    
    if videos:
        print()
        print("=" * 70)
        print(f"✅ Found {len(videos)} unique videos!")
        print()
        
        # Save to CSV
        csv_path = scraper.save_to_csv(videos, "vimeo_old_movies_scraped.csv")
        
        # Print sample
        print()
        print("📋 Sample results:")
        print("-" * 70)
        for i, video in enumerate(videos[:10], 1):
            print(f"{i}. {video['title'][:60]}")
            print(f"   {video['url']}")
            print()
    else:
        print("❌ No videos found.")
        print("   Try using the API version instead (vimeo_old_movies_finder.py)")


if __name__ == "__main__":
    main()
