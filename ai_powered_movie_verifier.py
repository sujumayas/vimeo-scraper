"""
AI-Powered Movie Verifier
==========================
Multi-stage AI classification system using Claude to identify genuine
feature-length classic movies and filter out trailers, promos, and reviews.

Three-stage pipeline:
1. Content Type Detection - Identify if video is a movie, trailer, review, etc.
2. Feature Film Analysis - Verify it's a genuine narrative feature film
3. Era & Studio Verification - Confirm production era and studio authenticity
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime


class AIMovieVerifier:
    """Multi-stage AI classifier for authentic movie verification."""

    def __init__(self, api_key: str):
        """
        Initialize AI movie verifier.

        Args:
            api_key: Anthropic Claude API key
        """
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"

    def _call_claude(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """
        Make a call to Claude API.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens for response

        Returns:
            Response text or None if error
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            return result["content"][0]["text"]

        except requests.exceptions.RequestException as e:
            print(f"❌ Claude API error: {e}")
            return None

    def stage1_content_type_detection(
        self,
        videos: List[Dict],
        batch_size: int = 10
    ) -> List[Dict]:
        """
        Stage 1: Detect content type (movie, trailer, review, promo, etc.).

        Args:
            videos: List of video dicts with title, description, duration, tags
            batch_size: Number of videos to process per API call

        Returns:
            Videos with added fields:
            - content_type: MOVIE, TRAILER, REVIEW, PROMO, TEST, ESSAY, OTHER
            - content_confidence: 0.0-1.0 confidence score
            - content_reasoning: Brief explanation
        """
        print(f"\n🎬 Stage 1: Content Type Detection ({len(videos)} videos)")
        print("=" * 70)

        enhanced_videos = []

        for i in range(0, len(videos), batch_size):
            batch = videos[i:i + batch_size]

            # Prepare video info with rich metadata
            video_info = []
            for v in batch:
                info = {
                    "title": v.get("title", ""),
                    "description": v.get("description", "")[:500],  # More context
                    "duration_minutes": round(v.get("duration", 0) / 60, 1),
                    "tags": v.get("tags", []),
                    "user": v.get("user", ""),
                    "views": v.get("views", 0)
                }
                video_info.append(info)

            prompt = f"""Analyze these videos and classify their content type.

For each video, determine:
1. content_type: Choose ONE from: MOVIE, TRAILER, REVIEW, PROMO, TEST, ESSAY, OTHER
   - MOVIE: Full-length feature film (narrative story, 45+ minutes)
   - TRAILER: Preview/teaser for a movie (typically 1-5 minutes)
   - REVIEW: Analysis, critique, or discussion about movies
   - PROMO: Promotional content (channel IDs, network promos, ads)
   - TEST: Technical tests (camera, lens, VFX breakdowns)
   - ESSAY: Video essays about film/cinema
   - OTHER: Doesn't fit above categories

2. content_confidence: Float 0.0-1.0 (how certain are you?)

3. content_reasoning: 1-2 sentence explanation of your classification

Red flags for NON-MOVIES:
- Titles with: "trailer", "promo", "review", "breakdown", "test", "essay", "recap"
- Very short duration (< 20 minutes) suggests trailer/promo
- Descriptions mentioning: "client:", "agency:", "director:", "shot on", "VFX"
- Channel names for networks/studios suggest promos

Green flags for MOVIES:
- Duration 45-180 minutes
- Plot/story elements in description
- Character names mentioned
- Classic movie vocabulary: "starring", "directed by", "film noir", "drama"

Videos:
{json.dumps(video_info, indent=2)}

Respond with ONLY a valid JSON array of objects in the same order as input:
[
  {{"content_type": "MOVIE", "content_confidence": 0.85, "content_reasoning": "Feature-length drama with plot summary"}},
  {{"content_type": "TRAILER", "content_confidence": 0.95, "content_reasoning": "2-minute duration, title contains 'trailer'"}}
]"""

            response_text = self._call_claude(prompt)

            if response_text:
                try:
                    # Parse JSON response
                    classifications = json.loads(response_text)

                    # Merge with original videos
                    for video, classification in zip(batch, classifications):
                        video.update(classification)
                        enhanced_videos.append(video)

                    print(f"  ✅ Processed {len(enhanced_videos)}/{len(videos)} videos")

                except json.JSONDecodeError as e:
                    print(f"  ⚠️  JSON parse error: {e}")
                    enhanced_videos.extend(batch)
            else:
                print(f"  ⚠️  API call failed, keeping batch unclassified")
                enhanced_videos.extend(batch)

            # Rate limiting
            time.sleep(1)

        # Filter: Keep only MOVIE content type with confidence > 0.7
        movies_only = [
            v for v in enhanced_videos
            if v.get("content_type") == "MOVIE"
            and v.get("content_confidence", 0) > 0.7
        ]

        print(f"\n  📊 Results: {len(movies_only)}/{len(videos)} classified as MOVIE")
        print(f"     Filtered out {len(videos) - len(movies_only)}: trailers, promos, reviews, etc.")

        return movies_only

    def stage2_feature_film_analysis(
        self,
        videos: List[Dict],
        batch_size: int = 8
    ) -> List[Dict]:
        """
        Stage 2: Verify videos are genuine feature-length narrative films.

        Args:
            videos: Videos that passed Stage 1 (classified as MOVIE)
            batch_size: Number of videos to process per API call

        Returns:
            Videos with added fields:
            - is_feature_film: bool - Genuine narrative feature film
            - has_narrative: bool - Contains story/plot elements
            - narrative_confidence: 0.0-1.0
            - film_reasoning: Detailed explanation
        """
        print(f"\n🎭 Stage 2: Feature Film Analysis ({len(videos)} videos)")
        print("=" * 70)

        enhanced_videos = []

        for i in range(0, len(videos), batch_size):
            batch = videos[i:i + batch_size]

            video_info = []
            for v in batch:
                info = {
                    "title": v.get("title", ""),
                    "description": v.get("description", "")[:800],  # Full description
                    "duration_minutes": round(v.get("duration", 0) / 60, 1),
                    "content_reasoning": v.get("content_reasoning", ""),
                    "tags": v.get("tags", [])[:10],
                    "user": v.get("user", "")
                }
                video_info.append(info)

            prompt = f"""These videos were classified as "MOVIE" in initial screening.
Now verify if they are genuine FEATURE-LENGTH NARRATIVE FILMS.

For each video, determine:
1. is_feature_film: true/false
   - TRUE if: Narrative story, character-driven, 40+ minutes, theatrical release quality
   - FALSE if: Documentary about films, compilation, short film (<40 min), music video

2. has_narrative: true/false
   - Does it tell a story with characters and plot?
   - Or is it experimental/abstract/documentary?

3. narrative_confidence: Float 0.0-1.0

4. film_reasoning: 2-3 sentence explanation with specific evidence

Look for POSITIVE indicators:
- Plot summary or story synopsis in description
- Character names (not just actor names)
- Genre keywords: drama, comedy, thriller, western, noir, horror, sci-fi
- Duration 40-180 minutes
- "Starring", "directed by", "screenplay", "based on"
- Film festival mentions, theatrical release info

Look for NEGATIVE indicators:
- "Documentary about...", "The story of how...", "Behind the scenes"
- "Supercut", "compilation", "collection", "montage", "tribute"
- Very short (<40 min) or very long (>200 min) duration
- "Music video", "concert film", "performance"
- Educational/instructional content
- Modern YouTube/Vimeo creator style descriptions

Videos:
{json.dumps(video_info, indent=2)}

Respond with ONLY valid JSON array:
[
  {{"is_feature_film": true, "has_narrative": true, "narrative_confidence": 0.9, "film_reasoning": "Classic noir with plot synopsis mentioning detective protagonist and murder mystery. 87-minute runtime is standard feature length."}},
  {{"is_feature_film": false, "has_narrative": false, "narrative_confidence": 0.3, "film_reasoning": "Description says 'documentary about classic horror films' - this is a film ABOUT movies, not a movie itself."}}
]"""

            response_text = self._call_claude(prompt)

            if response_text:
                try:
                    classifications = json.loads(response_text)

                    for video, classification in zip(batch, classifications):
                        video.update(classification)
                        enhanced_videos.append(video)

                    print(f"  ✅ Analyzed {len(enhanced_videos)}/{len(videos)} videos")

                except json.JSONDecodeError as e:
                    print(f"  ⚠️  JSON parse error: {e}")
                    enhanced_videos.extend(batch)
            else:
                print(f"  ⚠️  API call failed")
                enhanced_videos.extend(batch)

            time.sleep(1)

        # Filter: Keep only genuine feature films
        feature_films = [
            v for v in enhanced_videos
            if v.get("is_feature_film") == True
            and v.get("narrative_confidence", 0) > 0.6
        ]

        print(f"\n  📊 Results: {len(feature_films)}/{len(videos)} verified as feature films")
        print(f"     Filtered out {len(videos) - len(feature_films)}: documentaries, compilations, shorts")

        return feature_films

    def stage3_era_studio_verification(
        self,
        videos: List[Dict],
        batch_size: int = 8
    ) -> List[Dict]:
        """
        Stage 3: Verify production era and studio authenticity.

        Args:
            videos: Videos that passed Stage 2 (verified feature films)
            batch_size: Number of videos to process per API call

        Returns:
            Videos with added fields:
            - estimated_production_year: int or None
            - estimated_era: str (e.g., "1940s", "1950s", "modern")
            - is_pre_1965: bool
            - production_company: str or None
            - is_formal_studio: bool
            - genre: str (primary genre)
            - quality_score: int 1-10 (overall quality/relevance)
            - era_reasoning: Explanation
        """
        print(f"\n🎥 Stage 3: Era & Studio Verification ({len(videos)} videos)")
        print("=" * 70)

        enhanced_videos = []

        for i in range(0, len(videos), batch_size):
            batch = videos[i:i + batch_size]

            video_info = []
            for v in batch:
                info = {
                    "title": v.get("title", ""),
                    "description": v.get("description", "")[:800],
                    "duration_minutes": round(v.get("duration", 0) / 60, 1),
                    "created_date": v.get("created_date", "")[:10],  # Upload date
                    "user": v.get("user", ""),
                    "film_reasoning": v.get("film_reasoning", "")
                }
                video_info.append(info)

            prompt = f"""These are verified feature-length narrative films.
Determine their production era and studio authenticity.

For each video, determine:

1. estimated_production_year: Best guess of PRODUCTION year (not upload date!)
   - Analyze title, description for year clues
   - Look for decade indicators: "1940s classic", "pre-code", "silent era"
   - Actor/director names can indicate era
   - Return null if truly uncertain

2. estimated_era: Decade string
   - "1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s"
   - "1970s", "1980s", "modern" (1990+)

3. is_pre_1965: true/false
   - Conservative estimate - only true if confident it's pre-1965

4. production_company: Studio/production company name or null
   - Extract from description or title
   - Classic studios: MGM, Paramount, Warner Bros, Universal, RKO, 20th Century Fox, Columbia, United Artists
   - Independent studios also valid

5. is_formal_studio: true/false
   - TRUE if produced by recognized studio (major or established independent)
   - FALSE if amateur, modern indie, or uncertain

6. genre: Primary genre
   - drama, comedy, thriller, horror, western, noir, sci-fi, romance, war, crime, musical

7. quality_score: Integer 1-10
   - How confident are you this is a genuine classic movie worth watching?
   - Consider: era authenticity, studio legitimacy, genre clarity
   - 8-10: Highly confident classic
   - 5-7: Probable classic, some uncertainty
   - 1-4: Uncertain or likely not a true classic

8. era_reasoning: 2-3 sentences explaining your era/studio determination

Evidence to look for:
- Year in title: "Nosferatu (1922)", "The 39 Steps 1935"
- Era descriptors: "silent film", "pre-code", "golden age", "classic hollywood"
- Known classic titles: Casablanca, Citizen Kane, Metropolis, etc.
- Actor names: Chaplin, Bogart, Hepburn, Grant indicate classic era
- Director names: Hitchcock, Hawks, Ford, Lang, Welles
- Studio mentions in description
- "Public domain", "copyright expired" suggests pre-1965

Be CONSERVATIVE with is_pre_1965 - only mark true if you have good evidence.

Videos:
{json.dumps(video_info, indent=2)}

Respond with ONLY valid JSON array:
[
  {{
    "estimated_production_year": 1942,
    "estimated_era": "1940s",
    "is_pre_1965": true,
    "production_company": "Warner Bros.",
    "is_formal_studio": true,
    "genre": "drama",
    "quality_score": 9,
    "era_reasoning": "Title mentions Humphrey Bogart and Ingrid Bergman, iconic 1940s stars. Description references Warner Bros and wartime setting. Almost certainly Casablanca (1942)."
  }}
]"""

            response_text = self._call_claude(prompt, max_tokens=4000)

            if response_text:
                try:
                    classifications = json.loads(response_text)

                    for video, classification in zip(batch, classifications):
                        video.update(classification)
                        enhanced_videos.append(video)

                    print(f"  ✅ Verified {len(enhanced_videos)}/{len(videos)} videos")

                except json.JSONDecodeError as e:
                    print(f"  ⚠️  JSON parse error: {e}")
                    enhanced_videos.extend(batch)
            else:
                print(f"  ⚠️  API call failed")
                enhanced_videos.extend(batch)

            time.sleep(1)

        # Filter: Keep only pre-1965 films with quality score >= 6
        classic_films = [
            v for v in enhanced_videos
            if v.get("is_pre_1965") == True
            and v.get("quality_score", 0) >= 6
        ]

        print(f"\n  📊 Results: {len(classic_films)}/{len(videos)} verified as pre-1965 classics")
        print(f"     Filtered out {len(videos) - len(classic_films)}: modern films, uncertain era")

        # Show era distribution
        era_counts = {}
        for v in classic_films:
            era = v.get("estimated_era", "unknown")
            era_counts[era] = era_counts.get(era, 0) + 1

        print(f"\n  📅 Era distribution:")
        for era, count in sorted(era_counts.items()):
            print(f"     {era}: {count} films")

        return classic_films

    def verify_full_pipeline(
        self,
        videos: List[Dict],
        skip_stage1: bool = False,
        skip_stage2: bool = False
    ) -> List[Dict]:
        """
        Run complete three-stage verification pipeline.

        Args:
            videos: Raw videos from Vimeo
            skip_stage1: Skip content type detection (use if already filtered)
            skip_stage2: Skip feature film analysis (use if already verified)

        Returns:
            Fully verified classic movies
        """
        print(f"\n{'='*70}")
        print("🤖 AI-POWERED MOVIE VERIFICATION PIPELINE")
        print(f"{'='*70}")
        print(f"Starting with {len(videos)} videos...\n")

        results = videos

        if not skip_stage1:
            results = self.stage1_content_type_detection(results)
            if not results:
                print("\n❌ No videos passed Stage 1 (Content Type Detection)")
                return []

        if not skip_stage2:
            results = self.stage2_feature_film_analysis(results)
            if not results:
                print("\n❌ No videos passed Stage 2 (Feature Film Analysis)")
                return []

        results = self.stage3_era_studio_verification(results)

        print(f"\n{'='*70}")
        print(f"✅ PIPELINE COMPLETE")
        print(f"{'='*70}")
        print(f"Final results: {len(results)} verified classic movies")
        print(f"Success rate: {len(results)}/{len(videos)} ({len(results)/len(videos)*100:.1f}%)")

        return results


def main():
    """Test the AI movie verifier."""
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        return

    verifier = AIMovieVerifier(api_key)

    # Test cases with various content types
    test_videos = [
        {
            "title": "Casablanca (1942) - Full Movie",
            "description": "Humphrey Bogart and Ingrid Bergman star in this Warner Bros. classic romantic drama set in wartime Morocco.",
            "duration": 6120,  # 102 minutes
            "tags": ["classic", "drama", "1940s"],
            "user": "Classic Films Archive",
            "views": 150000
        },
        {
            "title": "Casablanca - Official Trailer (1942)",
            "description": "Theatrical trailer for the classic film starring Bogart",
            "duration": 150,  # 2.5 minutes
            "tags": ["trailer"],
            "user": "Warner Bros",
            "views": 50000
        },
        {
            "title": "The History of Film Noir",
            "description": "A documentary exploring the classic noir genre",
            "duration": 3600,  # 60 minutes
            "tags": ["documentary", "film noir"],
            "user": "Film Essays",
            "views": 25000
        },
        {
            "title": "Metropolis (1927) - Fritz Lang",
            "description": "Silent science fiction masterpiece from German expressionist cinema. Directed by Fritz Lang.",
            "duration": 9300,  # 155 minutes
            "tags": ["silent film", "1920s", "sci-fi"],
            "user": "Silent Cinema Collection",
            "views": 200000
        }
    ]

    print("🎬 Testing AI Movie Verifier - Three Stage Pipeline\n")

    verified_movies = verifier.verify_full_pipeline(test_videos)

    print("\n" + "=" * 70)
    print("VERIFIED MOVIES:")
    print("=" * 70)

    for movie in verified_movies:
        print(f"\n📽️  {movie['title']}")
        print(f"   Era: {movie.get('estimated_era')} ({movie.get('estimated_production_year', 'unknown')})")
        print(f"   Studio: {movie.get('production_company', 'Unknown')}")
        print(f"   Genre: {movie.get('genre', 'Unknown')}")
        print(f"   Quality Score: {movie.get('quality_score')}/10")
        print(f"   Duration: {round(movie['duration']/60)} minutes")


if __name__ == "__main__":
    main()
