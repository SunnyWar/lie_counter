# lie_counter
count and display days till last lie and total lies since taking power

## Overview

This project tracks false claims using a "Days Since Last Accident" style construction sign. It uses the Google Fact Check API to automatically detect false claims and update a counter displayed on a GitHub Pages site.

## Features

- **Visual Counter Display**: Yellow and black construction sign theme with digital counter
- **Automated Fact Checking**: Daily checks using Google Fact Check API
- **Historical Tracking**: Tracks lies from both presidential terms
- **Recent Lies List**: Displays the 10 most recent false claims
- **GitHub Pages**: Hosted directly from this repository

## Files

- `index.html` - GitHub Pages site with Tailwind CSS styling
- `data.json` - Data store for counter values and recent lies
- `fetch_lies.py` - Python script to check for false claims
- `.github/workflows/update-counter.yml` - GitHub Actions workflow for daily updates

## Setup

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Select "Deploy from a branch"
   - Choose "main" branch and "/" (root) folder
   - Save

2. **Configure API Key** (optional):
   - Get a Google Fact Check API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Add it as a repository secret named `GOOGLE_FACT_CHECK_API_KEY`
   - Go to Settings → Secrets and variables → Actions → New repository secret

3. **Manual Testing**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the script
   python fetch_lies.py
   ```

## How It Works

1. The GitHub Actions workflow runs daily at 9:00 AM UTC
2. The `fetch_lies.py` script queries the Google Fact Check API
3. If false claims are found in the last 24 hours:
   - Counter resets to 0
   - Term 2 counter increments
   - Recent lies list is updated
4. If no false claims are found, the counter increments by 1
5. Updated data is committed back to the repository
6. GitHub Pages automatically serves the updated site

## Data Structure

```json
{
  "days_since_lie": 0,          // Days since last detected false claim
  "term_1": 30573,              // Total lies from first term
  "term_2": 0,                  // Total lies from second term
  "recent_lies": []             // List of recent false claims
}
```

## License

MIT License - see LICENSE file for details
