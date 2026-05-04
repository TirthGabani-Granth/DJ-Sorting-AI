import requests
import config

def get_jiosaavn_info(title, artist):
    """Fetches song info from unofficial JioSaavn API."""
    if not hasattr(config, "JIOSAAVN_BASE_URL") or not config.JIOSAAVN_BASE_URL:
        return {}
        
    try:
        query = f"{title} {artist}".strip()
        if not query:
            return {}
            
        url = f"{config.JIOSAAVN_BASE_URL}/search/songs?query={query}&limit=1"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data and data.get("data", {}).get("results"):
                song_data = data["data"]["results"][0]
                return {
                    "language": song_data.get("language"),
                    "year": song_data.get("year")
                }
    except Exception as e:
        print(f"JioSaavn API error: {e}")
        
    return {}
