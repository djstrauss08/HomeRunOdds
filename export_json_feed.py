#!/usr/bin/env python3
"""
🏠 HomeRun JSON Export - Generate JSON Feeds for Home Run Props
==============================================================

Exports MLB home run props data in multiple JSON formats optimized 
for different use cases and consumers.

Usage:
    python3 export_json_feed.py                    # Export to file
    python3 export_json_feed.py --pretty           # Pretty print to file
    python3 export_json_feed.py --stdout           # Output to stdout
    python3 export_json_feed.py --format summary   # Summary format only

Environment Variables:
    THE_ODDS_API_KEY - Your API key from The Odds API
"""

import os
import sys
import json
import argparse
from datetime import datetime
import pytz
from typing import Dict, List, Any

# Import functions from main script
from homerun_odds import (
    validate_api_key, get_games_data, process_home_run_props
)
from homerun_summary import find_primary_lines

def create_full_dataset(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create complete dataset with all games, players, and odds"""
    return {
        'metadata': {
            **data['metadata'],
            'format': 'full_dataset',
            'description': 'Complete home run props with all sportsbooks and lines',
            'use_case': 'Full data analysis, comprehensive dashboards'
        },
        'summary': data['summary'],
        'games': data['games']
    }

def create_summary_dataset(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create lightweight summary without detailed odds"""
    summary_games = []
    
    for game in data['games']:
        summary_game = {
            'game_id': game['game_id'],
            'away_team': game['away_team'],
            'home_team': game['home_team'],
            'commence_time': game['commence_time'],
            'game_time_formatted': game['game_time_formatted'],
            'player_count': len(game['players']),
            'odds_status': game.get('odds_status', 'unknown'),
            'players': [
                {
                    'player_name': player['player_name'],
                    'line_display': player['line_display'],
                    'sportsbook_count': player['sportsbook_count']
                } for player in game['players']
            ]
        }
        
        # Add last_updated if it's cached odds
        if game.get('odds_status') == 'cached' and game.get('last_updated'):
            summary_game['last_updated'] = game['last_updated']
            
        summary_games.append(summary_game)
    
    return {
        'metadata': {
            **data['metadata'],
            'format': 'summary',
            'description': 'Lightweight summary with game info and player counts',
            'use_case': 'Quick overview, mobile apps, initial page loads'
        },
        'summary': data['summary'],
        'games': summary_games
    }

def create_players_dataset(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create player-centric dataset with game context"""
    all_players = []
    
    for game in data['games']:
        for player in game['players']:
            player_with_context = {
                **player,  # Include all player data
                'game_context': {
                    'game_id': game['game_id'],
                    'away_team': game['away_team'],
                    'home_team': game['home_team'],
                    'commence_time': game['commence_time'],
                    'game_time_formatted': game['game_time_formatted'],
                    'odds_status': game.get('odds_status', 'unknown')
                }
            }
            
            # Add last_updated if it's cached odds
            if game.get('odds_status') == 'cached' and game.get('last_updated'):
                player_with_context['game_context']['last_updated'] = game['last_updated']
            
            all_players.append(player_with_context)
    
    # Sort by player name
    all_players.sort(key=lambda x: x['player_name'])
    
    return {
        'metadata': {
            **data['metadata'],
            'format': 'players',
            'description': 'All player props with game context',
            'use_case': 'Player comparison, fantasy applications, player-specific analysis'
        },
        'summary': {
            **data['summary'],
            'total_entries': len(all_players)
        },
        'players': all_players
    }

def create_best_odds_dataset(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create dataset focusing on best odds and value bets"""
    best_odds_players = []
    
    for game in data['games']:
        for player in game['players']:
            # Calculate implied probability and potential value
            yes_odds = player.get('over_odds', {}).get('consensus', 0)
            no_odds = player.get('under_odds', {}).get('consensus', 0)
            
            if yes_odds and no_odds:
                # Calculate implied probabilities
                yes_prob = (abs(yes_odds) / (abs(yes_odds) + 100)) if yes_odds < 0 else (100 / (yes_odds + 100))
                no_prob = (abs(no_odds) / (abs(no_odds) + 100)) if no_odds < 0 else (100 / (no_odds + 100))
                
                # Find best individual book odds
                best_yes = max(player.get('over_odds', {}).get('individual_books', []), 
                              key=lambda x: x['odds'], default={'odds': yes_odds, 'sportsbook': 'Consensus'})
                best_no = max(player.get('under_odds', {}).get('individual_books', []), 
                             key=lambda x: x['odds'], default={'odds': no_odds, 'sportsbook': 'Consensus'})
                
                best_odds_player = {
                    'player_name': player['player_name'],
                    'line_display': player['line_display'],
                    'game_info': f"{game['away_team']} @ {game['home_team']}",
                    'game_time': game['game_time_formatted'],
                    'odds_status': game.get('odds_status', 'unknown'),
                    'consensus_odds': {
                        'yes': yes_odds,
                        'no': no_odds
                    },
                    'implied_probability': {
                        'yes': round(yes_prob, 3),
                        'no': round(no_prob, 3)
                    },
                    'best_odds': {
                        'yes': {
                            'odds': best_yes['odds'],
                            'sportsbook': best_yes['sportsbook']
                        },
                        'no': {
                            'odds': best_no['odds'],
                            'sportsbook': best_no['sportsbook']
                        }
                    },
                    'sportsbook_count': player['sportsbook_count'],
                    'value_score': abs(yes_odds) if yes_odds > 150 else abs(no_odds) if no_odds > 150 else 0
                }
                
                # Add last_updated if it's cached odds
                if game.get('odds_status') == 'cached' and game.get('last_updated'):
                    best_odds_player['last_updated'] = game['last_updated']
                
                best_odds_players.append(best_odds_player)
    
    # Sort by value score (highest first) then by player name
    best_odds_players.sort(key=lambda x: (-x['value_score'], x['player_name']))
    
    return {
        'metadata': {
            **data['metadata'],
            'format': 'best_odds',
            'description': 'Best odds and value bets ranked by favorability',
            'use_case': 'Value betting, line shopping, odds comparison'
        },
        'summary': {
            **data['summary'],
            'total_entries': len(best_odds_players),
            'high_value_bets': len([p for p in best_odds_players if p['value_score'] > 200])
        },
        'players': best_odds_players
    }

def export_json_feeds(data: Dict[str, Any], args) -> Dict[str, str]:
    """Export data in multiple JSON formats"""
    
    formats = {
        'full': create_full_dataset(data),
        'summary': create_summary_dataset(data),
        'players': create_players_dataset(data),
        'best_odds': create_best_odds_dataset(data)
    }
    
    # If specific format requested, only export that one
    if args.format and args.format in formats:
        formats = {args.format: formats[args.format]}
    
    exported_files = {}
    date_str = datetime.now().strftime('%Y%m%d')
    
    for format_name, format_data in formats.items():
        if args.stdout:
            # Output to stdout
            json_output = json.dumps(format_data, indent=2 if args.pretty else None)
            print(json_output)
            exported_files[format_name] = 'stdout'
        else:
            # Export to file
            filename = f"homerun_props_{format_name}_{date_str}.json"
            
            with open(filename, 'w') as f:
                if args.pretty:
                    json.dump(format_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(format_data, f, ensure_ascii=False)
            
            exported_files[format_name] = filename
            
            # Show file info
            file_size = os.path.getsize(filename)
            size_kb = file_size / 1024
            print(f"📁 {format_name:10} → {filename:30} ({size_kb:.1f} KB)")
    
    return exported_files

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Export MLB Home Run Props JSON Feeds')
    parser.add_argument('--pretty', action='store_true', 
                       help='Pretty print JSON output')
    parser.add_argument('--stdout', action='store_true',
                       help='Output to stdout instead of files')
    parser.add_argument('--format', choices=['full', 'summary', 'players', 'best_odds'],
                       help='Export specific format only')
    
    args = parser.parse_args()
    
    print("🏠 HomeRun JSON Export - Generate JSON Feeds")
    print("=" * 45)
    
    # Validate configuration
    validate_api_key()
    
    # Fetch and process data
    print("🔍 Fetching home run props data...")
    games_data = get_games_data()
    if not games_data:
        print("❌ No games data available")
        return
    
    processed_data = process_home_run_props(games_data)
    
    if not processed_data['games']:
        print("❌ No home run props found for today")
        return
    
    # Export JSON feeds
    print(f"\n📦 Exporting JSON feeds...")
    exported_files = export_json_feeds(processed_data, args)
    
    if not args.stdout:
        print(f"\n✅ Successfully exported {len(exported_files)} JSON format(s)")
        print(f"\n💡 Usage examples:")
        for format_name, filename in exported_files.items():
            if filename != 'stdout':
                print(f"   📄 {format_name}: cat {filename}")
    
    print(f"\n🔗 API usage: Check your quota at https://the-odds-api.com/account/")

if __name__ == "__main__":
    main() 