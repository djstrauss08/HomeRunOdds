# 📅 Daily Odds Persistence Feature

## Overview

The Daily Persistence feature keeps MLB home run prop odds visible in your feed until midnight ET, even after games start and the API no longer provides live odds for those games.

## 🎯 Problem Solved

**Before:** When MLB games started, their odds would disappear from the feed because The Odds API stops providing odds for active games.

**After:** Odds remain visible with clear indicators showing whether they're live or cached from earlier in the day.

## 🔧 How It Works

### 1. Data Collection
- Every 2 hours, fresh odds are fetched from The Odds API
- Data is processed and stored in a daily cache file (`daily_homerun_cache.json`)

### 2. Cache Management
- Cache is date-based (Eastern Time) - resets at midnight ET
- Previous day's cache is automatically discarded
- Cache file is ignored by git (added to `.gitignore`)

### 3. Data Merging
When new data is fetched:
- **Live Games**: Use fresh API data (marked as 🔴 [LIVE])
- **Started Games**: Keep cached odds from earlier (marked as 💾 [CACHED])
- **New Games**: Add any new games not in cache

### 4. Status Indicators
- 🔴 **[LIVE]**: Fresh odds from API
- 💾 **[CACHED]**: Preserved odds from earlier today
- Last updated time shown for cached odds

## 📊 Benefits

1. **Complete Daily View**: See all day's games, not just currently available ones
2. **Better User Experience**: Odds don't disappear when games start
3. **Historical Context**: Know when odds were last updated
4. **Seamless Updates**: Live odds still update normally

## 🚀 Usage

### Command Line
```bash
# Run the main script (with persistence)
python3 homerun_odds.py

# Test the persistence feature
python3 test_daily_persistence.py

# Update public API feeds (with persistence)
python3 update_public_feed.py
```

### Output Example
```
🏠 HomeRun Odds - MLB Home Run Props Fetcher with Daily Persistence
======================================================================
✅ API key configured: abc12345...
✅ Loaded cached odds data from earlier today
🔍 Fetching fresh odds data from API...
🔄 Merging new data with cached odds...
    🔄 Updated odds for Yankees @ Red Sox
    💾 Preserved cached odds for Dodgers @ Giants
    💾 Preserved cached odds for Cubs @ Cardinals

📅 Found 8 MLB games for today
🔴 2 games with live odds
💾 6 games with cached odds (kept until midnight)
⚾ 120 total players with home run odds

🏟️  New York Yankees @ Boston Red Sox 🔴 [LIVE]
    07:10 PM EST
    --------------------------------------------------
    ⚾ Aaron Judge
        To Hit HR
        Yes: +450  |  No: -650
        (6 sportsbooks)

🏟️  Los Angeles Dodgers @ San Francisco Giants 💾 [CACHED]
    04:15 PM EST
    Last updated: 03:30 PM
    --------------------------------------------------
    ⚾ Mookie Betts
        To Hit HR
        Yes: +380  |  No: -520
        (5 sportsbooks)
```

## 🔄 API Integration

The daily persistence works with all existing scripts:

### JSON Exports
All JSON export formats now include:
- `odds_status`: "live" or "cached"
- `last_updated`: Timestamp for cached odds
- `live_games` and `cached_games` counts in summary

### Public API
GitHub Pages API endpoints automatically include persistence:
- `/api/v1/homerun-props.json`
- `/api/v1/summary.json`
- `/api/v1/players.json`
- `/api/v1/best-odds.json`

## 📁 Files Added/Modified

### New Files
- `test_daily_persistence.py` - Demo script
- `daily_homerun_cache.json` - Daily cache (auto-generated, gitignored)

### Modified Files
- `homerun_odds.py` - Added caching functions and merge logic
- `update_public_feed.py` - Integrated with caching system
- `export_json_feed.py` - Added odds status fields
- `.gitignore` - Added cache file

## 🔍 Technical Details

### Cache File Structure
```json
{
  "metadata": {
    "generated_at": "2025-01-16T15:30:00-05:00",
    "date": "2025-01-16",
    "timezone": "US/Eastern"
  },
  "summary": {
    "total_games": 8,
    "total_players": 120,
    "live_games": 2,
    "cached_games": 6
  },
  "games": [
    {
      "game_id": "abc123",
      "away_team": "Yankees",
      "home_team": "Red Sox",
      "odds_status": "live",
      "players": [...]
    },
    {
      "game_id": "def456", 
      "away_team": "Dodgers",
      "home_team": "Giants",
      "odds_status": "cached",
      "last_updated": "2025-01-16T15:30:00-05:00",
      "players": [...]
    }
  ]
}
```

### Merge Algorithm
1. Load existing cache for today
2. Fetch fresh data from API
3. For each game in cache:
   - If game has fresh data: Use fresh data (mark as "live")
   - If no fresh data: Keep cached data (mark as "cached")
4. Add any new games from API
5. Save merged result to cache

## 🕒 Timing

- **Cache Reset**: Midnight ET (start of new day)
- **API Updates**: Every 2 hours during active hours
- **Persistence**: Until midnight ET of same day

## 📈 GitHub Actions

The automated workflow continues to run every 2 hours, now with persistence:
- Loads previous cache if available
- Fetches fresh data
- Merges and saves to cache
- Deploys to GitHub Pages

## 🧪 Testing

```bash
# Test with existing cache
python3 test_daily_persistence.py

# Run main script to see persistence in action
python3 homerun_odds.py

# Check cache file contents
cat daily_homerun_cache.json | jq .summary
```

## 🎉 Result

Players can now see a complete picture of the day's home run props:
- Live odds for games that haven't started
- Cached odds for games that have started
- Clear indicators of data freshness
- Seamless experience throughout the day 