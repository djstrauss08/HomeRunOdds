#!/usr/bin/env python3
"""
🏠 Update Public Feed - Generate Public API Endpoints
====================================================

Creates public API endpoints and documentation for MLB home run props.
Used by GitHub Actions to generate static API files for GitHub Pages.

Usage:
    python3 update_public_feed.py

Environment Variables:
    THE_ODDS_API_KEY - Your API key from The Odds API
"""

import os
import sys
import json
import shutil
from datetime import datetime
import pytz
from pathlib import Path

# Import functions from other scripts
from homerun_odds import (
    validate_api_key, get_games_data, process_home_run_props,
    load_daily_cache, save_daily_cache, merge_with_cached_data
)
from export_json_feed import (
    create_full_dataset, create_summary_dataset, 
    create_players_dataset, create_best_odds_dataset
)

def create_api_directories():
    """Create the API directory structure"""
    directories = [
        'public',
        'public/api',
        'public/api/v1'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("📁 Created API directory structure")

def generate_api_endpoints(data):
    """Generate all API endpoint JSON files"""
    endpoints = {
        'homerun-props.json': create_full_dataset(data),
        'summary.json': create_summary_dataset(data),
        'players.json': create_players_dataset(data),
        'best-odds.json': create_best_odds_dataset(data)
    }
    
    file_sizes = {}
    
    for filename, endpoint_data in endpoints.items():
        filepath = f"public/api/v1/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(endpoint_data, f, ensure_ascii=False, separators=(',', ':'))
        
        # Get file size
        file_size = os.path.getsize(filepath)
        file_sizes[filename] = file_size / 1024  # Convert to KB
        
        print(f"📄 Generated {filename:20} ({file_sizes[filename]:.1f} KB)")
    
    return file_sizes

def create_cors_headers():
    """Create CORS headers file for GitHub Pages"""
    headers_content = """/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, HEAD, OPTIONS
  Access-Control-Allow-Headers: Content-Type
  Access-Control-Max-Age: 86400

/api/*
  Content-Type: application/json
  Cache-Control: public, max-age=300
"""
    
    with open('public/_headers', 'w') as f:
        f.write(headers_content)
    
    print("🔧 Created CORS headers configuration")

def generate_documentation_page(data, file_sizes):
    """Generate the main documentation HTML page"""
    
    eastern = pytz.timezone('US/Eastern')
    last_updated = datetime.now(eastern).strftime('%Y-%m-%d %I:%M %p %Z')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏠 MLB Home Run Props JSON API</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .endpoint {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }}
        .endpoint code {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 8px 12px;
            border-radius: 4px;
            display: inline-block;
            font-weight: bold;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #3498db;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ opacity: 0.9; }}
        .code-block {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        .update-time {{
            background: #27ae60;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            display: inline-block;
            margin: 10px 0;
        }}
        .use-case {{
            background: #f39c12;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.9em;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 MLB Home Run Props JSON API</h1>
        
        <div class="update-time">
            Last updated: {last_updated}
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{data['summary']['total_games']}</div>
                <div class="stat-label">MLB Games</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['summary']['games_with_props']}</div>
                <div class="stat-label">Games with Props</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['summary']['total_players']}</div>
                <div class="stat-label">Players with Home Run Odds</div>
            </div>
        </div>

        <h2>📡 Available Endpoints</h2>

        <div class="endpoint">
            <h3>Full Home Run Props Data</h3>
            <code>GET /api/v1/homerun-props.json</code>
            <span class="use-case">Full data analysis, comprehensive dashboards</span>
            <p>Complete dataset with all games, players, lines, and odds from multiple sportsbooks.</p>
            <p><strong>Size:</strong> ~{file_sizes.get('homerun-props.json', 0):.1f} KB</p>
        </div>

        <div class="endpoint">
            <h3>Summary Data</h3>
            <code>GET /api/v1/summary.json</code>
            <span class="use-case">Quick overview, mobile apps, initial page loads</span>
            <p>Lightweight summary with game info and player counts (no odds data).</p>
            <p><strong>Size:</strong> ~{file_sizes.get('summary.json', 0):.1f} KB</p>
        </div>

        <div class="endpoint">
            <h3>Players Only</h3>
            <code>GET /api/v1/players.json</code>
            <span class="use-case">Player comparison tools, fantasy apps</span>
            <p>All player props with game context, optimized for player-focused views.</p>
            <p><strong>Size:</strong> ~{file_sizes.get('players.json', 0):.1f} KB</p>
        </div>

        <div class="endpoint">
            <h3>Best Odds</h3>
            <code>GET /api/v1/best-odds.json</code>
            <span class="use-case">Value betting, line shopping, odds comparison</span>
            <p>Best odds and value bets ranked by favorability across all sportsbooks.</p>
            <p><strong>Size:</strong> ~{file_sizes.get('best-odds.json', 0):.1f} KB</p>
        </div>

        <h2>🚀 Usage Examples</h2>

        <h3>JavaScript/Fetch</h3>
        <div class="code-block">
fetch('https://your-username.github.io/homerun-odds/api/v1/summary.json')
  .then(response => response.json())
  .then(data => {{
    console.log(`${{data.summary.total_players}} players across ${{data.summary.total_games}} games`);
    
    data.games.forEach(game => {{
      console.log(`${{game.away_team}} @ ${{game.home_team}} - ${{game.player_count}} players`);
    }});
  }});
        </div>

        <h3>Python</h3>
        <div class="code-block">
import requests

response = requests.get('https://your-username.github.io/homerun-odds/api/v1/players.json')
data = response.json()

for player in data['players']:
    print(f"{{player['player_name']}}: {{player['line_display']}}")
        </div>

        <h3>cURL</h3>
        <div class="code-block">
curl -H "Accept: application/json" \\
     https://your-username.github.io/homerun-odds/api/v1/best-odds.json
        </div>

        <h2>📊 Response Format</h2>
        <p>All endpoints return JSON with consistent structure:</p>
        <ul>
            <li><code>metadata</code>: Generation timestamp, date, timezone</li>
            <li><code>summary</code>: Total counts and statistics</li>
            <li><code>games</code> or <code>players</code>: Main data arrays</li>
        </ul>

        <h2>⚡ Rate Limiting</h2>
        <p>No rate limiting on these endpoints. Data is cached and served statically.</p>

        <h2>🔗 CORS</h2>
        <p>All endpoints support CORS for browser-based applications.</p>

        <h2>📈 Data Updates</h2>
        <p>Data is automatically updated every 2 hours during baseball season (10 AM - 10 PM ET).</p>
        
        <h2>🏠 About</h2>
        <p>This API provides MLB home run prop betting odds with consensus pricing across multiple sportsbooks. 
        Data is sourced from The Odds API and processed to provide clean, consistent formatting for developers and analysts.</p>
        
        <p><strong>Built with:</strong> Python, The Odds API, GitHub Actions, GitHub Pages</p>
    </div>
</body>
</html>"""
    
    with open('public/index.html', 'w') as f:
        f.write(html_content)
    
    print("📄 Generated documentation page")

def copy_to_root():
    """Copy public files to root for GitHub Pages"""
    
    # Copy API files to root api directory
    if os.path.exists('api'):
        shutil.rmtree('api')
    shutil.copytree('public/api', 'api')
    
    # Copy index.html to root
    if os.path.exists('public/index.html'):
        shutil.copy('public/index.html', 'index.html')
    
    # Copy headers file
    if os.path.exists('public/_headers'):
        shutil.copy('public/_headers', '_headers')
    
    print("📋 Copied files to root for GitHub Pages deployment")

def main():
    """Main execution function"""
    print("🏠 Update Public Feed - Generate Public API Endpoints with Daily Persistence")
    print("=" * 75)
    
    # Validate configuration
    validate_api_key()
    
    # Load cached data from earlier today
    cached_data = load_daily_cache()
    
    # Fetch fresh data from API
    print("🔍 Fetching fresh home run props data from API...")
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
        # No data at all - create empty structure
        print("❌ No games data available and no cached data")
        eastern = pytz.timezone('US/Eastern')
        final_data = {
            'metadata': {
                'generated_at': datetime.now(eastern).isoformat(),
                'date': datetime.now(eastern).strftime('%Y-%m-%d'),
                'timezone': 'US/Eastern',
                'sport': 'baseball_mlb',
                'market': 'batter_home_runs',
                'note': 'No data available'
            },
            'summary': {
                'total_games': 0,
                'games_with_props': 0,
                'total_players': 0,
                'live_games': 0,
                'cached_games': 0
            },
            'games': []
        }

    # Create directory structure
    create_api_directories()
    
    # Generate API endpoints
    print("\n📡 Generating API endpoints...")
    file_sizes = generate_api_endpoints(final_data)
    
    # Create CORS headers
    create_cors_headers()
    
    # Generate documentation
    print("\n📚 Generating documentation...")
    generate_documentation_page(final_data, file_sizes)
    
    # Copy to root for GitHub Pages
    copy_to_root()
    
    print(f"\n✅ Successfully generated public API feed with daily persistence")
    print(f"📊 Summary: {final_data['summary']['total_players']} players across {final_data['summary']['total_games']} games")
    
    # Show persistence info
    if 'live_games' in final_data['summary']:
        live_count = final_data['summary']['live_games']
        cached_count = final_data['summary']['cached_games']
        print(f"🔴 {live_count} games with live odds")
        print(f"💾 {cached_count} games with cached odds (preserved until midnight)")
    
    print(f"🌐 API endpoints ready for deployment")

if __name__ == "__main__":
    main() 