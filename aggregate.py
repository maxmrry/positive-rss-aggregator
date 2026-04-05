import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pytz
import os
import re

# --- CONFIGURATION ---
FEEDS = [
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCE6acMV3m35znLcf0JGNn7Q", # gibiasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCsr9ZL41tukMWLrqK-Edqaw", # kjtingles
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCVtQes1mJsOQVxqloWiMXxg", # tinglesbyjess
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCBsVm9XFIPhnyerJiSlCv5g", # caitasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCoviXqo4b1MAAkjRWEPJrBg", # busybasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCGEgrbsgWhp2Pd0JTO45A5w", # beezasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCFmL725KKPx2URVPvH3Gp8w", # asmrglow
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCJyZfWrqaGX4nwXGKOEdM6Q", # nanouasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCgUBjMqA_IZQVFdEElvPHDA", # lunabloomasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UC79B6k5KZxYLETtXFfZH1cg", # slightsoundsasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCxL_v3JKcd3_h5OYralxvPg", # darkliteasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCr122mXAEYZPcVi8-kCZP8g", # asmrgirl
    "http://www.youtube.com/feeds/videos.xml?channel_id=UC4bOYyhQgBVzk-neOMHJilQ", # itsbunnii
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCDwR_uew-XkbO0RjUAgrUug", # sarahlavender
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCsOK8zTbZ3BQyEuA11i19Wg", # ilamosasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCnLrvPN5kyK2gCb7pMgCrBw", # baituasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCW6ulUHXpmumuNZS8rWLXbA", # frecklesasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCM5z4re0CofPJJTp1Uocb9Q", # safespaceasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UC0beMA4EPX3TfgPB24zH3DA", # paganmoon
    "http://www.youtube.com/feeds/videos.xml?channel_id=UC2UDe1cKHqOblGo8rHcJ2Vg", # asmrshimmer
    "http://www.youtube.com/feeds/videos.xml?channel_id=UC9T_5DOidv_3EC9TGRDjZEA", # 11orangesasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCdYBTauH8tBrY6aJGdieIDA", # hudiasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCTIxX_suYllEj6n2Q0WVWZQ", # bbyasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCWwGnRCb6luuHOorUR_JxLw", # cassiabreeasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCbRuPWKGtsJo4v1LuizilfQ", # asmrleaf
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCn70vKPtIPkD0W8ISmwlK0A", # kayleescozyasmr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCDfpxS7GiqyoUeXS-zAutoA", # emmyasmrr
    "http://www.youtube.com/feeds/videos.xml?channel_id=UCikebqFWoT3QC9axUbXCPYw", # asmrdarling
]

KEYWORDS = ['affirmation', 'affirmations', 'subconscious', 'positive']

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

def is_relevant(title):
    """Strict relevance check: Keywords MUST be in the title."""
    title_matches = count_keyword_matches(title, KEYWORDS)

    # ✅ Only pass if the title has a keyword
    if title_matches >= 1:
        return True

    # ❌ We no longer check the description for keywords
    return False

def main():
    fg = FeedGenerator()
    fg.title('Filtered Positive Feed')
    fg.link(href='https://maxmrry.github.io/positive-rss-aggregator/docs/', rel='alternate')
    fg.description('Aggregated YouTube feeds with daily reminders.')
    
    # --- ADD MAIN FEED IMAGE ---
    image_url = 'https://raw.githubusercontent.com/maxmrry/positive-rss-aggregator/main/Moon.png'
    fg.logo(image_url)
    fg.image(url=image_url, title='Filtered Positive Feed', link='https://maxmrry.github.io/positive-rss-aggregator/docs/feed.xml')

    all_entries = []

    cutoff = datetime.now(TIMEZONE) - timedelta(days=60)

    # 1. Fetch and Filter YouTube Feeds
    for url in FEEDS:
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            title = entry.get('title', '')
            
            pub_date = date_parser.parse(entry.published)

            # Pass only the title to the gatekeeper
            if is_relevant(title) and pub_date >= cutoff:
                # Extract the highest resolution YouTube thumbnail available
                thumbnails = entry.get('media_thumbnail', [])
                thumb_url = thumbnails[0]['url'] if thumbnails else ''

                all_entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.get('summary', ''),
                    'published': pub_date,
                    'id': entry.id,
                    'thumbnail': thumb_url
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
                'link': f"https://maxmrry.github.io/positive-rss-aggregator/#reminder-{reminder_time.strftime('%Y%m%d')}",
                'description': '', # Empty description for reminders
                'published': reminder_time,
                'id': f"reminder-{reminder_time.strftime('%Y%m%d')}"
            })

    # 3. Sort entries
    all_entries.sort(key=lambda x: x['published'], reverse=True)

    # 4. Build RSS
    for item in all_entries:
        fe = fg.add_entry()
        fe.title(item['title'])

        if item.get('link'):
            fe.link(href=item['link'])

        # Inject the thumbnail image into the description text
        final_desc = ""
        if item.get('thumbnail'):
            fe.enclosure(item['thumbnail'], 0, 'image/jpeg') 
            final_desc += f"<img src='{item['thumbnail']}' alt='thumbnail'/><br><br>"
            
        if item.get('description'):
            final_desc += item['description']
            
        if final_desc:
            fe.description(final_desc)

        fe.pubDate(item['published'])
        fe.id(item['id'])

    # 5. Save
    os.makedirs('docs', exist_ok=True)
    fg.rss_file('docs/feed.xml')

if __name__ == "__main__":
    main()
