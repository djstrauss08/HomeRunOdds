#!/usr/bin/env python3
"""
📅 Test Daily Persistence - Demonstrate odds persistence functionality
=====================================================================

Test script to show how odds persist throughout the day even after games start.

Usage:
    python3 test_daily_persistence.py

Environment Variables:
    THE_ODDS_API_KEY - Your API key from The Odds API
"""

import os
import sys
from datetime import datetime
import pytz
import json

# Import functions from homerun_odds
from homerun_odds import (
    validate_api_key, get_games_data, process_home_run_props,
    load_daily_cache, save_daily_cache, merge_with_cached_data,
    DAILY_CACHE_FILE
)

def simulate_game_progression():
    """Simulate how odds persist as games start throughout the day"""
    print("📅 Daily Persistence Test - MLB Home Run Props")
    print("=" * 55)
    print("This test demonstrates how odds remain visible until midnight")
    print("even after games start during the day.\n")
    
    # Check if we have a cache file
    if os.path.exists(DAILY_CACHE_FILE):
        print("💾 Found existing daily cache file")
        cached_data = load_daily_cache()
        
        if cached_data:
            eastern = pytz.timezone('US/Eastern')
            cache_date = cached_data.get('metadata', {}).get('date')
            today_date = datetime.now(eastern).strftime('%Y-%m-%d')
            
            print(f"   Cache date: {cache_date}")
            print(f"   Today's date: {today_date}")
            
            if cache_date == today_date:
                print("✅ Cache is from today - odds will persist")
                
                # Show summary of cached data
                summary = cached_data.get('summary', {})
                print(f"\n📊 Cached Data Summary:")
                print(f"   Total games: {summary.get('total_games', 0)}")
                print(f"   Total players: {summary.get('total_players', 0)}")
                
                if 'live_games' in summary:
                    print(f"   Live games: {summary.get('live_games', 0)}")
                    print(f"   Cached games: {summary.get('cached_games', 0)}")
                
                # Show sample of cached games
                games = cached_data.get('games', [])
                if games:
                    print(f"\n🏟️  Sample Games in Cache:")
                    for i, game in enumerate(games[:3]):  # Show first 3 games
                        status = game.get('odds_status', 'unknown')
                        status_emoji = "🔴" if status == 'live' else "💾" if status == 'cached' else "❓"
                        print(f"   {status_emoji} {game['away_team']} @ {game['home_team']} [{status.upper()}]")
                        print(f"      Players: {len(game.get('players', []))}")
                        
                        if status == 'cached' and game.get('last_updated'):
                            try:
                                update_time = datetime.fromisoformat(game['last_updated'].replace('Z', '+00:00'))
                                eastern = pytz.timezone('US/Eastern')
                                update_time_est = update_time.astimezone(eastern)
                                formatted_time = update_time_est.strftime('%I:%M %p')
                                print(f"      Last updated: {formatted_time}")
                            except:
                                print(f"      Last updated: {game.get('last_updated')}")
                
                print(f"\n💡 How Daily Persistence Works:")
                print(f"   1️⃣  Fresh odds are fetched from the API every 2 hours")
                print(f"   2️⃣  When games start, their odds disappear from the API")
                print(f"   3️⃣  BUT cached odds from earlier remain visible")
                print(f"   4️⃣  Feed shows mix of live odds + cached odds until midnight")
                print(f"   5️⃣  At midnight ET, cache resets for the new day")
                
            else:
                print("🗑️  Cache is from a previous day - will start fresh")
        else:
            print("⚠️  Cache file exists but couldn't be loaded")
    else:
        print("ℹ️  No daily cache file found")
        print("   This is normal for the first run of the day")
    
    print(f"\n🔧 Technical Details:")
    print(f"   Cache file: {DAILY_CACHE_FILE}")
    print(f"   Cache logic: Date-based (resets at midnight ET)")
    print(f"   Merge strategy: Live odds override cached, cached preserved when live unavailable")
    
    # Show what would happen in next run
    print(f"\n🚀 Next Steps:")
    print(f"   Run 'python3 homerun_odds.py' to:")
    print(f"   • Fetch fresh odds from the API")
    print(f"   • Merge with existing cache")
    print(f"   • Display both live and cached odds")
    print(f"   • Update the cache file")

def main():
    """Main test function"""
    try:
        # Don't require API key for this demo
        simulate_game_progression()
        
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main() 