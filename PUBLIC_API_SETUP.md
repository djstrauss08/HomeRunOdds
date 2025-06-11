# 🌐 Public API Setup Guide - MLB Home Run Props

Complete step-by-step guide to deploy your MLB Home Run Props API using GitHub Pages.

## 📋 Prerequisites

* GitHub account
* The Odds API key ([get one here](https://the-odds-api.com/))
* Basic familiarity with GitHub

## 🚀 Quick Start (5 minutes)

### Step 1: Create Repository

1. Go to GitHub and create a new repository
2. Name it something like `homerun-odds` or `mlb-homerun-props`
3. Make it **Public** (required for free GitHub Pages)
4. Initialize with README

### Step 2: Upload Code

1. Download/clone this HomeRun Odds system
2. Upload all files to your new repository:
   - All `.py` files
   - `requirements.txt`
   - `.github/workflows/update-feed.yml`
   - `README.md`
   - `.gitignore`

### Step 3: Configure API Key

1. Go to your repository **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `THE_ODDS_API_KEY`
5. Value: Your actual API key from The Odds API
6. Click **Add secret**

### Step 4: Enable GitHub Pages

1. In repository **Settings**
2. Scroll to **Pages** section
3. Source: **Deploy from a branch**
4. Branch: **main**
5. Folder: **/ (root)**
6. Click **Save**

### Step 5: First Run

1. Go to **Actions** tab
2. Click **Update Home Run Props Feed**
3. Click **Run workflow** → **Run workflow**
4. Wait 2-3 minutes for completion

### Step 6: Access Your API

Your API will be available at:
```
https://your-username.github.io/your-repo-name/
```

## 📡 API Endpoints

Once deployed, you'll have these endpoints:

| Endpoint | Description | Size | Use Case |
|----------|-------------|------|----------|
| `/api/v1/homerun-props.json` | Complete dataset | ~95KB | Full analysis, dashboards |
| `/api/v1/summary.json` | Lightweight summary | ~5KB | Quick overview, mobile apps |
| `/api/v1/players.json` | Player-focused data | ~96KB | Player comparison tools |
| `/api/v1/best-odds.json` | Value bets ranked | ~8KB | Line shopping, value betting |

## 🔧 Customization Options

### Scheduling

Edit `.github/workflows/update-feed.yml` to change update frequency:

```yaml
schedule:
  # Every hour during active hours
  - cron: '0 14,15,16,17,18,19,20,21,22,23,0,1,2 * * *'
  
  # Every 30 minutes (more aggressive)
  - cron: '0,30 14-23,0-2 * * *'
  
  # Only game days (example: Tue, Wed, Thu, Fri, Sat, Sun)
  - cron: '0 14,16,18,20,22,0,2 * * 2-7'
```

### Repository Name

If you change your repository name:
1. Update the documentation URLs in `update_public_feed.py`
2. Update any hardcoded references in README files

### Custom Domain (Optional)

To use a custom domain like `api.yourdomain.com`:

1. Add a `CNAME` file to your repository root:
   ```
   api.yourdomain.com
   ```

2. Configure DNS:
   ```
   CNAME api your-username.github.io
   ```

3. In GitHub Pages settings, add your custom domain

## 🔍 Monitoring & Troubleshooting

### Check Workflow Status

1. Go to **Actions** tab
2. Look for green ✅ or red ❌ on recent runs
3. Click any run to see detailed logs

### Common Issues

**❌ "API key not set" error:**
- Check that `THE_ODDS_API_KEY` secret is properly configured
- Verify the secret name matches exactly (case-sensitive)

**❌ Workflow fails on first run:**
- Make sure all Python files are uploaded correctly
- Check that `requirements.txt` exists and contains required packages

**❌ API endpoints return 404:**
- Ensure GitHub Pages is enabled and deployed from main branch
- Check that workflow completed successfully
- Files may take 5-10 minutes to propagate after workflow completion

**❌ No data in API responses:**
- Check if it's baseball season (API returns empty during off-season)
- Verify your API key has sufficient quota
- Look at workflow logs for specific error messages

### Quota Management

Monitor your API usage:
1. Visit [The Odds API dashboard](https://the-odds-api.com/account/)
2. Check remaining quota
3. Adjust workflow frequency if needed

## 🎯 Usage Examples

### JavaScript (Fetch)

```javascript
// Get today's summary
fetch('https://your-username.github.io/homerun-odds/api/v1/summary.json')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.summary.total_players} players with home run props`);
    
    data.games.forEach(game => {
      console.log(`${game.away_team} @ ${game.home_team}: ${game.player_count} players`);
    });
  })
  .catch(error => console.error('Error:', error));
```

### Python (Requests)

```python
import requests

# Get best odds for value betting
response = requests.get('https://your-username.github.io/homerun-odds/api/v1/best-odds.json')
data = response.json()

print(f"Found {len(data['players'])} players with home run props")

# Show top 5 value bets
for player in data['players'][:5]:
    print(f"{player['player_name']}: {player['line_display']}")
    print(f"  Best Yes: {player['best_odds']['yes']['odds']} ({player['best_odds']['yes']['sportsbook']})")
    print(f"  Best No: {player['best_odds']['no']['odds']} ({player['best_odds']['no']['sportsbook']})")
    print()
```

### cURL

```bash
# Quick check of today's data
curl -s https://your-username.github.io/homerun-odds/api/v1/summary.json | jq '.summary'

# Get full dataset
curl -s https://your-username.github.io/homerun-odds/api/v1/homerun-props.json > homerun_data.json
```

## 🔒 Security Best Practices

### API Key Security

✅ **DO:**
- Store API key in GitHub Secrets only
- Use environment variables in your code
- Rotate API keys periodically
- Monitor API usage for unusual activity

❌ **DON'T:**
- Hardcode API keys in source code
- Commit API keys to version control
- Share API keys in documentation or examples
- Use the same API key across multiple projects

### Repository Security

- Keep your repository public (required for free GitHub Pages)
- Regularly update dependencies in `requirements.txt`
- Monitor workflow runs for suspicious activity
- Use branch protection if working with a team

## 📊 Performance Optimization

### File Size Optimization

The JSON files are automatically optimized:
- No pretty-printing in production files
- Minimal whitespace
- Efficient data structures

### CDN Benefits

GitHub Pages provides:
- Global CDN distribution
- Automatic compression
- SSL/HTTPS by default
- High availability

### Caching

API responses include cache headers:
```
Cache-Control: public, max-age=300
```

Consumers should respect these headers to avoid unnecessary requests.

## 🔄 Maintenance

### Regular Tasks

**Weekly:**
- Check workflow success rate
- Monitor API quota usage
- Review any error patterns in logs

**Monthly:**
- Update Python dependencies if needed
- Check for any new features in The Odds API
- Review and optimize data formats if needed

**Season Start/End:**
- Adjust workflow schedule for active season
- Update documentation with current season info
- Archive or backup historical data if needed

### Backup Strategy

Your data is automatically backed up in:
1. GitHub repository (all generated files)
2. Git history (version control)
3. GitHub Actions artifacts (temporary)

For additional backup:
```bash
# Download all current data
curl -s https://your-username.github.io/homerun-odds/api/v1/homerun-props.json > backup_$(date +%Y%m%d).json
```

## 🚀 Going Live Checklist

- [ ] Repository created and code uploaded
- [ ] API key configured in GitHub Secrets
- [ ] GitHub Pages enabled
- [ ] First workflow run completed successfully
- [ ] All API endpoints accessible
- [ ] Documentation updated with your URLs
- [ ] Monitoring set up for workflow status

## 🔗 Additional Resources

- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [JSON API Best Practices](https://jsonapi.org/)

## 💡 Tips for Success

1. **Start Simple**: Deploy with default settings first, then customize
2. **Monitor Closely**: Watch the first few workflow runs carefully
3. **Test Endpoints**: Verify all API endpoints work before sharing
4. **Document Changes**: Keep your README updated with any modifications
5. **Plan for Scale**: Consider API quota limits as your usage grows

Your MLB Home Run Props API is now ready to serve data to applications worldwide! 🌍⚾ 