# Dwarf Fortress Bug Bot
A bot that posts random bugs from the [Dwarf Fortress bug tracker](https://dwarffortressbugtracker.com)

https://bsky.app/profile/dwarffortressbugs.bsky.social

Inspired by DwarfFortBugs on twitter (rip)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Bluesky Credentials
You should probably use an App Password instead of your main password:
- Go to Bluesky Settings > Privacy and Security > App Passwords
- Create a new app password for this bot

```bash
cp .env.example .env
```

add your Bluesky credentials:
```
BLUESKY_HANDLE=your-handle.bsky.social
BLUESKY_PASSWORD=your-password
```


### 3. Initialize the Database
```bash
python update_bugs.py
```

## Usage

### Update
Run whenever you want to refresh the bug data:
```bash
python update_bugs.py
```

The script performs incremental updates–it adds new bugs and updates existing ones without removing old entries.

### Post Random Bug to Bluesky
```bash
python post_random_bug.py
```
