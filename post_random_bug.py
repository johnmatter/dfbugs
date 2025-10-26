#!/usr/bin/env python3
"""
Post a random Dwarf Fortress bug to Bluesky.
"""

import os
import sqlite3
import sys
import warnings
from pathlib import Path

# Suppress Pydantic warning from atproto library
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from atproto import Client, client_utils
from dotenv import load_dotenv

# Configuration
DB_PATH = Path(__file__).parent / "dfbugs.db"
FILTER_STATUS = ["new", "confirmed", "acknowledged", "feedback"]  # Only post open bugs. I'm not enabling this rn though

def get_random_bug():
    """Retrieve a random bug from the database."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}", file=sys.stderr)
        print("Run update_bugs.py first to create the database.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query for a random bug with open status
    # placeholders = ','.join('?' * len(FILTER_STATUS))
    #    WHERE status IN ({placeholders})

    query = f"""
        SELECT id, summary, status, category, severity
        FROM bugs
        ORDER BY RANDOM()
        LIMIT 1
    """

    cursor.execute(query)
    # cursor.execute(query, FILTER_STATUS)
    bug = cursor.fetchone()
    conn.close()

    if not bug:
        print("No bugs found matching criteria.", file=sys.stderr)
        sys.exit(1)

    return {
        'id': bug[0],
        'summary': bug[1],
        'status': bug[2],
        'category': bug[3],
        'severity': bug[4]
    }

def format_post(bug):
    """Format the bug information for posting with proper link facets."""
    # Use TextBuilder to create post with proper facets
    tb = client_utils.TextBuilder()

    # Add bug summary
    tb.text(bug['summary'])

    # Add newlines and the tracker link as a hyperlink
    bug_url = f"https://dwarffortressbugtracker.com/view.php?id={bug['id']}"
    tb.text("\n\n")
    tb.link(bug_url, bug_url)

    return tb

def post_to_bluesky(text_builder):
    """Post text to Bluesky using credentials from environment."""
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    if not handle or not password:
        print("Error: BLUESKY_HANDLE and BLUESKY_PASSWORD must be set", file=sys.stderr)
        print("Create a .env file with your credentials (see .env.example)", file=sys.stderr)
        sys.exit(1)

    try:
        # Create client and login
        client = Client()
        client.login(handle, password)

        # Post using the TextBuilder which includes facets
        response = client.send_post(text_builder)

        print(f"Posted successfully!")
        print(f"Post URI: {response.uri}")
        return response

    except Exception as e:
        print(f"Error posting to Bluesky: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """main function"""
    # Load environment variables from .env file
    load_dotenv()

    # Get a random bug
    print("selecting...")
    bug = get_random_bug()
    print(f"selected bug #{bug['id']}: {bug['summary'][:60]}...")

    # Format the post
    post_builder = format_post(bug)
    print(f"\npost text ({len(post_builder.build_text())} characters):")
    print("-" * 50)
    print(post_builder.build_text())
    print("-" * 50)

    # Post to Bluesky
    print("\nPosting to Bluesky...")
    post_to_bluesky(post_builder)

    print("=" * 50)
    print("Done!")

if __name__ == "__main__":
    main()
