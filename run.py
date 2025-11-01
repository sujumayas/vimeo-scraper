#!/usr/bin/env python3
"""
Vimeo Movie Finder - Simple Menu
Choose your preferred method to search for old movies
"""

import sys
import subprocess
import os

def print_header():
    print("\n" + "=" * 70)
    print("🎬 VIMEO OLD MOVIES FINDER")
    print("=" * 70)
    print()

def print_menu():
    print("Choose your search method:")
    print()
    print("1. 🔑 Vimeo API Method (Recommended)")
    print("   - Most reliable")
    print("   - Best results")
    print("   - Requires free API token from https://developer.vimeo.com/")
    print()
    print("2. 🌐 Web Scraping Method (No API Key)")
    print("   - No registration needed")
    print("   - Less reliable")
    print("   - May have limited results")
    print()
    print("3. 🤖 AI-Enhanced Method (Advanced)")
    print("   - Uses AI to filter/classify results")
    print("   - Requires both Vimeo API + Claude API")
    print("   - Best quality filtering")
    print()
    print("4. 🎯 Comprehensive AI-First Pipeline (BEST)")
    print("   - Multi-stage verification (AI + TMDb)")
    print("   - Finds REAL classic movies (pre-1965)")
    print("   - Filters out trailers, promos, reviews")
    print("   - Requires Vimeo + Claude + TMDb APIs")
    print()
    print("5. ❓ Setup Help")
    print("   - How to get API tokens")
    print("   - Installation instructions")
    print()
    print("6. 🚪 Exit")
    print()

def show_setup_help():
    print("\n" + "=" * 70)
    print("📚 SETUP HELP")
    print("=" * 70)
    print()
    
    print("🔧 Installation:")
    print("   1. Make sure Python 3.7+ is installed")
    print("   2. Run: pip install -r requirements.txt")
    print()
    
    print("🔑 Getting Vimeo API Token (Free):")
    print("   1. Go to: https://developer.vimeo.com/apps")
    print("   2. Create a free account")
    print("   3. Click 'Create App'")
    print("   4. Fill in app name (anything you want)")
    print("   5. Go to Authentication tab")
    print("   6. Generate access token with 'Public' scope")
    print("   7. Copy the token")
    print("   8. Add it to your .env file as VIMEO_API_TOKEN")
    print()

    print("🤖 Getting Claude API Key (Optional, for AI features):")
    print("   1. Go to: https://console.anthropic.com/")
    print("   2. Sign up for an account")
    print("   3. Add billing (pay-as-you-go, very cheap)")
    print("   4. Get your API key from settings")
    print("   5. Add it to your .env file as ANTHROPIC_API_KEY")
    print()

    print("🎬 Getting TMDb API Key (Free, for comprehensive pipeline):")
    print("   1. Go to: https://www.themoviedb.org/signup")
    print("   2. Create a free account")
    print("   3. Go to Settings → API")
    print("   4. Request an API key (choose 'Developer')")
    print("   5. Fill in basic info about your use")
    print("   6. Copy the API Read Access Token (v4 auth)")
    print("   7. Add it to your .env file as TMDB_API_KEY")
    print()

    print("📝 Setting up .env file:")
    print("   1. Copy .env.example to .env")
    print("   2. Edit .env and add your API keys")
    print("   3. Never commit .env to version control (already in .gitignore)")
    print()

    print("💡 Which method to choose:")
    print("   - No API key? → Use Web Scraping (limited results)")
    print("   - Have 5 minutes? → Get free Vimeo API (best results)")
    print("   - Want AI filtering? → Use AI-Enhanced (requires Vimeo + Claude)")
    print("   - Want BEST results? → Use Comprehensive Pipeline (all 3 APIs)")
    print()
    
    input("Press Enter to return to menu...")

def run_script(script_name):
    """Run a Python script"""
    print(f"\n🚀 Launching {script_name}...")
    print("-" * 70)
    print()
    
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running script: {e}")
    except FileNotFoundError:
        print(f"\n❌ Script not found: {script_name}")
        print("   Make sure all files are in the same directory.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    print()
    input("Press Enter to return to menu...")

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import requests
        import bs4
        import dotenv
        return True
    except ImportError:
        return False

def main():
    if not check_dependencies():
        print("\n⚠️  WARNING: Required packages not installed!")
        print("   Please run: pip install -r requirements.txt")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    while True:
        print_header()
        print_menu()

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            run_script("vimeo_old_movies_finder.py")
        elif choice == "2":
            run_script("vimeo_scraper_no_api.py")
        elif choice == "3":
            run_script("ai_enhanced_finder.py")
        elif choice == "4":
            run_script("comprehensive_movie_finder.py")
        elif choice == "5":
            show_setup_help()
        elif choice == "6":
            print("\n👋 Goodbye! Happy movie hunting!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-6.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
