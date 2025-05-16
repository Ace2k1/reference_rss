import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime

def add_entry_if_not_exists(feed_file, character_name, artist, image_url, entry_date):
    # Parse existing RSS feed
    existing_feed = feedparser.parse(feed_file)

    # Collect existing image URLs from descriptions to detect duplicates
    existing_image_urls = set()
    for entry in existing_feed.entries:
        # Naive extraction of src from img tag in description
        if 'description' in entry:
            desc = entry.description
            start = desc.find("src='")
            if start == -1:
                start = desc.find('src="')
                if start == -1:
                    continue
                quote = '"'
            else:
                quote = "'"
            if start != -1:
                start += 5  # move past src=' or src="
                end = desc.find(quote, start)
                if end != -1:
                    url = desc[start:end]
                    existing_image_urls.add(url)

    # Skip if image_url already exists
    if image_url in existing_image_urls:
        print(f"Entry with image URL '{image_url}' already exists. Skipping.")
        return

    # Create feed generator and copy existing metadata
    fg = FeedGenerator()
    fg.title(existing_feed.feed.get('title', "Character References RSS"))
    fg.link(href=existing_feed.feed.get('link', "https://github.com/Ace2k1/reference-rss"), rel="alternate")
    fg.description(existing_feed.feed.get('description', "A feed of character references and artwork."))
    fg.language(existing_feed.feed.get('language', "en"))

    # Re-add old entries
    for entry in existing_feed.entries:
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.description(entry.description)
        # Convert published to datetime if possible, else skip
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            fe.pubDate(datetime(*entry.published_parsed[:6]))

    # Add the new entry
    fe = fg.add_entry()
    fe.title(f"{character_name} by {artist}")
    fe.link(href=image_url)
    fe.description(f"<img src='{image_url}' alt='{character_name}' /><br>{character_name} by {artist}")
    fe.pubDate(entry_date)

    # Write updated feed to file
    fg.rss_file(feed_file)
    print(f"Added new entry: {character_name} by {artist}")

# Example usage
add_entry_if_not_exists(
    feed_file="rss.xml",
    character_name="Asuka Langley",
    artist="John Doe",
    image_url="https://raw.githubusercontent.com/Ace2k1/reference-rss/main/images/asuka.jpg",
    entry_date=datetime(2025, 5, 16)
