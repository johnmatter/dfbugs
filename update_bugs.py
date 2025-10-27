#!/usr/bin/env python3
"""
Download Dwarf Fortress bug tracker CSV and update local SQLite database.
"""

import csv
import sqlite3
import sys
from io import StringIO
from pathlib import Path

import requests


# Configuration
CSV_URL = "https://dwarffortressbugtracker.com/csv_export.php"
DB_PATH = Path(__file__).parent / "dfbugs.db"


def create_database():
    """Create the database and bugs table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            status TEXT,
            category TEXT,
            resolution TEXT,
            severity TEXT,
            date_submitted TEXT
        )
    """)

    conn.commit()
    return conn


def download_csv():
    """Download the bug tracker CSV file."""
    print(f"Downloading CSV from {CSV_URL}...")

    try:
        response = requests.get(CSV_URL, timeout=30)
        response.raise_for_status()
        print(f"Downloaded {len(response.content)} bytes")
        # Decode with utf-8-sig to handle BOM (Byte Order Mark)
        return response.content.decode('utf-8-sig')
    except requests.RequestException as e:
        print(f"Error downloading CSV: {e}", file=sys.stderr)
        sys.exit(1)


def parse_and_update_bugs(conn, csv_content):
    """Parse CSV content and update the database."""
    cursor = conn.cursor()

    # Parse CSV
    csv_reader = csv.DictReader(StringIO(csv_content))

    bugs_added = 0
    bugs_updated = 0

    for row in csv_reader:
        # Extract the fields we want to store
        try:
            bug_data = {
                'id': row['Id'],
                'summary': row['Summary'],
                'status': row['Status'],
                'category': row['Category'],
                'resolution': row['Resolution'],
                'severity': row['Severity'],
                'date_submitted': row['Date Submitted']
            }
        except KeyError as e:
            # Debug output to see actual column names
            print(f"Error: Column {e} not found", file=sys.stderr)
            print(f"Available columns: {list(row.keys())}", file=sys.stderr)
            sys.exit(1)

        # Check if bug exists
        cursor.execute("SELECT id FROM bugs WHERE id = ?", (bug_data['id'],))
        exists = cursor.fetchone()

        # Insert or update
        cursor.execute("""
            INSERT OR REPLACE INTO bugs
            (id, summary, status, category, resolution, severity, date_submitted)
            VALUES (:id, :summary, :status, :category, :resolution, :severity, :date_submitted)
        """, bug_data)

        if exists:
            bugs_updated += 1
        else:
            bugs_added += 1

    conn.commit()
    return bugs_added, bugs_updated


def main():
    """main function"""
    print("df bugs db updater")
    print("=" * 50)

    # Create or connect to database
    conn = create_database()

    # Download CSV
    csv_content = download_csv()

    # Parse and update
    print("updating...")
    bugs_added, bugs_updated = parse_and_update_bugs(conn, csv_content)

    # Get total count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bugs")
    total_bugs = cursor.fetchone()[0]

    # Close connection
    conn.close()

    # Report results
    print("=" * 50)
    print(f"done!")
    print("")
    print(f"new bugs: {bugs_added}")
    print(f"updated bugs: {bugs_updated}")
    print(f"total bugs: {total_bugs}")
    print(f"db saved to: {DB_PATH}")

if __name__ == "__main__":
    main()
