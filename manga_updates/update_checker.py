import feedparser
import time

# Define the RSS feed URL
FEED_URL = "https://api.mangaupdates.com/v1/series/24893347544/rss"

# Store seen entries to avoid duplicate notifications
seen_entries = set()

async def get_json_file(path:str):
    with open(path, 'r') as file:
        game_info = json.load(file)
    return game_info

async def update_feed():
    tracking_list = await get_json_file("tracking_list.json")
    # * Tracking list should have at least: 
    #     * name
    #     * link
    #     * latest chapter

    feed = feedparser.parse(tracking_list['url'])


async def check_feed():
    # Parse the RSS feed
    feed = feedparser.parse(FEED_URL)
    
    # Loop through entries
    for entry in feed.entries:
        if entry.id not in seen_entries:
            # Notify about the new entry (e.g., print or send an email)
            print(f"New entry: {entry.title}")
            print(f"Link: {entry.link}")
            print(f"Published: {entry.published}\n")

            # Mark entry as seen
            seen_entries.add(entry.id)

if __name__ == "__main__":
    check_feed()
    time.sleep(3600)  # Check every hour


{'bozo': False, 'entries': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, ...], 'feed': {'title': 'Mato Seihei no Slave - Releases on MangaUpdates', 'title_detail': {...}, 'links': [...], 'link': 'https://www.mangaupdates.com/series/bfoutw8/mato-seihei-no-slave', 'subtitle': 'This feed shows the latest releases for the series Mato Seihei no Slave as shown on MangaUpdates.com', 'subtitle_detail': {...}}, 'headers': {'date': 'Sun, 03 Nov 2024 22:17:05 GMT', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'connection': 'close', 'x-frame-options': 'SAMEORIGIN', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-encoding': 'gzip'}, 'href': 'https://api.mangaupdates.com/v1/series/24893347544/rss', 'status': 200, 'encoding': 'utf-8', 'version': 'rss20', 'namespaces': {'content': 'http://purl.org/rss/1.0/modules/content/'}}