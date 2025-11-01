# Vimeo Old Movies Finder

A tool to search for old/classic movies on Vimeo and export results to CSV or Excel format.

## 🎯 Features

- Search Vimeo for classic/old movies
- Two methods available: API (reliable) or Web Scraping (no API key needed)
- Export results to CSV or JSON
- Customizable search queries
- Deduplication of results
- Optional AI integration for filtering

## 📋 Files Included

1. **vimeo_old_movies_finder.py** - Uses Vimeo API (recommended, requires free API token)
2. **vimeo_scraper_no_api.py** - Web scraping version (no API token needed, but less reliable)
3. **requirements.txt** - Python dependencies

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## 📖 Method 1: Using Vimeo API (Recommended)

### Step 1: Get Your Free API Token

1. Go to https://developer.vimeo.com/
2. Create a free account (if you don't have one)
3. Go to https://developer.vimeo.com/apps
4. Click "Create App"
5. Fill in the app details (name it whatever you want, e.g., "Movie Finder")
6. Once created, go to the "Authentication" tab
7. Generate a new token with these scopes:
   - ✅ Public
   - ✅ Private (optional, for better search results)
8. Copy your access token

### Step 2: Configure the Script

Open `vimeo_old_movies_finder.py` and replace this line:

```python
API_TOKEN = "YOUR_VIMEO_API_TOKEN_HERE"
```

With your actual token:

```python
API_TOKEN = "your_actual_token_here"
```

### Step 3: Run the Script

```bash
python vimeo_old_movies_finder.py
```

The script will:
- Search for old movies using multiple queries
- Find up to 50 unique videos
- Save results to `vimeo_old_movies.csv`
- Also create a backup JSON file

### Customization

You can customize the search queries in the script:

```python
search_queries = [
    "classic films",
    "old movies 1920s",
    "silent films",
    # Add your own queries here
]
```

Or adjust the number of results:

```python
videos = finder.search_videos("classic films", max_results=100)  # Get 100 videos
```

## 📖 Method 2: Web Scraping (No API Token)

If you don't want to get an API token, you can use the scraping version:

```bash
python vimeo_scraper_no_api.py
```

**Note:** This method is less reliable because:
- Vimeo's HTML structure may change
- You might get fewer/incomplete results
- It's slower due to rate limiting
- Some video details may be missing

## 📊 Output Format

The CSV file will contain the following columns:

### API Version Columns:
- `title` - Video title
- `url` - Direct link to the video
- `description` - Video description (first 200 chars)
- `duration` - Duration in seconds
- `duration_formatted` - Human-readable duration (HH:MM:SS)
- `created_date` - When the video was uploaded
- `views` - Number of views
- `user` - Channel/user name
- `user_url` - Link to the user's profile

### Scraper Version Columns:
- `title` - Video title
- `url` - Direct link to the video
- `video_id` - Vimeo video ID
- `description` - Video description (if available)
- `duration` - Duration (if available)
- `views` - View count (if available)
- `user` - Uploader name (if available)

## 🎨 Customization Tips

### 1. Search for Specific Eras

```python
search_queries = [
    "1920s movies",
    "1930s cinema",
    "1940s films",
    "1950s classics"
]
```

### 2. Search by Genre

```python
search_queries = [
    "classic horror",
    "film noir",
    "vintage westerns",
    "silent comedies"
]
```

### 3. Search by Director/Actor

```python
search_queries = [
    "charlie chaplin",
    "buster keaton",
    "hitchcock classic",
    "marx brothers"
]
```

### 4. Focus on Public Domain

```python
# In the API version, uncomment this line:
# "filter": "CC"  # Creative Commons only
```

## 🤖 AI Enhancement (Optional)

You can use AI (like Claude or GPT) to:

1. **Filter results** - Classify videos by era, genre, or quality
2. **Enhance descriptions** - Generate better descriptions
3. **Remove duplicates** - Smart deduplication based on content

To integrate AI:

1. Add your Claude API key
2. Use the search results as input
3. Ask AI to classify/filter the videos

Example:
```python
# After getting videos, you can send them to Claude API
# to filter for specific criteria like:
# - Only feature-length films (> 60 minutes)
# - Specific genres or time periods
# - Quality assessment based on description
```

## 🔧 Troubleshooting

### Issue: API returns 401 error
- Double-check your API token is correct
- Make sure you copied the entire token
- Regenerate token if needed

### Issue: No results found
- Try different search queries
- Make sure your API token has "Public" scope
- Check if Vimeo API is accessible from your network

### Issue: Web scraper not working
- Vimeo's HTML structure may have changed
- Use the API version instead (recommended)
- Check your internet connection

### Issue: CSV encoding problems
- The script uses UTF-8 encoding
- Open CSV in Excel: Data → From Text/CSV → UTF-8 encoding

## 📝 Example Output

```csv
title,url,duration_formatted,views
"The Great Train Robbery (1903)",https://vimeo.com/12345678,12:00,15420
"A Trip to the Moon (1902)",https://vimeo.com/87654321,14:35,28910
"The Cabinet of Dr. Caligari",https://vimeo.com/11223344,01:16:23,42500
```

## 🎯 Tips for Finding Old Movies

1. **Use specific decades**: "1920s films" works better than "old movies"
2. **Search for directors**: "Chaplin", "Méliès", "Eisenstein"
3. **Try genre + era**: "silent horror", "1930s western"
4. **Look for keywords**: "public domain", "classic", "vintage", "restored"
5. **Famous titles**: Search for specific classic films you know

## 📜 Rate Limits

- **Vimeo API**: Free tier allows generous usage
- **Web Scraping**: Built-in delays to be respectful
- **Recommended**: Use API version for reliable results

## 🤝 Contributing

Feel free to modify the search queries, add features, or improve the scraping logic!

## ⚖️ Legal Note

- Respect Vimeo's Terms of Service
- Use API method when possible (it's official and supported)
- Don't scrape excessively
- Some content may have copyright restrictions

## 📚 Resources

- [Vimeo API Documentation](https://developer.vimeo.com/api/reference)
- [Vimeo Developer Portal](https://developer.vimeo.com/)
- [Public Domain Movies](https://archive.org/details/films) - Alternative source

## 🆘 Need Help?

If you encounter issues:
1. Check the error messages carefully
2. Verify your API token (if using API version)
3. Try the alternative method
4. Ensure all dependencies are installed

---

**Happy movie hunting! 🎬🍿**
