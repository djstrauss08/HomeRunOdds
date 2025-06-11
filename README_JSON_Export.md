# 📊 JSON Export System - Technical Documentation

Comprehensive guide to the MLB Home Run Props JSON export system, data formats, and API endpoints.

## 🏗️ System Architecture

```
homerun_odds.py          → Raw data fetching from The Odds API
       ↓
process_home_run_props() → Data processing and consensus calculation
       ↓
export_json_feed.py      → Multiple format generation
       ↓
update_public_feed.py    → Public API endpoint creation
       ↓
GitHub Pages             → Static API hosting
```

## 📁 Data Flow

1. **Data Ingestion**: `homerun_odds.py` fetches live data from The Odds API
2. **Processing**: Raw API data is cleaned, structured, and consensus odds calculated
3. **Format Generation**: Multiple optimized JSON formats created for different use cases
4. **Public API**: Static JSON files deployed to GitHub Pages with CORS headers
5. **Consumption**: External applications access data via RESTful endpoints

## 📋 Export Formats

### 1. Full Dataset (`homerun-props.json`)

**Purpose**: Complete dataset with all available data
**Size**: ~95KB
**Use Cases**: Comprehensive analysis, data warehousing, full dashboards

**Structure**:
```json
{
  "metadata": {
    "generated_at": "2025-01-16T15:30:00-05:00",
    "date": "2025-01-16",
    "timezone": "US/Eastern",
    "sport": "baseball_mlb",
    "market": "batter_home_runs",
    "format": "full_dataset",
    "description": "Complete home run props with all sportsbooks and lines"
  },
  "summary": {
    "total_games": 15,
    "games_with_props": 12,
    "total_players": 180
  },
  "games": [
    {
      "game_id": "abc123...",
      "away_team": "Colorado Rockies",
      "home_team": "Miami Marlins",
      "commence_time": "2025-01-16T23:40:00-05:00",
      "game_time_formatted": "06:40 PM EST",
      "players": [
        {
          "player_name": "Mike Trout",
          "line": 0.5,
          "line_display": "To Hit HR",
          "sportsbook_count": 6,
          "sportsbooks": ["DraftKings", "FanDuel", "BetMGM", "..."],
          "over_odds": {
            "consensus": 450,
            "individual_books": [
              {"sportsbook": "DraftKings", "odds": 425},
              {"sportsbook": "FanDuel", "odds": 475}
            ]
          },
          "under_odds": {
            "consensus": -650,
            "individual_books": [...]
          },
          "odds_by_book": {
            "DraftKings": {"over": 425, "under": -625},
            "FanDuel": {"over": 475, "under": -675}
          }
        }
      ]
    }
  ]
}
```

### 2. Summary (`summary.json`)

**Purpose**: Lightweight overview without detailed odds
**Size**: ~5KB
**Use Cases**: Mobile apps, initial page loads, quick overviews

**Structure**:
```json
{
  "metadata": {
    "format": "summary",
    "description": "Lightweight summary with game info and player counts"
  },
  "summary": {
    "total_games": 15,
    "games_with_props": 12,
    "total_players": 180
  },
  "games": [
    {
      "game_id": "abc123...",
      "away_team": "Colorado Rockies",
      "home_team": "Miami Marlins",
      "commence_time": "2025-01-16T23:40:00-05:00",
      "game_time_formatted": "06:40 PM EST",
      "player_count": 15,
      "players": [
        {
          "player_name": "Mike Trout",
          "line_display": "To Hit HR",
          "sportsbook_count": 6
        }
      ]
    }
  ]
}
```

### 3. Players Focus (`players.json`)

**Purpose**: Player-centric view with game context
**Size**: ~96KB
**Use Cases**: Player comparison tools, fantasy applications, player-specific analysis

**Structure**:
```json
{
  "metadata": {
    "format": "players",
    "description": "All player props with game context"
  },
  "summary": {
    "total_games": 15,
    "games_with_props": 12,
    "total_players": 180,
    "total_entries": 180
  },
  "players": [
    {
      "player_name": "Aaron Judge",
      "line": 0.5,
      "line_display": "To Hit HR",
      "sportsbook_count": 6,
      "over_odds": {...},
      "under_odds": {...},
      "game_context": {
        "game_id": "xyz789...",
        "away_team": "New York Yankees",
        "home_team": "Boston Red Sox",
        "commence_time": "2025-01-16T20:10:00-05:00",
        "game_time_formatted": "03:10 PM EST"
      }
    }
  ]
}
```

### 4. Best Odds (`best-odds.json`)

**Purpose**: Value betting and line shopping optimization
**Size**: ~8KB
**Use Cases**: Arbitrage detection, value betting, odds comparison

**Structure**:
```json
{
  "metadata": {
    "format": "best_odds",
    "description": "Best odds and value bets ranked by favorability"
  },
  "summary": {
    "total_games": 15,
    "games_with_props": 12,
    "total_players": 180,
    "total_entries": 180,
    "high_value_bets": 23
  },
  "players": [
    {
      "player_name": "Mike Trout",
      "line_display": "To Hit HR",
      "game_info": "Colorado Rockies @ Miami Marlins",
      "game_time": "06:40 PM EST",
      "consensus_odds": {
        "yes": 450,
        "no": -650
      },
      "implied_probability": {
        "yes": 0.182,
        "no": 0.867
      },
      "best_odds": {
        "yes": {"odds": 475, "sportsbook": "FanDuel"},
        "no": {"odds": -625, "sportsbook": "DraftKings"}
      },
      "sportsbook_count": 6,
      "value_score": 475
    }
  ]
}
```

## 🔧 Technical Specifications

### Consensus Odds Calculation

```python
def calculate_consensus_odds(odds_list):
    """
    1. Convert American odds to implied probabilities
    2. Calculate average probability across all sportsbooks
    3. Convert average probability back to American odds
    """
    probabilities = [american_to_probability(odds) for odds in odds_list]
    avg_probability = sum(probabilities) / len(probabilities)
    return probability_to_american(avg_probability)
```

### Data Quality Standards

- **Completeness**: All available sportsbooks included
- **Accuracy**: Real-time data with proper error handling
- **Consistency**: Standardized player names and team identifiers
- **Freshness**: Data updated every 2 hours during active season

### Performance Optimizations

- **Minified JSON**: No unnecessary whitespace in production
- **Efficient Structures**: Optimized for fast parsing and small size
- **CDN Delivery**: GitHub Pages provides global distribution
- **Compression**: Automatic gzip compression

## 🎯 Usage Patterns

### JavaScript Applications

```javascript
// Load summary for quick overview
const summary = await fetch('/api/v1/summary.json').then(r => r.json());

// Load specific player data
const players = await fetch('/api/v1/players.json').then(r => r.json());
const playerData = players.players.find(p => p.player_name === 'Mike Trout');

// Find best odds for arbitrage
const bestOdds = await fetch('/api/v1/best-odds.json').then(r => r.json());
const arbitrageOpps = bestOdds.players.filter(p => p.value_score > 500);
```

### Python Analytics

```python
import requests
import pandas as pd

# Load data into DataFrame
response = requests.get('https://api.example.com/api/v1/homerun-props.json')
data = response.json()

# Convert to DataFrame for analysis
players_data = []
for game in data['games']:
    for player in game['players']:
        player['game_info'] = f"{game['away_team']} @ {game['home_team']}"
        players_data.append(player)

df = pd.DataFrame(players_data)
```

### Mobile Applications

```swift
// Swift example for iOS
struct HomeRunAPI {
    static func loadSummary() async throws -> SummaryData {
        let url = URL(string: "https://api.example.com/api/v1/summary.json")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(SummaryData.self, from: data)
    }
}
```

## 🚀 API Optimization Strategies

### Caching Strategy

```
Cache-Control: public, max-age=300  # 5 minutes
```

### Error Handling

All endpoints gracefully handle:
- Empty data during off-season
- Partial API failures
- Missing sportsbook data
- Invalid player names

### Rate Limiting

- **GitHub Pages**: No rate limiting (static files)
- **Source API**: Respects The Odds API quotas
- **Recommended**: Client-side caching to reduce requests

## 📊 Data Schema Reference

### Player Object

```typescript
interface Player {
  player_name: string;           // "Mike Trout"
  line: number;                  // 0.5 (for "to hit HR")
  line_display: string;          // "To Hit HR"
  sportsbook_count: number;      // 6
  sportsbooks: string[];         // ["DraftKings", "FanDuel", ...]
  over_odds: OddsData;          // Yes/Over odds data
  under_odds: OddsData;         // No/Under odds data
  odds_by_book: BookOdds;       // Individual sportsbook odds
}

interface OddsData {
  consensus: number;             // -150
  individual_books: BookOdd[];   // Individual sportsbook entries
}

interface BookOdd {
  sportsbook: string;           // "DraftKings"
  odds: number;                 // -145
}
```

### Game Object

```typescript
interface Game {
  game_id: string;              // Unique identifier
  away_team: string;            // "Colorado Rockies"
  home_team: string;            // "Miami Marlins"
  commence_time: string;        // ISO 8601 timestamp
  game_time_formatted: string;  // "06:40 PM EST"
  players: Player[];            // Array of player props
}
```

## 🔍 Quality Assurance

### Automated Testing

- **Data Validation**: Schema compliance checking
- **Odds Verification**: Consensus calculation accuracy
- **Format Testing**: JSON structure validation
- **Performance Testing**: File size and load time monitoring

### Manual Review

- **Player Name Accuracy**: Consistent spelling and formatting
- **Team Name Standardization**: Official team names
- **Timezone Handling**: Proper EST/EDT conversion
- **Edge Case Handling**: Empty data, single sportsbook scenarios

## 📈 Analytics & Monitoring

### Usage Metrics

Track via GitHub Pages analytics:
- Endpoint popularity
- Geographic distribution
- Peak usage times
- Error rates

### Data Quality Metrics

- **Coverage**: Percentage of games with props
- **Completeness**: Average sportsbooks per player
- **Freshness**: Time since last update
- **Accuracy**: Consensus vs individual book variance

## 🔄 Maintenance Procedures

### Daily Tasks

- Monitor workflow execution
- Check data quality metrics
- Review error logs

### Weekly Tasks

- Analyze usage patterns
- Update documentation
- Review sportsbook coverage

### Seasonal Tasks

- Adjust scheduling for season start/end
- Archive historical data
- Update team rosters and names

This JSON export system provides a robust, scalable foundation for MLB home run props data distribution. The multi-format approach ensures optimal performance for diverse use cases while maintaining data quality and reliability. 