#!/usr/bin/env python3
"""
🔍 Debug Games - Test Home Run Props API Connection
================================================

Simple debug script to test The Odds API connection and show
basic information about available MLB games and home run props.

Usage:
    python3 debug_games.py

Environment Variables:
    THE_ODDS_API_KEY - Your API key from The Odds API
"""

import os
import sys
import requests
import json
from datetime import datetime
import pytz

# API Configuration
API_KEY = os.getenv('THE_ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4'
SPORT = 'baseball_mlb'
MARKETS = 'batter_home_runs'
REGIONS = 'us'
ODDS_FORMAT = 'american'

def test_api_connection():
    """Test basic API connection"""
    print("🔍 Testing API connection...")
    
    if not API_KEY:
        print("❌ Error: THE_ODDS_API_KEY environment variable not set")
        print("Please set your API key:")
        print("export THE_ODDS_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ API key found: {API_KEY[:8]}...")
    
    # Test sports endpoint
    try:
        url = f"{BASE_URL}/sports/"
        params = {'apiKey': API_KEY}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        sports = response.json()
        mlb_sport = next((s for s in sports if s['key'] == SPORT), None)
        
        if mlb_sport:
            print(f"✅ MLB sport found: {mlb_sport['title']}")
            print(f"   Active: {mlb_sport.get('active', 'Unknown')}")
        else:
            print("⚠️  MLB sport not found in available sports")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False

def get_games_info():
    """Get basic information about today's games"""
    print("\n🎯 Fetching today's MLB games...")
    
    # Get today's date in Eastern timezone
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    date_str = today_est.strftime('%Y-%m-%d')
    
    url = f"{BASE_URL}/sports/{SPORT}/odds/"
    params = {
        'apiKey': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': 'iso',
        'commenceTimeFrom': f"{date_str}T00:00:00Z",
        'commenceTimeTo': f"{date_str}T23:59:59Z"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        games_data = response.json()
        print(f"✅ Found {len(games_data)} games")
        
        if not games_data:
            print("ℹ️  No games found for today")
            print("   This is normal during off-season or rest days")
            return
        
        games_with_props = 0
        total_players = 0
        all_sportsbooks = set()
        
        for game in games_data:
            away_team = game['away_team']
            home_team = game['home_team']
            commence_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            game_time_est = commence_time.astimezone(eastern)
            
            # Check for home run props
            has_props = False
            game_players = 0
            game_sportsbooks = set()
            
            for bookmaker in game.get('bookmakers', []):
                bookmaker_name = bookmaker['title']
                all_sportsbooks.add(bookmaker_name)
                
                for market in bookmaker.get('markets', []):
                    if market['key'] == MARKETS:
                        has_props = True
                        game_sportsbooks.add(bookmaker_name)
                        
                        # Count unique players
                        players_in_market = set()
                        for outcome in market.get('outcomes', []):
                            players_in_market.add(outcome['description'])
                        game_players = max(game_players, len(players_in_market))
            
            if has_props:
                games_with_props += 1
                total_players += game_players
                
                print(f"\n🏟️  {away_team} @ {home_team}")
                print(f"    Time: {game_time_est.strftime('%I:%M %p %Z')}")
                print(f"    Players: {game_players}")
                print(f"    Sportsbooks: {len(game_sportsbooks)} ({', '.join(sorted(game_sportsbooks))})")
        
        print(f"\n📊 Summary:")
        print(f"   Total games: {len(games_data)}")
        print(f"   Games with home run props: {games_with_props}")
        print(f"   Total players: {total_players}")
        print(f"   Available sportsbooks: {len(all_sportsbooks)}")
        print(f"   Sportsbooks: {', '.join(sorted(all_sportsbooks))}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching games: {e}")

def check_quota():
    """Check remaining API quota if available"""
    print("\n💳 API Usage Information:")
    print(f"   Check your quota at: https://the-odds-api.com/account/")
    print(f"   Each request to fetch games costs API credits")
    print(f"   Monitor usage to avoid hitting limits")

def main():
    """Main debug function"""
    print("🔍 Home Run Props Debug - API Connection Test")
    print("=" * 45)
    
    # Test API connection
    if not test_api_connection():
        return
    
    # Get games information
    get_games_info()
    
    # Show quota information
    check_quota()
    
    print(f"\n✅ Debug complete!")
    print(f"💡 If everything looks good, try running:")
    print(f"   python3 homerun_summary.py")

if __name__ == "__main__":
    main() 