# 🏠 HomeRun Odds - MLB Home Run Props API

A comprehensive system for fetching, analyzing, and distributing MLB home run props data with consensus odds from multiple sportsbooks.

## 🚀 Features

* **Real-time Data**: Live odds from 6+ major sportsbooks via The Odds API
* **Consensus Odds**: Mathematically averaged odds across all available books
* **Multiple Formats**: JSON exports optimized for different use cases
* **Public API**: Hosted endpoints for other websites and applications
* **Automatic Updates**: GitHub Actions workflow for scheduled data refreshes
* **Clean Interface**: Beautiful summary views and detailed analysis tools

## 📊 What You Get

### Data Coverage

* All MLB games for today (Eastern timezone)
* Player home run props with multiple sportsbooks
* Individual sportsbook odds + consensus averages
* Sportsbook availability counts and comparisons

### Export Formats

* **Full Dataset**: Complete odds data with all sportsbooks
* **Summary View**: Game info and player counts (lightweight)
* **Player Focus**: Optimized for player comparison tools
* **Best Odds**: Top value bets ranked by favorability

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key (REQUIRED)

**🔐 IMPORTANT: Your API key should be set as an environment variable, never hardcoded.**

Get your API key from The Odds API, then:

```bash
# Set environment variable (replace with your actual key)
export THE_ODDS_API_KEY="your-api-key-here"
```

For permanent setup, add to your shell profile:

```bash
echo 'export THE_ODDS_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Test the Setup

```bash
# Verify environment variable
echo $THE_ODDS_API_KEY

# Test basic functionality
python3 homerun_summary.py
```

## 🎯 Usage

### Basic Analysis

```bash
# Clean summary view (most commonly offered props per player)
python3 homerun_summary.py

# Detailed analysis with all available lines
python3 homerun_odds.py
```

### JSON Export

```bash
# Export to file
python3 export_json_feed.py

# Export with pretty formatting
python3 export_json_feed.py --pretty

# Output to stdout (for piping)
python3 export_json_feed.py --stdout

# Export specific format only
python3 export_json_feed.py --format summary
```

### Public API Generation

```bash
# Generate public API endpoints
python3 update_public_feed.py
```

## 📡 Public API

Once deployed, your API provides multiple endpoints:

* `/api/v1/homerun-props.json` - Full dataset (~95KB)
* `/api/v1/summary.json` - Lightweight summary (~5KB)
* `/api/v1/players.json` - Player-focused data (~96KB)
* `/api/v1/best-odds.json` - Best odds rankings (~8KB)

### Example Usage

```javascript
fetch('https://your-username.github.io/HomeRunOdds/api/v1/summary.json')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.summary.total_players} players across ${data.summary.total_games} games`);
  });
```

## 🔄 Automatic Updates

GitHub Actions workflow runs every 2 hours during baseball season (10 AM - 10 PM ET) to:

* Fetch fresh data from The Odds API
* Update JSON endpoints
* Commit changes to repository
* Deploy via GitHub Pages

## 📈 Key Benefits

### For You

* 🔒 **Control API costs** - You decide when to fetch data
* ⚙️ **Process data your way** - Custom consensus calculations
* 📊 **Rich analytics** - Multiple view formats for different needs
* 🚀 **Easy deployment** - One-click GitHub Pages hosting

### For Others

* 🆓 **Free access** - No API keys needed for consumers
* ⚡ **Fast delivery** - Global CDN via GitHub Pages
* 🌐 **CORS enabled** - Works from any website
* 📱 **Multiple formats** - Choose the right endpoint for your needs

## 🛡️ Security Features

* Environment variable configuration for API keys
* GitHub Secrets integration for automated workflows
* API key never exposed in public code
* Easy key rotation and management

## 📚 Documentation

* `PUBLIC_API_SETUP.md` - Complete deployment guide
* `SECURITY_SETUP.md` - API key security configuration
* `README_JSON_Export.md` - JSON export system details

## 🎯 Use Cases

**Your Internal Analysis:**

* Daily betting research and value identification
* Sportsbook comparison and line shopping
* Historical tracking and trend analysis

**Public API Consumers:**

* Betting analysis websites and tools
* Fantasy baseball applications
* Discord bots and notifications
* Mobile apps and dashboards
* Academic research and data visualization

## 📊 Example Output

Shows the most commonly offered home run props across sportsbooks:

```
🏠 MLB Home Run Props - Today's Players
============================================================
Date: Tuesday, June 03, 2025

📅 Found 15 MLB games for today

📊 PLAYER HOME RUN PROPS
============================================================

🏟️  Colorado Rockies @ Miami Marlins
    06:40 PM EDT
    --------------------------------------------------
    ⚾ Mike Trout
        To Hit HR
        Yes: +450  |  No: -650
        (6 sportsbooks)

```

## 🔧 Advanced Features

* **Consensus Calculation**: Converts odds to implied probabilities, averages, then back to American odds
* **Multiple Lines**: Handles different home run props for the same player
* **Primary Line Detection**: Shows most commonly offered prop across books
* **Error Handling**: Graceful handling of missing props or API issues
* **Timezone Management**: Proper Eastern timezone handling for game times

## 📞 Support

For issues related to:

* **The Odds API**: Contact their support for API-related questions
* **This Tool**: Open an issue in this repository
* **GitHub Pages**: Check GitHub's documentation for hosting issues

## 🔄 Migration from Strikeout Props

This system follows the same proven architecture as the StrikeoutCenter project but is optimized for home run betting markets:

* Same API patterns and error handling
* Same JSON export formats and endpoints
* Same GitHub Actions automation
* Same security and deployment model

Built with ❤️ for the baseball analytics community 