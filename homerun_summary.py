#!/usr/bin/env python3
"""
🏠 HomeRun Summary - Clean MLB Home Run Props Display
===================================================

Shows the most commonly offered home run prop for each player
in a clean, readable format.

Usage:
    python3 homerun_summary.py

Environment Variables:
    THE_ODDS_API_KEY - Your API key from The Odds API
"""

import os
import sys
import requests
import json
from datetime import datetime
import pytz
from collections import defaultdict
from typing import Dict, List, Any

# Import shared functions from main script
from homerun_odds import (
    validate_api_key, get_games_data, process_home_run_props,
    calculate_consensus_odds
)

def find_primary_lines(data: Dict[str, Any]) -> Dict[str, Any]:
    """Find the most commonly offered line for each player"""
    print("🔍 Finding primary home run lines for each player...")
    
    # Track line frequency across all players
    player_lines = defaultdict(lambda: defaultdict(int))
    
    for game in data['games']:
        for player in game['players']:
            player_name = player['player_name']
            line = player['line']
            sportsbook_count = player['sportsbook_count']
            
            # Weight by number of sportsbooks offering this line
            player_lines[player_name][line] += sportsbook_count
    
    # Create summary with primary lines only
    summary_data = {
        'metadata': data['metadata'].copy(),
        'summary': data['summary'].copy(),
        'games': []
    }
    
    for game in data['games']:
        if not game['players']:
            continue
            
        summary_game = {
            'game_id': game['game_id'],
            'away_team': game['away_team'],
            'home_team': game['home_team'],
            'commence_time': game['commence_time'],
            'game_time_formatted': game['game_time_formatted'],
            'players': []
        }
        
        # Get primary line for each player in this game
        seen_players = set()
        
        for player in game['players']:
            player_name = player['player_name']
            
            if player_name in seen_players:
                continue
                
            # Find the most common line for this player
            lines_count = player_lines[player_name]
            if not lines_count:
                continue
                
            primary_line = max(lines_count.keys(), key=lambda k: lines_count[k])
            
            # Find the player data with this primary line
            primary_player = None
            for p in game['players']:
                if p['player_name'] == player_name and p['line'] == primary_line:
                    primary_player = p
                    break
            
            if primary_player:
                summary_game['players'].append(primary_player)
                seen_players.add(player_name)
        
        # Sort players by name
        summary_game['players'].sort(key=lambda x: x['player_name'])
        
        if summary_game['players']:  # Only add games with players
            summary_data['games'].append(summary_game)
    
    # Update summary counts
    total_players = sum(len(game['players']) for game in summary_data['games'])
    summary_data['summary']['total_players'] = total_players
    summary_data['summary']['primary_lines_only'] = True
    
    print(f"✅ Found primary lines for {total_players} players")
    return summary_data

def display_clean_summary(data: Dict[str, Any]):
    """Display clean summary focusing on primary lines"""
    print("\n" + "="*60)
    print("🏠 MLB Home Run Props - Today's Players")
    print("="*60)
    print(f"Date: {datetime.fromisoformat(data['metadata']['generated_at']).strftime('%A, %B %d, %Y')}")
    print(f"\n📅 Found {data['summary']['total_games']} MLB games for today")
    
    if not data['games']:
        print("\n❌ No home run props available for today")
        return
    
    print(f"\n📊 PLAYER HOME RUN PROPS")
    print("="*60)
    
    total_displayed = 0
    
    for game in data['games']:
        if not game['players']:
            continue
            
        print(f"\n🏟️  {game['away_team']} @ {game['home_team']}")
        print(f"    {game['game_time_formatted']}")
        print("    " + "-"*50)
        
        for player in game['players']:
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
                total_displayed += 1
    
    print(f"\n📊 Summary: {total_displayed} players with home run props across {len(data['games'])} games")

def main():
    """Main execution function"""
    print("🏠 HomeRun Summary - Clean MLB Home Run Props Display")
    print("=" * 55)
    
    # Validate configuration
    validate_api_key()
    
    # Fetch and process data
    games_data = get_games_data()
    if not games_data:
        print("❌ No games data available")
        return
    
    # Process full data
    processed_data = process_home_run_props(games_data)
    
    # Find primary lines
    summary_data = find_primary_lines(processed_data)
    
    # Display clean summary
    display_clean_summary(summary_data)
    
    print(f"\n💡 Tip: Run 'python3 homerun_odds.py' to see all available lines")
    print(f"🔗 API usage: Check your quota at https://the-odds-api.com/account/")

if __name__ == "__main__":
    main() 