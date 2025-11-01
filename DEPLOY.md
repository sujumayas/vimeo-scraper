# Deployment Guide

## Netlify Deployment

This project is configured to deploy automatically to Netlify when you push to GitHub.

### Prerequisites

1. Ensure `outputs/ai_enhanced_movies.json` exists with your movie data
2. Commit all changes to Git
3. Push to GitHub

### Setup Steps

1. **Connect Repository to Netlify:**
   - Go to [netlify.com](https://netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Select "GitHub" and authorize Netlify
   - Choose your repository

2. **Configuration (Auto-detected):**
   The `netlify.toml` file in the root directory contains all necessary configuration:
   - Base directory: `app`
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Node version: 18

3. **Deploy:**
   - Click "Deploy site"
   - Netlify will automatically build and deploy
   - Your site will be live at `https://[random-name].netlify.app`

### Manual Configuration (if needed)

If Netlify doesn't auto-detect the settings, configure manually:

```
Base directory: app
Build command: npm run build
Publish directory: dist
```

### Environment Variables

No environment variables needed for the frontend! The movie data is static and included in the build.

### Updating Movie Data

To update the movies displayed on the site:

1. Run the Python scraper:
   ```bash
   source venv/bin/activate
   python ai_enhanced_finder.py
   ```

2. Convert to JSON:
   ```bash
   python convert_to_json.py
   ```

3. Commit and push:
   ```bash
   git add outputs/ai_enhanced_movies.json
   git commit -m "Update movie data"
   git push
   ```

4. Netlify will automatically rebuild and deploy

### Custom Domain (Optional)

1. Go to "Domain settings" in Netlify
2. Click "Add custom domain"
3. Follow the DNS configuration instructions

### Troubleshooting

**Build fails:**
- Check that `outputs/ai_enhanced_movies.json` exists in the repository
- Verify Node version is 18 or higher
- Check build logs in Netlify dashboard

**Movies not showing:**
- Verify `ai_enhanced_movies.json` is in the `outputs/` folder
- Check browser console for errors
- Clear browser cache

**404 errors:**
- The `netlify.toml` includes redirect rules for SPA routing
- If issues persist, check "Redirects and rewrites" in Netlify dashboard
