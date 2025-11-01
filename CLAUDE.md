# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack application for discovering and browsing old/classic movies on Vimeo. It consists of:

1. **Python Backend Tools** - Three distinct approaches to searching and collecting movie data from Vimeo
2. **React Frontend** - A web application for browsing and watching the discovered movies

All backend results are exported to CSV/JSON format in the `./outputs/` directory, which the web app consumes for display.

## Project Structure

```
.
├── vimeo_old_movies_finder.py   # API-based movie finder (recommended)
├── vimeo_scraper_no_api.py      # Web scraping version (no API key needed)
├── ai_enhanced_finder.py        # AI-powered classifier (requires Claude API)
├── run.py                       # Interactive CLI menu
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .env                         # API keys (git-ignored)
├── outputs/                     # Generated CSV/JSON files
├── README.md                    # Full project documentation
├── QUICKSTART.md                # Quick start guide
└── app/                         # React web application
    ├── src/
    │   ├── components/          # React components
    │   │   ├── MovieBrowser.tsx
    │   │   ├── MovieCard.tsx
    │   │   └── VideoPlayer.tsx
    │   ├── ui/                  # UI components from esen-ds-minimal
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

## Development Commands

### Backend (Python)

**Setup:**
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys
```

**Running the Tools:**
```bash
# Interactive menu to choose method
python run.py

# API-based search (recommended, requires Vimeo API token)
python vimeo_old_movies_finder.py

# Web scraping (no API token needed, limited results)
python vimeo_scraper_no_api.py

# AI-enhanced filtering (requires both Vimeo + Claude API tokens)
python ai_enhanced_finder.py
```

### Frontend (React/TypeScript)

**Setup:**
```bash
cd app
npm install
```

**Development:**
```bash
cd app
npm run dev
# App runs at http://localhost:5173
```

**Build:**
```bash
cd app
npm run build
npm run preview
```

## Architecture

### Backend Components

**1. API-Based Finder** (`vimeo_old_movies_finder.py`)
- Uses official Vimeo API v3.4
- `VimeoMovieFinder` class with search, pagination, and export capabilities
- Searches multiple queries and deduplicates results by URL
- Applies Creative Commons filter (`filter: "CC"`) for public domain content
- Outputs: `outputs/vimeo_old_movies.csv` and `outputs/vimeo_old_movies.json`
- Line references:
  - Class definition: `vimeo_old_movies_finder.py:19`
  - API token loading: `vimeo_old_movies_finder.py:199`
  - Search method: `vimeo_old_movies_finder.py:34`
  - Creative Commons filter: `vimeo_old_movies_finder.py:63`

**2. Web Scraper** (`vimeo_scraper_no_api.py`)
- `VimeoScraper` class using BeautifulSoup for HTML parsing
- Searches Vimeo's public search pages without authentication
- Extracts video IDs via regex pattern `^/\d+`
- Less reliable due to HTML structure changes
- Outputs: `outputs/vimeo_old_movies_scraped.csv`

**3. AI-Enhanced Finder** (`ai_enhanced_finder.py`)
- `AIEnhancedMovieFinder` class combining Vimeo API + Claude API
- Uses Claude (model: `claude-sonnet-4-20250514`) to classify videos
- Batch processing (10 videos per API call) for efficiency
- Adds AI-generated fields: `is_old_movie`, `estimated_era`, `genre`, `relevance_score`
- Filters results by minimum relevance score (default: 6/10)
- Outputs: `outputs/vimeo_movies_ai_enhanced.csv`
- Line references:
  - Class definition: `ai_enhanced_finder.py:17`
  - AI classification: `ai_enhanced_finder.py:88`
  - Claude model: `ai_enhanced_finder.py:146`

**4. Interactive Menu** (`run.py`)
- CLI menu system for choosing between the three methods
- Dependency checking before execution
- Setup help and API token guidance
- Launches scripts as subprocesses

### Frontend Components

**Web Application** (`app/`)
- Built with React 18, TypeScript, and Vite
- Loads movie data from `outputs/vimeo_old_movies.json`
- Features:
  - Responsive grid layout for movie cards
  - Embedded Vimeo player for instant playback
  - Real-time search filtering
  - Dark/light mode toggle
  - Minimal design using esen-ds-minimal design system
- Key files:
  - `app/src/components/MovieBrowser.tsx` - Main browser component with search and grid
  - `app/src/components/MovieCard.tsx` - Individual movie card with thumbnail
  - `app/src/components/VideoPlayer.tsx` - Embedded Vimeo player
  - `app/src/ui/` - Design system components (Page, Button, Input, etc.)

### Key Design Patterns

**Environment Variables**:
- All API keys are loaded from `.env` file using `python-dotenv`
- Never commit `.env` (included in `.gitignore`)
- Template provided in `.env.example`
- Environment variables:
  - `VIMEO_API_TOKEN` - Required for API-based and AI-enhanced finders
  - `ANTHROPIC_API_KEY` - Required for AI-enhanced finder only

**API Token Configuration**:
- Vimeo API: `os.getenv("VIMEO_API_TOKEN")` in `vimeo_old_movies_finder.py:199` and `ai_enhanced_finder.py:216`
- Claude API: `os.getenv("ANTHROPIC_API_KEY")` in `ai_enhanced_finder.py:217`
- Scripts check for missing tokens and provide helpful error messages
- No hardcoded tokens - all loaded from environment

**Deduplication Strategy**:
- All finders track `seen_urls` sets to prevent duplicate entries across multiple search queries

**Output Location**:
- All scripts write to `./outputs/` directory relative to the project root
- Directory is automatically created if it doesn't exist
- Both CSV and JSON formats generated

**Rate Limiting**:
- API finder: 0.5-1 second delays between requests (`vimeo_old_movies_finder.py:104,128`)
- Web scraper: 2-3 second delays to be respectful
- AI classifier: Processes in batches to minimize API calls

**Error Handling**:
- Scripts continue on errors but print helpful emoji-prefixed messages
- Never crash completely - graceful degradation
- Missing API tokens show setup instructions

### Search Query Strategy

All finders use multiple search queries for variety:
- Eras: "old movies 1920s", "1930s movies"
- Genres: "film noir", "silent films", "vintage cinema"
- Descriptors: "classic films", "public domain films", "classic hollywood"

Example in `vimeo_old_movies_finder.py:211-222`:
```python
search_queries = [
    "classic films",
    "old movies 1920s",
    "silent films",
    "vintage cinema",
    "public domain films",
    # ...
]
```

Queries are processed sequentially with results combined and deduplicated.

### Output Schema

**API Version** (`vimeo_old_movies.csv/json`):
- `title` - Video title
- `url` - Direct link to video
- `description` - Video description (truncated to 200 chars)
- `duration` - Duration in seconds
- `duration_formatted` - Human-readable format (HH:MM:SS or MM:SS)
- `created_date` - ISO timestamp when video was uploaded
- `views` - Number of views
- `user` - Channel/user name
- `user_url` - Link to user's profile

**Scraper Version** (`vimeo_old_movies_scraped.csv`):
- Same fields as API version, but some may be empty due to scraping limitations
- Additional `video_id` field

**AI-Enhanced Version** (`vimeo_movies_ai_enhanced.csv`):
- All fields from API version, plus:
- `is_old_movie` - Boolean (AI classification)
- `estimated_era` - Decade like "1920s", "1940s", or "modern"
- `genre` - Primary genre (horror, comedy, drama, western, etc.)
- `relevance_score` - 1-10 rating for relevance to old movie search

## Important Notes

### Backend
- Python scripts use `python-dotenv` for environment variable management
- Dependencies: `requests`, `beautifulsoup4`, `openpyxl`, `python-dotenv`
- Output files saved to `./outputs/` directory (auto-created)
- Web scraper is fragile and depends on Vimeo's HTML structure remaining stable
- Creative Commons filter applied in API searches to focus on public domain content
- Duration formatting uses `HH:MM:SS` or `MM:SS` depending on length

### Frontend
- Web app loads data from `outputs/vimeo_old_movies.json` (generated by Python scripts)
- Uses Vite dev server on port 5173 (typically)
- Requires running the Python scraper first to generate data
- Design system: esen-ds-minimal (monospace fonts, 3px border radius)
- Responsive design with grid layout

### Documentation
- `README.md` - Comprehensive user guide with setup instructions
- `QUICKSTART.md` - Fast-track setup guide for quick starts
- `.env.example` - Template showing required environment variables

## Getting Started (Quick Reference)

1. **Backend Setup:**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   python run.py  # Interactive menu
   ```

2. **Frontend Setup:**
   ```bash
   cd app
   npm install
   npm run dev
   ```

3. **API Keys:**
   - Vimeo: https://developer.vimeo.com/apps (free)
   - Claude: https://console.anthropic.com/ (optional, for AI features)
