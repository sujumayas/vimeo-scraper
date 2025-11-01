"""
TMDb Movie Verifier
===================
Cross-references Vimeo videos with The Movie Database (TMDb) to verify
authenticity of classic movies.

Uses TMDb API v3 to:
- Search for movies by title
- Verify release dates (pre-1965 for public domain)
- Confirm production studios
- Match runtime with Vimeo duration
"""

import os
import requests
import time
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from datetime import datetime


class TMDbVerifier:
    """Verifies movie authenticity using The Movie Database API."""

    # Classic Hollywood studios and major independent studios
    CLASSIC_STUDIOS = {
        "Metro-Goldwyn-Mayer", "MGM", "Paramount", "Paramount Pictures",
        "Warner Bros.", "Warner Brothers", "Universal", "Universal Pictures",
        "20th Century Fox", "20th Century-Fox", "Twentieth Century Fox",
        "RKO", "RKO Radio Pictures", "Columbia Pictures", "Columbia",
        "United Artists", "Republic Pictures", "Monogram Pictures",
        "Allied Artists", "American International Pictures", "AIP",
        "Selznick International Pictures", "The Criterion Collection",
        "British Film Institute", "Ealing Studios", "Hammer Film Productions",
        "Pathé", "Gaumont", "UFA", "Mosfilm", "Toho"
    }

    def __init__(self, api_key: str):
        """
        Initialize TMDb verifier.

        Args:
            api_key: TMDb API key (v3) or bearer token (v4)
        """
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

        # Determine if using bearer token or API key
        if api_key.startswith("eyJ"):  # JWT token format
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            self.use_bearer = True
        else:
            self.headers = {}
            self.use_bearer = False

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_movie(self, title: str, year: Optional[int] = None) -> List[Dict]:
        """
        Search for a movie by title in TMDb.

        Args:
            title: Movie title to search
            year: Optional release year to narrow results

        Returns:
            List of matching movies with metadata
        """
        endpoint = f"{self.base_url}/search/movie"

        params = {
            "query": title,
            "include_adult": False
        }

        if not self.use_bearer:
            params["api_key"] = self.api_key

        if year:
            params["year"] = year

        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get("results", [])

        except requests.exceptions.RequestException as e:
            print(f"❌ TMDb search error for '{title}': {e}")
            return []

    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get detailed information about a movie.

        Args:
            tmdb_id: TMDb movie ID

        Returns:
            Movie details including runtime, production companies, etc.
        """
        endpoint = f"{self.base_url}/movie/{tmdb_id}"

        params = {}
        if not self.use_bearer:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ TMDb details error for ID {tmdb_id}: {e}")
            return None

    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two titles (0.0 to 1.0).

        Args:
            title1: First title
            title2: Second title

        Returns:
            Similarity ratio (0.0 = completely different, 1.0 = identical)
        """
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        # Remove common prefixes/suffixes
        for prefix in ["the ", "a ", "an "]:
            if t1.startswith(prefix):
                t1 = t1[len(prefix):]
            if t2.startswith(prefix):
                t2 = t2[len(prefix):]

        return SequenceMatcher(None, t1, t2).ratio()

    def is_classic_studio(self, production_companies: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Check if movie was produced by a classic/formal studio.

        Args:
            production_companies: List of production company dicts from TMDb

        Returns:
            Tuple of (is_classic, list of matching studio names)
        """
        matching_studios = []

        for company in production_companies:
            company_name = company.get("name", "")

            # Check against our classic studios list
            for classic_studio in self.CLASSIC_STUDIOS:
                if classic_studio.lower() in company_name.lower():
                    matching_studios.append(company_name)
                    break

        return len(matching_studios) > 0, matching_studios

    def verify_movie(
        self,
        vimeo_title: str,
        vimeo_duration_seconds: int,
        vimeo_description: str = "",
        year_hint: Optional[int] = None
    ) -> Dict:
        """
        Verify if a Vimeo video is an authentic classic movie.

        Args:
            vimeo_title: Video title from Vimeo
            vimeo_duration_seconds: Video duration in seconds
            vimeo_description: Video description (may contain year hints)
            year_hint: Optional year hint from AI or metadata

        Returns:
            Verification result dict with:
            - verified: bool - Whether movie is verified as authentic classic
            - confidence: float (0-100) - Confidence score
            - tmdb_id: int or None - TMDb movie ID if found
            - tmdb_title: str - Official movie title
            - release_year: int or None - Official release year
            - is_pre_1965: bool - Whether released before 1965
            - production_companies: List of studio names
            - is_classic_studio: bool - Whether from formal studio
            - runtime_minutes: int or None - Official runtime
            - runtime_match: bool - Whether runtime matches Vimeo duration
            - title_similarity: float - How closely titles match
            - match_reason: str - Explanation of verification result
        """
        result = {
            "verified": False,
            "confidence": 0.0,
            "tmdb_id": None,
            "tmdb_title": "",
            "release_year": None,
            "is_pre_1965": False,
            "production_companies": [],
            "is_classic_studio": False,
            "runtime_minutes": None,
            "runtime_match": False,
            "title_similarity": 0.0,
            "match_reason": "No TMDb match found"
        }

        # Search TMDb for the movie
        search_results = self.search_movie(vimeo_title, year_hint)

        if not search_results:
            return result

        # Find best match by title similarity
        best_match = None
        best_similarity = 0.0

        for movie in search_results:
            similarity = self.calculate_title_similarity(
                vimeo_title,
                movie.get("title", "")
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = movie

        # Require minimum similarity of 0.6 (60%)
        if best_match is None or best_similarity < 0.6:
            result["match_reason"] = f"Best title match only {best_similarity*100:.0f}% similar"
            return result

        # Get full movie details
        tmdb_id = best_match["id"]
        movie_details = self.get_movie_details(tmdb_id)

        if not movie_details:
            result["match_reason"] = "Could not fetch movie details from TMDb"
            return result

        # Extract metadata
        result["tmdb_id"] = tmdb_id
        result["tmdb_title"] = movie_details.get("title", "")
        result["title_similarity"] = best_similarity

        # Parse release year
        release_date = movie_details.get("release_date", "")
        if release_date:
            try:
                release_year = int(release_date[:4])
                result["release_year"] = release_year
                result["is_pre_1965"] = release_year < 1965
            except (ValueError, IndexError):
                pass

        # Check production companies
        production_companies = movie_details.get("production_companies", [])
        is_classic, studio_names = self.is_classic_studio(production_companies)
        result["production_companies"] = studio_names if studio_names else [
            c.get("name", "") for c in production_companies[:3]
        ]
        result["is_classic_studio"] = is_classic

        # Check runtime match
        tmdb_runtime = movie_details.get("runtime")
        if tmdb_runtime:
            result["runtime_minutes"] = tmdb_runtime
            vimeo_minutes = vimeo_duration_seconds / 60

            # Allow ±10 minute tolerance
            runtime_diff = abs(tmdb_runtime - vimeo_minutes)
            result["runtime_match"] = runtime_diff <= 10

        # Calculate confidence score
        confidence = 0.0

        # Title similarity (0-40 points)
        confidence += best_similarity * 40

        # Pre-1965 release (30 points)
        if result["is_pre_1965"]:
            confidence += 30

        # Classic studio (20 points)
        if result["is_classic_studio"]:
            confidence += 20

        # Runtime match (10 points)
        if result["runtime_match"]:
            confidence += 10

        result["confidence"] = min(confidence, 100)

        # Determine if verified
        # Criteria: pre-1965 + (classic studio OR high title similarity)
        if result["is_pre_1965"]:
            if result["is_classic_studio"] or best_similarity >= 0.85:
                result["verified"] = True
                result["match_reason"] = "Verified classic movie: pre-1965"
                if result["is_classic_studio"]:
                    result["match_reason"] += f" from {', '.join(result['production_companies'][:2])}"
            else:
                result["match_reason"] = "Pre-1965 but uncertain studio/title match"
        else:
            result["match_reason"] = f"Released in {result['release_year']} (after 1965 cutoff)"

        return result

    def batch_verify(
        self,
        videos: List[Dict],
        delay: float = 0.25
    ) -> List[Dict]:
        """
        Verify a batch of videos with rate limiting.

        Args:
            videos: List of video dicts with 'title', 'duration', etc.
            delay: Delay between API calls in seconds

        Returns:
            List of videos with 'tmdb_verification' field added
        """
        results = []
        total = len(videos)

        print(f"\n🎬 Verifying {total} videos with TMDb...")

        for i, video in enumerate(videos, 1):
            print(f"   [{i}/{total}] Verifying: {video.get('title', 'Untitled')[:50]}...", end=" ")

            verification = self.verify_movie(
                vimeo_title=video.get("title", ""),
                vimeo_duration_seconds=video.get("duration", 0),
                vimeo_description=video.get("description", ""),
                year_hint=video.get("estimated_year")
            )

            video["tmdb_verification"] = verification

            if verification["verified"]:
                print(f"✅ {verification['confidence']:.0f}% - {verification['release_year']}")
            else:
                print(f"❌ {verification['match_reason'][:50]}")

            results.append(video)

            # Rate limiting
            if i < total:
                time.sleep(delay)

        verified_count = sum(1 for v in results if v["tmdb_verification"]["verified"])
        print(f"\n✅ Verified {verified_count}/{total} movies as authentic classics")

        return results


def main():
    """Test the TMDb verifier."""
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        print("❌ Error: TMDB_API_KEY not found in .env file")
        return

    verifier = TMDbVerifier(api_key)

    # Test cases
    test_videos = [
        {
            "title": "Casablanca",
            "duration": 6120,  # 102 minutes
            "description": "Classic romantic drama"
        },
        {
            "title": "Citizen Kane",
            "duration": 7140,  # 119 minutes
            "description": "Orson Welles masterpiece"
        },
        {
            "title": "Inception",  # Modern movie - should fail
            "duration": 8880,  # 148 minutes
            "description": "Christopher Nolan film"
        },
        {
            "title": "The Great Train Robbery",
            "duration": 660,  # 11 minutes - short film
            "description": "1903 silent western"
        }
    ]

    print("🎬 Testing TMDb Movie Verifier\n")
    print("=" * 70)

    for video in test_videos:
        print(f"\nTesting: {video['title']}")
        print("-" * 70)

        result = verifier.verify_movie(
            vimeo_title=video["title"],
            vimeo_duration_seconds=video["duration"],
            vimeo_description=video["description"]
        )

        print(f"  Verified: {result['verified']}")
        print(f"  Confidence: {result['confidence']:.1f}%")
        print(f"  TMDb ID: {result['tmdb_id']}")
        print(f"  Title: {result['tmdb_title']}")
        print(f"  Release Year: {result['release_year']}")
        print(f"  Pre-1965: {result['is_pre_1965']}")
        print(f"  Studios: {', '.join(result['production_companies'][:2]) if result['production_companies'] else 'N/A'}")
        print(f"  Classic Studio: {result['is_classic_studio']}")
        print(f"  Runtime: {result['runtime_minutes']} min (match: {result['runtime_match']})")
        print(f"  Reason: {result['match_reason']}")

        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("✅ Test complete!")


if __name__ == "__main__":
    main()
