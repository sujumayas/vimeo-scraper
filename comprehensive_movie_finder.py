#!/usr/bin/env python3
"""
Comprehensive Classic Movie Finder
===================================
AI-first pipeline combining Vimeo API, Claude AI, and TMDb API to find
genuine feature-length classic movies from before 1965.

Pipeline stages:
1. Vimeo Search - Enhanced metadata extraction with duration filtering
2. Keyword Pre-filter - Quick elimination of obvious non-movies
3. AI Stage 1 - Content type detection (MOVIE vs TRAILER vs REVIEW, etc.)
4. AI Stage 2 - Feature film verification
5. AI Stage 3 - Era and studio authentication
6. TMDb Verification - Cross-reference with official movie database
7. Scoring & Ranking - Combine all signals into confidence score
8. Export - Save verified classic movies to CSV/JSON
"""

import os
import csv
import json
import time
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

# Import our custom modules
from vimeo_old_movies_finder import VimeoMovieFinder
from ai_powered_movie_verifier import AIMovieVerifier
from tmdb_verifier import TMDbVerifier


class ComprehensiveMovieFinder:
    """
    Comprehensive pipeline for finding authentic classic movies.
    """

    # Keywords that indicate non-movie content
    BLACKLIST_KEYWORDS = [
        "trailer", "teaser", "promo", "preview", "clip",
        "behind the scenes", "making of", "breakdown", "VFX",
        "test", "demo", "reel", "showreel", "recap",
        "review", "analysis", "essay", "critique",
        "supercut", "compilation", "montage", "tribute",
        "how to", "tutorial", "lesson", "workshop",
        "interview", "Q&A", "panel", "discussion",
        "opener", "bumper", "ident", "logo", "intro",
        "campaign", "ad", "commercial", "spot"
    ]

    # Enhanced search queries targeting known classics and eras
    SEARCH_QUERIES = [
        # Known classic films
        "Casablanca 1942",
        "Citizen Kane 1941",
        "Metropolis 1927",
        "Nosferatu 1922",
        "The Cabinet of Dr Caligari",
        "The General Buster Keaton",
        "Modern Times Chaplin",
        "City Lights Chaplin",
        "The 39 Steps Hitchcock",
        "The Maltese Falcon",
        "Double Indemnity",
        "Sunset Boulevard",
        "The Third Man",

        # Era + genre combinations
        "1920s silent feature film",
        "1930s classic film noir",
        "1940s hollywood classic",
        "1950s feature film",
        "pre-code hollywood 1930s",
        "golden age cinema 1940s",
        "classic westerns 1950s",
        "vintage horror 1930s",

        # Director searches
        "Hitchcock classic film",
        "Chaplin feature film",
        "Orson Welles film",
        "Fritz Lang film",
        "John Ford western",
        "Frank Capra film",

        # Public domain indicators
        "public domain feature film",
        "copyright free classic movie",
        "classic cinema full movie"
    ]

    def __init__(
        self,
        vimeo_token: str,
        claude_api_key: str,
        tmdb_api_key: str
    ):
        """
        Initialize comprehensive finder with all API credentials.

        Args:
            vimeo_token: Vimeo API token
            claude_api_key: Anthropic Claude API key
            tmdb_api_key: The Movie Database API key
        """
        self.vimeo_finder = VimeoMovieFinder(vimeo_token)
        self.ai_verifier = AIMovieVerifier(claude_api_key)
        self.tmdb_verifier = TMDbVerifier(tmdb_api_key)

        self.config = {
            "min_duration": 45 * 60,  # 45 minutes in seconds
            "max_duration": 180 * 60,  # 3 hours in seconds
            "per_query_results": 5,  # Results per search query
            "min_tmdb_confidence": 70,  # Minimum TMDb confidence score
            "min_ai_quality": 6,  # Minimum AI quality score (1-10)
        }

    def stage1_vimeo_search(self, queries: List[str] = None) -> List[Dict]:
        """
        Stage 1: Search Vimeo with enhanced metadata extraction.

        Args:
            queries: Custom search queries (uses defaults if None)

        Returns:
            List of videos with full metadata
        """
        if queries is None:
            queries = self.SEARCH_QUERIES

        print(f"\n{'='*70}")
        print("🔍 STAGE 1: VIMEO SEARCH")
        print(f"{'='*70}")
        print(f"Searching {len(queries)} queries...")
        print(f"Duration filter: {self.config['min_duration']//60}-{self.config['max_duration']//60} minutes")

        all_videos = []
        seen_urls = set()

        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Query: '{query}'")

            videos = self.vimeo_finder.search_videos(
                query,
                per_page=self.config["per_query_results"],
                max_results=self.config["per_query_results"]
            )

            # Deduplicate and apply duration filter
            for video in videos:
                url = video["url"]
                duration = video["duration"]

                # Duration filter
                if duration < self.config["min_duration"]:
                    continue
                if duration > self.config["max_duration"]:
                    continue

                # Deduplicate
                if url not in seen_urls:
                    all_videos.append(video)
                    seen_urls.add(url)

            time.sleep(1)  # Rate limiting

        print(f"\n{'='*70}")
        print(f"✅ Found {len(all_videos)} videos (after duration filtering + deduplication)")
        print(f"{'='*70}")

        return all_videos

    def stage2_keyword_prefilter(self, videos: List[Dict]) -> List[Dict]:
        """
        Stage 2: Quick keyword-based filtering to eliminate obvious non-movies.

        Args:
            videos: Videos from Stage 1

        Returns:
            Filtered videos
        """
        print(f"\n{'='*70}")
        print("🔎 STAGE 2: KEYWORD PRE-FILTER")
        print(f"{'='*70}")

        filtered = []

        for video in videos:
            title = video.get("title", "").lower()
            description = video.get("description", "").lower()
            tags = [t.lower() for t in video.get("tags", [])]

            # Check for blacklisted keywords
            has_blacklist = False
            matched_keyword = None

            for keyword in self.BLACKLIST_KEYWORDS:
                if keyword in title or keyword in description or keyword in " ".join(tags):
                    has_blacklist = True
                    matched_keyword = keyword
                    break

            if has_blacklist:
                print(f"  ❌ Filtered: '{video['title'][:60]}' (contains '{matched_keyword}')")
            else:
                filtered.append(video)

        print(f"\n{'='*70}")
        print(f"✅ Passed: {len(filtered)}/{len(videos)} videos")
        print(f"   Filtered out {len(videos) - len(filtered)} videos with blacklist keywords")
        print(f"{'='*70}")

        return filtered

    def stage3_ai_classification(self, videos: List[Dict]) -> List[Dict]:
        """
        Stage 3: Three-stage AI classification pipeline.

        Args:
            videos: Videos from Stage 2

        Returns:
            AI-verified classic movies
        """
        print(f"\n{'='*70}")
        print("🤖 STAGE 3: AI CLASSIFICATION (3 sub-stages)")
        print(f"{'='*70}")

        verified_movies = self.ai_verifier.verify_full_pipeline(videos)

        return verified_movies

    def stage4_tmdb_verification(self, videos: List[Dict]) -> List[Dict]:
        """
        Stage 4: Cross-reference with TMDb for final verification.

        Args:
            videos: AI-verified movies from Stage 3

        Returns:
            TMDb-verified movies with confidence scores
        """
        print(f"\n{'='*70}")
        print("🎬 STAGE 4: TMDB VERIFICATION")
        print(f"{'='*70}")

        verified_movies = self.tmdb_verifier.batch_verify(
            videos,
            delay=0.3
        )

        # Filter by TMDb confidence threshold
        high_confidence = [
            v for v in verified_movies
            if v.get("tmdb_verification", {}).get("confidence", 0) >= self.config["min_tmdb_confidence"]
        ]

        print(f"\n{'='*70}")
        print(f"✅ High confidence matches: {len(high_confidence)}/{len(videos)}")
        print(f"   (TMDb confidence >= {self.config['min_tmdb_confidence']}%)")
        print(f"{'='*70}")

        return high_confidence

    def stage5_scoring_ranking(self, videos: List[Dict]) -> List[Dict]:
        """
        Stage 5: Calculate final confidence scores and rank results.

        Combines:
        - AI quality score
        - TMDb confidence
        - Duration appropriateness
        - View count (popularity signal)
        - Tags/metadata quality

        Args:
            videos: TMDb-verified movies

        Returns:
            Ranked movies with final_score field
        """
        print(f"\n{'='*70}")
        print("📊 STAGE 5: SCORING & RANKING")
        print(f"{'='*70}")

        for video in videos:
            score = 0.0

            # AI quality score (0-40 points)
            ai_quality = video.get("quality_score", 0)
            score += (ai_quality / 10) * 40

            # TMDb confidence (0-30 points)
            tmdb_confidence = video.get("tmdb_verification", {}).get("confidence", 0)
            score += (tmdb_confidence / 100) * 30

            # Duration appropriateness (0-10 points)
            duration_min = (video.get("duration") or 0) / 60
            if 70 <= duration_min <= 120:  # Sweet spot for classic films
                score += 10
            elif 60 <= duration_min <= 150:
                score += 7
            elif 45 <= duration_min <= 180:
                score += 4

            # View count - popularity signal (0-10 points)
            views = video.get("views") or 0  # Handle None values
            if views >= 100000:
                score += 10
            elif views >= 50000:
                score += 7
            elif views >= 10000:
                score += 5
            elif views >= 1000:
                score += 3

            # TMDb verified status bonus (0-10 points)
            if video.get("tmdb_verification", {}).get("verified"):
                score += 10

            video["final_score"] = round(score, 1)

        # Sort by final score (descending)
        videos.sort(key=lambda v: v["final_score"], reverse=True)

        print(f"✅ Scored and ranked {len(videos)} movies")
        print(f"\nTop 5 movies by confidence:")
        for i, v in enumerate(videos[:5], 1):
            print(f"  {i}. {v['title'][:50]} - Score: {v['final_score']}/100")

        print(f"\n{'='*70}")

        return videos

    def stage6_export(
        self,
        videos: List[Dict],
        output_dir: str = "./outputs"
    ) -> None:
        """
        Stage 6: Export verified movies to CSV and JSON.

        Args:
            videos: Ranked and scored movies
            output_dir: Output directory path
        """
        print(f"\n{'='*70}")
        print("💾 STAGE 6: EXPORT RESULTS")
        print(f"{'='*70}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(output_dir, f"verified_classic_movies_{timestamp}.csv")
        json_path = os.path.join(output_dir, f"verified_classic_movies_{timestamp}.json")

        # Prepare flattened data for CSV
        csv_rows = []
        for video in videos:
            tmdb = video.get("tmdb_verification", {})

            row = {
                # Basic info
                "title": video.get("title", ""),
                "url": video.get("url", ""),
                "duration_minutes": round((video.get("duration") or 0) / 60),
                "duration_formatted": video.get("duration_formatted", ""),

                # AI classification
                "estimated_production_year": video.get("estimated_production_year"),
                "estimated_era": video.get("estimated_era", ""),
                "genre": video.get("genre", ""),
                "production_company": video.get("production_company", ""),
                "is_formal_studio": video.get("is_formal_studio", False),
                "ai_quality_score": video.get("quality_score", 0),

                # TMDb verification
                "tmdb_verified": tmdb.get("verified", False),
                "tmdb_id": tmdb.get("tmdb_id"),
                "tmdb_title": tmdb.get("tmdb_title", ""),
                "tmdb_release_year": tmdb.get("release_year"),
                "tmdb_runtime_minutes": tmdb.get("runtime_minutes"),
                "tmdb_studios": ", ".join(tmdb.get("production_companies", [])),
                "tmdb_confidence": tmdb.get("confidence", 0),

                # Metadata
                "views": video.get("views") or 0,
                "likes": video.get("likes") or 0,
                "comments": video.get("comments") or 0,
                "created_date": video.get("created_date", ""),
                "user": video.get("user", ""),
                "user_url": video.get("user_url", ""),
                "tags": ", ".join(video.get("tags", [])),
                "categories": ", ".join(video.get("categories", [])),

                # Scoring
                "final_score": video.get("final_score", 0),

                # Descriptions
                "description": video.get("description", "")[:500],  # Limit for CSV
            }

            csv_rows.append(row)

        # Write CSV
        if csv_rows:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
                writer.writeheader()
                writer.writerows(csv_rows)

            print(f"✅ Saved CSV: {csv_path}")

        # Write JSON (full data)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved JSON: {json_path}")

        print(f"\n{'='*70}")
        print(f"📈 FINAL STATISTICS")
        print(f"{'='*70}")
        print(f"Total verified classic movies: {len(videos)}")

        # Era breakdown
        era_counts = {}
        for v in videos:
            era = v.get("estimated_era", "unknown")
            era_counts[era] = era_counts.get(era, 0) + 1

        print(f"\nMovies by era:")
        for era, count in sorted(era_counts.items()):
            print(f"  {era}: {count} movies")

        # TMDb verification rate
        tmdb_verified = sum(1 for v in videos if v.get("tmdb_verification", {}).get("verified"))
        print(f"\nTMDb verification rate: {tmdb_verified}/{len(videos)} ({tmdb_verified/len(videos)*100:.1f}%)")

        # Average scores
        avg_final = sum(v.get("final_score", 0) for v in videos) / len(videos) if videos else 0
        avg_ai = sum(v.get("quality_score", 0) for v in videos) / len(videos) if videos else 0

        print(f"\nAverage final score: {avg_final:.1f}/100")
        print(f"Average AI quality: {avg_ai:.1f}/10")

        print(f"\n{'='*70}")

    def run_full_pipeline(
        self,
        queries: List[str] = None,
        output_dir: str = "./outputs"
    ) -> List[Dict]:
        """
        Run the complete comprehensive movie finding pipeline.

        Args:
            queries: Custom search queries (optional)
            output_dir: Where to save results

        Returns:
            List of verified classic movies
        """
        start_time = time.time()

        print("\n")
        print("=" * 70)
        print("🎬 COMPREHENSIVE CLASSIC MOVIE FINDER")
        print("=" * 70)
        print("AI-First Pipeline for Authentic Pre-1965 Feature Films")
        print("=" * 70)
        print(f"\nConfiguration:")
        print(f"  Duration range: {self.config['min_duration']//60}-{self.config['max_duration']//60} minutes")
        print(f"  Results per query: {self.config['per_query_results']}")
        print(f"  Min TMDb confidence: {self.config['min_tmdb_confidence']}%")
        print(f"  Min AI quality: {self.config['min_ai_quality']}/10")
        print()

        # Stage 1: Vimeo Search
        videos = self.stage1_vimeo_search(queries)

        if not videos:
            print("\n❌ No videos found in Stage 1. Exiting.")
            return []

        # Stage 2: Keyword Pre-filter
        videos = self.stage2_keyword_prefilter(videos)

        if not videos:
            print("\n❌ No videos passed Stage 2. Exiting.")
            return []

        # Stage 3: AI Classification (3 sub-stages)
        videos = self.stage3_ai_classification(videos)

        if not videos:
            print("\n❌ No videos passed Stage 3 (AI). Exiting.")
            return []

        # Stage 4: TMDb Verification
        videos = self.stage4_tmdb_verification(videos)

        if not videos:
            print("\n❌ No videos passed Stage 4 (TMDb). Exiting.")
            return []

        # Stage 5: Scoring & Ranking
        videos = self.stage5_scoring_ranking(videos)

        # Stage 6: Export
        self.stage6_export(videos, output_dir)

        elapsed = time.time() - start_time
        print(f"\n⏱️  Total pipeline time: {elapsed/60:.1f} minutes")
        print(f"✅ Pipeline complete! Found {len(videos)} verified classic movies.\n")

        return videos


def main():
    """Main entry point."""
    load_dotenv()

    # Load API keys
    vimeo_token = os.getenv("VIMEO_API_TOKEN")
    claude_api_key = os.getenv("ANTHROPIC_API_KEY")
    tmdb_api_key = os.getenv("TMDB_API_KEY")

    # Check for required API keys
    missing = []
    if not vimeo_token:
        missing.append("VIMEO_API_TOKEN")
    if not claude_api_key:
        missing.append("ANTHROPIC_API_KEY")
    if not tmdb_api_key:
        missing.append("TMDB_API_KEY")

    if missing:
        print("❌ Error: Missing required API keys in .env file:")
        for key in missing:
            print(f"   - {key}")
        print("\nPlease add these keys to your .env file.")
        print("See .env.example for reference.")
        return

    # Initialize finder
    finder = ComprehensiveMovieFinder(
        vimeo_token=vimeo_token,
        claude_api_key=claude_api_key,
        tmdb_api_key=tmdb_api_key
    )

    # Run pipeline
    verified_movies = finder.run_full_pipeline()

    if verified_movies:
        print("\n🎉 Success! Check the ./outputs directory for results.")
    else:
        print("\n⚠️  No movies found. Try adjusting search queries or filters.")


if __name__ == "__main__":
    main()
