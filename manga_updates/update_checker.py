import feedparser
import asyncio
import json 
import os

async def get_json_file(path:str):
    with open(path, 'r') as file:
        game_info = json.load(file)
    return game_info

async def init_update_feed():
    tracking_list = await get_json_file("manga_updates/tracking_chapter_list.json")
    tracking_info_list = []
    # * Tracking list should have at least: 
    #     * name
    #     * link
    #     * latest chapter

    for tracking in tracking_list:
        url = tracking['url']
        feed = feedparser.parse(url)

        name = feed['feed']['title'].replace(' - Releases on MangaUpdates', '')
        latest_chapter = feed['entries'][0]['title']
        entries = feed['entries']

        tracking_info_list.append(

            {
                "name": name,
                "latest_chapter": latest_chapter,
                "entries": entries
            }

        )

        if not os.path.exists('manga_updates/tracking_manga_info.json'):
            with open('manga_updates/tracking_manga_info.json', 'w') as json_file:
                json.dump(tracking_info_list, json_file)
        else:
            with open('manga_updates/tracking_manga_info.json', 'w') as json_file:
                json.dump(tracking_info_list, json_file, indent=4)

async def add_manga_track(name, url):
    tracking_list = await get_json_file("manga_updates/tracking_chapter_list.json")
    tracking_list.append(
        {
            "name": name,
            "url": url
        }
    )

    with open('manga_updates/tracking_chapter_list.json', 'w') as json_file:
        json.dump(tracking_list, json_file, indent=4)

if __name__ == "__main__":
    asyncio.run(add_manga_track("Rebuild World", "https://api.mangaupdates.com/v1/series/73393743472/rss"))
    asyncio.run(init_update_feed())
