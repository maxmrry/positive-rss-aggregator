import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pytz
import os

# --- CONFIGURATION ---
FEEDS = [
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCp6COGFcWCnEx9JbPIoYJLw",
    # Add more YouTube RSS links here
]

# The "Gate": Only allow entries containing these words
KEYWORDS = ['affirmation', 'affirmations', 'positive'] 

# Reminder Configuration
TIMEZONE = pytz.timezone('Europe/Paris')
REMINDER_HOUR = 23   # 11 PM France
REMINDER_MINUTE = 0
# ---------------------

def main():
    fg = FeedGenerator()
    fg.title('Filtered Positive Feed')
    fg.link(href='https://maxmrry.github.io/positive-rss-aggregator/feed.xml', rel='self')
    fg.description('Aggregated YouTube feeds with daily reminders.')

    all_entries = []

    # 1. Fetch and Filter YouTube Feeds
    for url in FEEDS:
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            title = entry.get('title', '').lower()
            desc = entry.get('summary', '').lower()
            
            # Filter logic: Check if any keyword is in the title or description
            if any(kw in title or kw in desc for kw in KEYWORDS):
                pub_date = date_parser.parse(entry.published)
                
                all_entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.get('summary', ''),
                    'published': pub_date,
                    'id': entry.id
                })

    # 2. Add Daily Reminders
    now = datetime.now(TIMEZONE)
    
    # Generate reminders for the last 3 days to ensure they persist in the feed for a bit
    for i in range(3):
        target_date = now - timedelta(days=i)
        reminder_time = target_date.replace(hour=REMINDER_HOUR, minute=REMINDER_MINUTE, second=0, microsecond=0)
        
        # Only add today's reminder if the current time has actually passed the scheduled time
        if now >= reminder_time or i > 0:
            all_entries.append({
                'title': '✅ Remember to do daily positive affirmations',
                'link': '',  # No link
                'description': '',  # No extra text
                'published': reminder_time,
                'id': f"reminder-{reminder_time.strftime('%Y%m%d')}"
            })

    # 3. Sort entries chronologically (newest first)
    all_entries.sort(key=lambda x: x['published'], reverse=True)

    # 4. Build the final RSS feed
    for item in all_entries:
        fe = fg.add_entry()
        fe.title(item['title'])
        fe.link(href=item['link'])
        fe.description(item['description'])
        fe.pubDate(item['published'])
        fe.id(item['id'])

    # 5. Save Feed to the docs folder
    os.makedirs('docs', exist_ok=True)
    fg.rss_file('docs/feed.xml')

if __name__ == "__main__":
    main()
