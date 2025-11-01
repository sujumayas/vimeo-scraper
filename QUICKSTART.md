# 🎬 Vimeo Old Movies Finder - Quick Start Guide

## ⚡ Fastest Way to Get Started

### Option 1: No Setup Required (Limited Results)
```bash
pip install -r requirements.txt
python vimeo_scraper_no_api.py
```
✅ No API keys needed  
⚠️ May have limited/incomplete results

### Option 2: Best Results (5 minutes setup)
```bash
# 1. Get free API token: https://developer.vimeo.com/apps
# 2. Edit vimeo_old_movies_finder.py and add your token
# 3. Run:
pip install -r requirements.txt
python vimeo_old_movies_finder.py
```
✅ Best quality results  
✅ Complete video information  
⚠️ Requires free Vimeo API token

### Option 3: Interactive Menu
```bash
python run.py
```
Choose your method from an easy menu!

## 📦 What You Get

All scripts will create a CSV file with 50 old movies including:
- Video title
- Direct URL to watch
- Description
- Duration
- View count
- Upload date
- User/channel info

## 🎯 Output Location

Files are saved to: `/mnt/user-data/outputs/`

Default filenames:
- `vimeo_old_movies.csv` (API version)
- `vimeo_old_movies_scraped.csv` (Web scraper)
- `vimeo_movies_ai_enhanced.csv` (AI version)

## 🔧 Files Included

| File | Purpose |
|------|---------|
| `run.py` | Interactive menu to choose method |
| `vimeo_old_movies_finder.py` | API version (recommended) |
| `vimeo_scraper_no_api.py` | Web scraping (no API needed) |
| `ai_enhanced_finder.py` | AI-powered filtering |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |

## 🆘 Troubleshooting

**"No module named 'requests'"**
→ Run: `pip install -r requirements.txt`

**"401 Authentication failed"**
→ Check your Vimeo API token is correct

**"No videos found"**
→ Try the API version instead of web scraping
→ Or try different search terms

**CSV won't open properly**
→ Use UTF-8 encoding when opening in Excel
→ Or open with Google Sheets (auto-detects)

## 💡 Tips

1. **For variety**: Run multiple times with different searches
2. **For quality**: Use the API version
3. **For filtering**: Use the AI-enhanced version
4. **For Excel**: CSV files open directly in Excel

## 🎓 Getting API Tokens

### Vimeo API (Free, 5 minutes)
1. https://developer.vimeo.com/apps
2. Create app → Generate token → Copy it

### Claude API (Optional, for AI features)
1. https://console.anthropic.com/
2. Sign up → Add payment → Get API key

## 📚 Search Examples

The tool searches for:
- "classic films" 
- "silent movies"
- "vintage cinema"
- "old horror movies"
- "film noir"
- And more...

You can customize these in the script!

## 🚀 Ready to Start?

```bash
# Quick start (no API):
python vimeo_scraper_no_api.py

# Or use the menu:
python run.py
```

**Happy movie hunting! 🍿**
