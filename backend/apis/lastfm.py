import requests
import config
import json

def get_lastfm_tags(title, artist):
    """Fetches top tags from Last.fm API."""
    if not hasattr(config, "LASTFM_API_KEY") or not config.LASTFM_API_KEY or config.LASTFM_API_KEY == "your_lastfm_free_api_key":
        return "[]"
        
    if title == "Unknown" or artist == "Unknown":
        return "[]"
        
    try:
        url = f"http://ws.audioscrobbler.com/2.0/?method=track.gettoptags&artist={artist}&track={title}&api_key={config.LASTFM_API_KEY}&format=json"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if "toptags" in data and "tag" in data["toptags"]:
                tags = [tag["name"] for tag in data["toptags"]["tag"]]
                return json.dumps(tags[:10]) # Get top 10 tags
    except Exception as e:
        print(f"LastFM API error: {e}")
        
    return "[]"
