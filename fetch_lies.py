#!/usr/bin/env python3
"""
Fetch lies from Google Fact Check API and update the counter.
This script checks for false claims about Donald Trump in the last 24 hours.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import requests


def load_data() -> Dict[str, Any]:
    """Load the current data from data.json"""
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: data.json not found. Creating default data.")
        default_data = {
            "days_since_lie": 0,
            "term_1": 30573,
            "term_2": 0,
            "recent_lies": []
        }
        save_data(default_data)
        return default_data
    except json.JSONDecodeError as e:
        print(f"Error: data.json is malformed: {e}")
        raise


def save_data(data: Dict[str, Any]) -> None:
    """Save updated data to data.json"""
    try:
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error: Failed to write data.json: {e}")
        raise


def fetch_fact_checks(api_key: str, query: str = "Donald Trump") -> List[Dict[str, Any]]:
    """
    Fetch fact checks from Google Fact Check API
    
    Args:
        api_key: Google API key
        query: Search query (default: "Donald Trump")
    
    Returns:
        List of fact check claims
    """
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "key": api_key,
        "query": query,
        "languageCode": "en"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("claims", [])
    except requests.RequestException as e:
        print(f"Error fetching fact checks: {e}")
        return []


def check_for_recent_false_claims(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check if there are any false claims in the last 24 hours
    
    Args:
        claims: List of fact check claims
    
    Returns:
        List of false claims from the last 24 hours
    """
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(days=1)
    recent_false_claims = []
    
    for claim in claims:
        # Check if claim has review data
        if "claimReview" not in claim:
            continue
            
        for review in claim["claimReview"]:
            # Parse the review date
            review_date_str = review.get("reviewDate")
            if not review_date_str:
                continue
                
            try:
                # Handle ISO format date
                review_date = datetime.fromisoformat(review_date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                continue
            
            # Check if review is within last 24 hours
            if review_date < cutoff_time:
                continue
            
            # Check if rating indicates false claim
            rating = review.get("textualRating", "").lower()
            if any(term in rating for term in ["false", "pants on fire", "lie", "incorrect", "wrong"]):
                recent_false_claims.append({
                    "date": review_date.strftime("%Y-%m-%d"),
                    "claim": claim.get("text", "Unknown claim"),
                    "rating": review.get("textualRating", "Unknown"),
                    "source": review.get("publisher", {}).get("name", "Unknown source"),
                    "url": review.get("url", "")
                })
    
    return recent_false_claims


def update_counter(data: Dict[str, Any], false_claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Update the counter based on whether false claims were found
    
    Args:
        data: Current data dictionary
        false_claims: List of recent false claims
    
    Returns:
        Updated data dictionary
    """
    if false_claims:
        # Reset counter to 0 if false claims found
        data["days_since_lie"] = 0
        data["term_2"] += len(false_claims)
        
        # Add to recent lies (keep last 10)
        for claim in false_claims:
            data["recent_lies"].insert(0, claim)
        data["recent_lies"] = data["recent_lies"][:10]
        
        print(f"Found {len(false_claims)} false claim(s). Counter reset to 0.")
    else:
        # Increment counter if no false claims found
        data["days_since_lie"] += 1
        print(f"No false claims found. Counter incremented to {data['days_since_lie']}.")
    
    return data


def main():
    """Main function to run the lie counter update"""
    # Get API key from environment variable
    api_key = os.environ.get("GOOGLE_FACT_CHECK_API_KEY")
    
    if not api_key:
        print("Warning: GOOGLE_FACT_CHECK_API_KEY not set. Skipping API check.")
        print("Counter will be incremented without checking for new lies.")
        
        # Load and increment counter without API check
        data = load_data()
        data["days_since_lie"] += 1
        save_data(data)
        print(f"Counter incremented to {data['days_since_lie']} (no API check performed).")
        return
    
    # Load current data
    data = load_data()
    
    # Fetch fact checks
    claims = fetch_fact_checks(api_key)
    
    if not claims:
        print("No claims returned from API. Incrementing counter by default.")
        data["days_since_lie"] += 1
        save_data(data)
        return
    
    # Check for recent false claims
    false_claims = check_for_recent_false_claims(claims)
    
    # Update counter
    data = update_counter(data, false_claims)
    
    # Save updated data
    save_data(data)
    
    print("Data updated successfully!")


if __name__ == "__main__":
    main()
