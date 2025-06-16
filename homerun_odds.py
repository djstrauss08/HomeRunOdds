#!/usr/bin/env python3
"""
🏠 HomeRun Odds - MLB Home Run Props Data Fetcher with Daily Persistence
========================================================================

Fetches MLB home run prop betting odds from The Odds API and calculates
consensus odds across multiple sportsbooks. Keeps odds visible until
the next day even after games start.

Usage:
    python3 homerun_odds.py

Environment Variables:
    THE_ODDS_API_KEY - Your API key from The Odds API
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any, Optional

# API Configuration
API_KEY = os.getenv('THE_ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4'

# Sports and Markets Configuration
SPORT = 'baseball_mlb'
MARKETS = 'batter_home_runs'  # Home run props market
REGIONS = 'us'
ODDS_FORMAT = 'american'

# Daily persistence configuration
DAILY_CACHE_FILE = "daily_homerun_cache.json"

def validate_api_key():
    """Validate API key is configured"""
    if not API_KEY:
        print("❌ Error: THE_ODDS_API_KEY environment variable not set")
        print("Please set your API key:")
        print("export THE_ODDS_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print(f"✅ API key configured: {API_KEY[:8]}...")

def american_to_probability(odds: int) -> float:
    """Convert American odds to implied probability"""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

def probability_to_american(prob: float) -> int:
    """Convert probability back to American odds"""
    if prob >= 0.5:
        return int(-prob * 100 / (1 - prob))
    else:
        return int((1 - prob) * 100 / prob)

def calculate_consensus_odds(odds_list: List[int]) -> int:
    """Calculate consensus odds from multiple sportsbooks"""
    if not odds_list:
        return 0
    
    # Convert to probabilities, average, convert back
    probabilities = [american_to_probability(odds) for odds in odds_list]
    avg_probability = sum(probabilities) / len(probabilities)
    return probability_to_american(avg_probability)

def load_daily_cache() -> Dict[str, Any]:
    """Load cached odds data from previous runs today"""
    try:
        if os.path.exists(DAILY_CACHE_FILE):
            with open(DAILY_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is from today
            eastern = pytz.timezone('US/Eastern')
            today_str = datetime.now(eastern).strftime('%Y-%m-%d')
            
            if cache_data.get('metadata', {}).get('date') == today_str:
                print(f"✅ Loaded cached odds data from earlier today")
                return cache_data
            else:
                print(f"🗑️  Cache is from {cache_data.get('metadata', {}).get('date', 'unknown date')}, starting fresh")
                return {}
        else:
            print("ℹ️  No daily cache file found, starting fresh")
            return {}
    except Exception as e:
        print(f"⚠️  Error loading cache: {e}")
        return {}

def save_daily_cache(data: Dict[str, Any]):
    """Save current odds data to daily cache"""
    try:
        with open(DAILY_CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved odds data to daily cache")
    except Exception as e:
        print(f"⚠️  Error saving cache: {e}")

def merge_with_cached_data(new_data: Dict[str, Any], cached_data: Dict[str, Any]) -> Dict[str, Any]:
    """Merge new API data with cached data, keeping the best of both"""
    if not cached_data or not cached_data.get('games'):
        return new_data
    
    print("🔄 Merging new data with cached odds...")
    
    # Create a lookup for new games by game_id
    new_games_lookup = {game['game_id']: game for game in new_data.get('games', [])}
    
    # Start with new data structure
    merged_data = new_data.copy()
    merged_games = []
    
    # Process cached games
    for cached_game in cached_data.get('games', []):
        game_id = cached_game['game_id']
        
        if game_id in new_games_lookup:
            # Game still has live odds - use the new data
            merged_games.append(new_games_lookup[game_id])
            print(f"    🔄 Updated odds for {cached_game['away_team']} @ {cached_game['home_team']}")
        else:
            # Game no longer has live odds - keep cached data with a flag
            cached_game_copy = cached_game.copy()
            cached_game_copy['odds_status'] = 'cached'
            cached_game_copy['last_updated'] = cached_data.get('metadata', {}).get('generated_at', 'unknown')
            merged_games.append(cached_game_copy)
            print(f"    💾 Preserved cached odds for {cached_game['away_team']} @ {cached_game['home_team']}")
    
    # Add any new games that weren't in cache
    for game_id, new_game in new_games_lookup.items():
        if not any(g['game_id'] == game_id for g in merged_games):
            new_game['odds_status'] = 'live'
            merged_games.append(new_game)
            print(f"    🆕 Added new game {new_game['away_team']} @ {new_game['home_team']}")
    
    # Update merged data
    merged_data['games'] = merged_games
    
    # Update summary counts
    live_games = len([g for g in merged_games if g.get('odds_status') == 'live'])
    cached_games = len([g for g in merged_games if g.get('odds_status') == 'cached'])
    total_players = sum(len(game.get('players', [])) for game in merged_games)
    
    merged_data['summary'] = {
        'total_games': len(merged_games),
        'games_with_props': len(merged_games),
        'total_players': total_players,
        'live_games': live_games,
        'cached_games': cached_games
    }
    
    print(f"✅ Merged data: {live_games} live games, {cached_games} cached games, {total_players} total players")
    return merged_data

def get_games_data() -> List[Dict]:
    """Fetch today's MLB games and their home run props"""
    print("🔍 Fetching today's MLB games...")
    
    # Get today's date in Eastern timezone
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    date_str = today_est.strftime('%Y-%m-%d')
    
    # Step 1: Get today's games using h2h market (which always works)
    # Remove date filtering from API call and filter afterward to catch all games
    games_url = f"{BASE_URL}/sports/{SPORT}/odds/"
    games_params = {
        'apiKey': API_KEY,
        'regions': REGIONS,
        'markets': 'h2h',  # Use h2h to get basic game info
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': 'iso'
        # Removed date filtering - we'll filter afterward
    }
    
    try:
        print(f"🎯 Getting all available MLB games...")
        games_response = requests.get(games_url, params=games_params, timeout=30)
        games_response.raise_for_status()
        
        games_data = games_response.json()
        
        # Filter games to only include those that are actually today in Eastern time
        today_games = []
        for game in games_data:
            # Convert UTC time to Eastern time
            commence_utc = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            commence_est = commence_utc.astimezone(eastern)
            game_date_est = commence_est.strftime('%Y-%m-%d')
            
            if game_date_est == date_str:
                today_games.append(game)
        
        print(f"✅ Found {len(today_games)} MLB games for today (filtered from {len(games_data)} total)")
        
        if not today_games:
            print("ℹ️  No MLB games found for today")
            return []
        
        # Step 2: Get player props for each game using the EVENTS endpoint
        games_with_props = []
        
        for i, game in enumerate(today_games, 1):
            event_id = game['id']
            commence_utc = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            commence_est = commence_utc.astimezone(eastern)
            time_str = commence_est.strftime('%H:%M EST')
            
            print(f"🏠 [{i}/{len(today_games)}] Getting home run props for {game['away_team']} @ {game['home_team']} ({time_str})...")
            
            # FIXED: Use the events endpoint for player props (this is the key!)
            props_url = f"{BASE_URL}/sports/{SPORT}/events/{event_id}/odds"
            props_params = {
                'apiKey': API_KEY,
                'regions': REGIONS,
                'markets': MARKETS,  # batter_home_runs
                'oddsFormat': ODDS_FORMAT,
                'dateFormat': 'iso'
            }
            
            try:
                props_response = requests.get(props_url, params=props_params, timeout=30)
                
                if props_response.status_code == 200:
                    props_data = props_response.json()
                    
                    # Check if this game has home run props
                    has_props = False
                    if props_data.get('bookmakers'):
                        for bookmaker in props_data['bookmakers']:
                            for market in bookmaker.get('markets', []):
                                if market['key'] == MARKETS and market.get('outcomes'):
                                    has_props = True
                                    break
                            if has_props:
                                break
                    
                    if has_props:
                        # Merge game info with props data
                        game_with_props = {
                            'id': game['id'],
                            'sport_key': game['sport_key'],
                            'sport_title': game['sport_title'],
                            'commence_time': game['commence_time'],
                            'home_team': game['home_team'],
                            'away_team': game['away_team'],
                            'bookmakers': props_data['bookmakers']
                        }
                        games_with_props.append(game_with_props)
                        print(f"    ✅ Found home run props!")
                    else:
                        print(f"    ❌ No home run props available")
                else:
                    print(f"    ⚠️  API error for props: {props_response.status_code}")
                    if props_response.status_code == 422:
                        print(f"    Error: {props_response.text[:200]}...")
                    
            except Exception as e:
                print(f"    ❌ Error getting props: {e}")
                continue
        
        print(f"🎯 Final result: {len(games_with_props)} games with home run props out of {len(today_games)} total games")
        return games_with_props
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching games: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

def process_home_run_props(games_data: List[Dict]) -> Dict[str, Any]:
    """Process home run props data into structured format"""
    print("🏠 Processing home run props data...")
    
    eastern = pytz.timezone('US/Eastern')
    processed_data = {
        'metadata': {
            'generated_at': datetime.now(eastern).isoformat(),
            'date': datetime.now(eastern).strftime('%Y-%m-%d'),
            'timezone': 'US/Eastern',
            'sport': SPORT,
            'market': MARKETS
        },
        'summary': {
            'total_games': 0,
            'total_players': 0,
            'games_with_props': 0
        },
        'games': []
    }
    
    games_with_props = 0
    total_players = 0
    
    for game in games_data:
        # Parse game info
        away_team = game['away_team']
        home_team = game['home_team']
        commence_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
        game_time_est = commence_time.astimezone(eastern)
        
        # Find home run props market
        home_run_market = None
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                if market['key'] == MARKETS:
                    home_run_market = market
                    break
            if home_run_market:
                break
        
        if not home_run_market:
            continue
            
        games_with_props += 1
        
        # Process player props
        game_data = {
            'game_id': game['id'],
            'away_team': away_team,
            'home_team': home_team,
            'commence_time': game_time_est.isoformat(),
            'game_time_formatted': game_time_est.strftime('%I:%M %p %Z'),
            'players': []
        }
        
        # Group outcomes by player
        player_props = {}
        
        for bookmaker in game.get('bookmakers', []):
            bookmaker_name = bookmaker['title']
            
            for market in bookmaker.get('markets', []):
                if market['key'] != MARKETS:
                    continue
                    
                for outcome in market.get('outcomes', []):
                    player_name = outcome['description']
                    line = outcome.get('point', 0.5)  # Default to 0.5 for "to hit home run"
                    outcome_type = outcome['name']  # 'Over' for Yes, 'Under' for No
                    odds = outcome['price']
                    
                    # Create player key
                    player_key = f"{player_name}_{line}"
                    
                    if player_key not in player_props:
                        player_props[player_key] = {
                            'player_name': player_name,
                            'line': line,
                            'line_display': f"{line}" if line != 0.5 else "To Hit HR",
                            'odds': {},
                            'sportsbooks': []
                        }
                    
                    # Store odds by outcome type
                    if outcome_type not in player_props[player_key]['odds']:
                        player_props[player_key]['odds'][outcome_type] = []
                    
                    player_props[player_key]['odds'][outcome_type].append({
                        'sportsbook': bookmaker_name,
                        'odds': odds
                    })
                    
                    if bookmaker_name not in player_props[player_key]['sportsbooks']:
                        player_props[player_key]['sportsbooks'].append(bookmaker_name)
        
        # Calculate consensus odds for each player
        for player_key, player_data in player_props.items():
            processed_player = {
                'player_name': player_data['player_name'],
                'line': player_data['line'],
                'line_display': player_data['line_display'],
                'sportsbook_count': len(player_data['sportsbooks']),
                'sportsbooks': player_data['sportsbooks'],
                'odds_by_book': {}
            }
            
            # Process Yes/No odds (Over/Under)
            for outcome_type, odds_list in player_data['odds'].items():
                odds_values = [item['odds'] for item in odds_list]
                consensus_odds = calculate_consensus_odds(odds_values)
                
                processed_player[f"{outcome_type.lower()}_odds"] = {
                    'consensus': consensus_odds,
                    'individual_books': odds_list
                }
                
                # Store by book for easy access
                for odds_item in odds_list:
                    book_name = odds_item['sportsbook']
                    if book_name not in processed_player['odds_by_book']:
                        processed_player['odds_by_book'][book_name] = {}
                    processed_player['odds_by_book'][book_name][outcome_type.lower()] = odds_item['odds']
            
            game_data['players'].append(processed_player)
            total_players += 1
        
        # Sort players by name
        game_data['players'].sort(key=lambda x: x['player_name'])
        processed_data['games'].append(game_data)
    
    # Update summary
    processed_data['summary'] = {
        'total_games': len(games_data),
        'games_with_props': games_with_props,
        'total_players': total_players
    }
    
    print(f"✅ Processed {total_players} players across {games_with_props} games")
    return processed_data

def display_summary(data: Dict[str, Any]):
    """Display formatted summary of home run props"""
    print("\n" + "="*60)
    print("🏠 MLB Home Run Props - Today's Players")
    print("="*60)
    print(f"Date: {datetime.fromisoformat(data['metadata']['generated_at']).strftime('%A, %B %d, %Y')}")
    print(f"\n📅 Found {data['summary']['total_games']} MLB games for today")
    
    # Show live vs cached breakdown if available
    if 'live_games' in data['summary']:
        live_games = data['summary']['live_games']
        cached_games = data['summary']['cached_games']
        print(f"🔴 {live_games} games with live odds")
        print(f"💾 {cached_games} games with cached odds (kept until midnight)")
    else:
        print(f"🏠 {data['summary']['games_with_props']} games have home run props")
    
    print(f"⚾ {data['summary']['total_players']} total players with home run odds")
    
    if not data['games']:
        print("\n❌ No home run props available for today")
        return
    
    print(f"\n📊 PLAYER HOME RUN PROPS")
    print("="*60)
    
    for game in data['games']:
        if not game['players']:
            continue
        
        # Show status indicator
        status_indicator = ""
        if game.get('odds_status') == 'cached':
            status_indicator = " 💾 [CACHED]"
        elif game.get('odds_status') == 'live':
            status_indicator = " 🔴 [LIVE]"
            
        print(f"\n🏟️  {game['away_team']} @ {game['home_team']}{status_indicator}")
        print(f"    {game['game_time_formatted']}")
        
        if game.get('odds_status') == 'cached':
            last_updated = game.get('last_updated', 'unknown')
            try:
                update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                eastern = pytz.timezone('US/Eastern')
                update_time_est = update_time.astimezone(eastern)
                formatted_time = update_time_est.strftime('%I:%M %p')
                print(f"    Last updated: {formatted_time}")
            except:
                print(f"    Last updated: {last_updated}")
        
        print("    " + "-"*50)
        
        for player in game['players'][:10]:  # Show top 10 players per game
            line_display = player['line_display']
            book_count = player['sportsbook_count']
            
            # Get consensus odds
            yes_odds = player.get('over_odds', {}).get('consensus', 0)
            no_odds = player.get('under_odds', {}).get('consensus', 0)
            
            if yes_odds and no_odds:
                yes_display = f"+{yes_odds}" if yes_odds > 0 else str(yes_odds)
                no_display = f"+{no_odds}" if no_odds > 0 else str(no_odds)
                
                print(f"    ⚾ {player['player_name']}")
                print(f"        {line_display}")
                print(f"        Yes: {yes_display}  |  No: {no_display}")
                print(f"        ({book_count} sportsbooks)")
            
        if len(game['players']) > 10:
            remaining = len(game['players']) - 10
            print(f"    ... and {remaining} more players")

def main():
    """Main execution function"""
    print("🏠 HomeRun Odds - MLB Home Run Props Fetcher with Daily Persistence")
    print("=" * 70)
    
    # Validate configuration
    validate_api_key()
    
    # Load cached data from earlier today
    cached_data = load_daily_cache()
    
    # Fetch fresh data from API
    print("\n🔍 Fetching fresh odds data from API...")
    games_data = get_games_data()
    
    if games_data:
        # Process the fresh data
        processed_data = process_home_run_props(games_data)
        
        # Merge with cached data to preserve odds from games that started
        final_data = merge_with_cached_data(processed_data, cached_data)
        
        # Save the merged data as new cache
        save_daily_cache(final_data)
        
    elif cached_data:
        # No fresh data available, but we have cached data
        print("⚠️  No fresh data available from API, using cached data only")
        final_data = cached_data
        
        # Update the generated_at timestamp while keeping cached odds
        eastern = pytz.timezone('US/Eastern')
        final_data['metadata']['generated_at'] = datetime.now(eastern).isoformat()
        final_data['metadata']['note'] = 'Using cached odds - API returned no data'
        
    else:
        # No data at all
        print("❌ No games data available and no cached data")
        return
    
    # Display summary
    display_summary(final_data)
    
    # Save raw data for other scripts
    output_file = f"homerun_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(final_data, f, indent=2)
    
    print(f"\n💾 Raw data saved to: {output_file}")
    print(f"🔗 API usage: Check your quota at https://the-odds-api.com/account/")
    
    # Show cache info
    print(f"\n💡 Odds will remain visible until midnight ET")
    if cached_data:
        live_count = final_data['summary'].get('live_games', 0)
        cached_count = final_data['summary'].get('cached_games', 0)
        if cached_count > 0:
            print(f"   {live_count} games still have live odds")
            print(f"   {cached_count} games are showing cached odds from earlier today")

if __name__ == "__main__":
    main() 