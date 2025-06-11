#!/usr/bin/env python3
"""
🏠 HomeRun Odds - MLB Home Run Props Data Fetcher
=================================================

Fetches MLB home run prop betting odds from The Odds API and calculates
consensus odds across multiple sportsbooks.

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

def validate_api_key():
    """Validate API key is configured"""
    if not API_KEY:
        print("❌ Error: THE_ODDS_API_KEY environment variable not set")
        print("Please set your API key:")
        print("export THE_ODDS_API_KEY='your-api-key-here'")
        sys.exit(1)

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

def get_games_data() -> List[Dict]:
    """Fetch today's MLB games"""
    print("🔍 Fetching today's MLB games...")
    
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
        print(f"✅ Found {len(games_data)} games with home run props")
        return games_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching games data: {e}")
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
        for market in game.get('bookmakers', []):
            for market_data in market.get('markets', []):
                if market_data['key'] == MARKETS:
                    home_run_market = market_data
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
            
        print(f"\n🏟️  {game['away_team']} @ {game['home_team']}")
        print(f"    {game['game_time_formatted']}")
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
    print("🏠 HomeRun Odds - MLB Home Run Props Fetcher")
    print("=" * 50)
    
    # Validate configuration
    validate_api_key()
    
    # Fetch and process data
    games_data = get_games_data()
    if not games_data:
        print("❌ No games data available")
        return
    
    processed_data = process_home_run_props(games_data)
    
    # Display summary
    display_summary(processed_data)
    
    # Save raw data for other scripts
    output_file = f"homerun_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"\n💾 Raw data saved to: {output_file}")
    print(f"🔗 API usage: Check your quota at https://the-odds-api.com/account/")

if __name__ == "__main__":
    main() 