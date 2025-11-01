#!/usr/bin/env python3
"""Convert AI-enhanced CSV to JSON for frontend"""
import csv
import json

# Read CSV
movies = []
with open('outputs/vimeo_movies_ai_enhanced.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convert numeric fields
        duration = 0
        if row.get('duration'):
            try:
                duration = int(row['duration'])
            except ValueError:
                duration = 0

        views = None
        if row.get('views') and row['views'].strip():
            try:
                views = int(row['views'])
            except ValueError:
                views = None

        relevance_score = 0
        if row.get('relevance_score'):
            try:
                relevance_score = int(row['relevance_score'])
            except ValueError:
                relevance_score = 0

        # Convert boolean
        is_old_movie = False
        if row.get('is_old_movie'):
            is_old_movie = row['is_old_movie'].lower() == 'true'

        # Format duration
        if duration:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            if hours > 0:
                duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                duration_formatted = f"{minutes:02d}:{seconds:02d}"
        else:
            duration_formatted = "0:00"

        # Create movie object matching TypeScript interface
        movie = {
            'title': row.get('title', ''),
            'url': row.get('url', ''),
            'description': row.get('description', ''),
            'duration': duration,
            'duration_formatted': duration_formatted,
            'created_date': row.get('created_time', ''),  # Rename field
            'views': views,
            'user': row.get('user', ''),
            'user_url': '',  # Required by interface, but not in CSV
            'is_old_movie': is_old_movie,
            'estimated_era': row.get('estimated_era', ''),
            'genre': row.get('genre', ''),
            'quality_score': relevance_score,  # Map relevance_score to quality_score
        }

        movies.append(movie)

# Save to JSON
with open('app/public/ai_enhanced_movies.json', 'w', encoding='utf-8') as f:
    json.dump(movies, f, indent=2, ensure_ascii=False)

print(f"✅ Converted {len(movies)} movies to JSON")
print(f"   Saved to: app/public/ai_enhanced_movies.json")
