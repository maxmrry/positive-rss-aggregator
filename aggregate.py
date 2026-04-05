import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pytz
import os
import re

# --- CONFIGURATION ---
FEEDS = [
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCp6COGFcWCnEx9JbPIoYJLw",
]

KEYWORDS = ['affirmation', 'affirmations', 'positive']

TIMEZONE = pytz.timezone('Europe/Paris')
REMINDER_HOUR = 23
REMINDER_MINUTE = 0
# ---------------------

def count_keyword_matches(text, keywords):
    """Count whole-word keyword matches (case-insensitive)."""
    return sum(
        1 for kw in keywords
        if re.search(rf'\b{kw}\b', text, re.IGNORECASE)
    )

def is_relevant(title, desc):
    """Weighted relevance check."""
    title_matches = count_keyword_matches(title, KEYWORDS)
    desc_matches = count_keyword_matches(desc, KEYWORDS)

    # ✅ Strong signal: title match
    if title_matches >= 1:
        return True

    # ⚠️ Weak signal: require stronger match in description
    if desc_matches >= 2:
        return True

    return False

def main():
    fg = FeedGenerator()
    fg.title('Filtered Positive Feed')
    fg.link(href='https://maxmrry.github.io/positive-rss-aggregator/feed.xml', rel='self')
    fg.description('Aggregated YouTube feeds with daily reminders.')

    all_entries = []

    cutoff = datetime.now(TIMEZONE) - timedelta(days=14)

    # 1. Fetch and Filter YouTube Feeds
    for url in FEEDS:
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            title = entry.get('title', '')
            desc = entry.get('summary', '')

            pub_date = date_parser.parse(entry.published)

            if is_relevant(title, desc) and pub_date >= cutoff:
                all_entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.get('summary', ''),
                    'published': pub_date,
                    'id': entry.id
                })

    # 2. Add Daily Reminders
    now = datetime.now(TIMEZONE)

    for i in range(3):
        target_date = now - timedelta(days=i)
        reminder_time = target_date.replace(
            hour=REMINDER_HOUR,
            minute=REMINDER_MINUTE,
            second=0,
            microsecond=0
        )

        if now >= reminder_time or i > 0:
            all_entries.append({
                'title': '✅ Remember to do daily positive affirmations',
                'link': '',
                'description': '',
                'published': reminder_time,
                'id': f"reminder-{reminder_time.strftime('%Y%m%d')}"
            })

    # 3. Sort entries
    all_entries.sort(key=lambda x: x['published'], reverse=True)

    # 4. Build RSS
    for item in all_entries:
        fe = fg.add_entry()
        fe.title(item['title'])

        if item['link']:
            fe.link(href=item['link'])

        if item['description']:
            fe.description(item['description'])

        fe.pubDate(item['published'])
        fe.id(item['id'])

    # 5. Save
    os.makedirs('docs', exist_ok=True)
    fg.rss_file('docs/feed.xml')

if __name__ == "__main__":
    main()
