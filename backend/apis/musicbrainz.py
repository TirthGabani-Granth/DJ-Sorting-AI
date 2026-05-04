import acoustid
import requests
import config

def get_musicbrainz_info(file_path):
    """Fetches verified metadata using AcoustID and MusicBrainz."""
    if not hasattr(config, "ACOUSTID_API_KEY") or not config.ACOUSTID_API_KEY or config.ACOUSTID_API_KEY == "your_acoustid_free_api_key":
        return {}
        
    try:
        # Generate fingerprint
        duration, fp = acoustid.fingerprint_file(file_path)
        
        # Look up acoustid
        response = acoustid.lookup(config.ACOUSTID_API_KEY, fp, duration, meta=['recordings', 'releases'])
        
        for result in response['results']:
            if 'recordings' in result:
                for recording in result['recordings']:
                    return {
                        "acoustid_id": result['id'],
                        "musicbrainz_id": recording.get('id', '')
                    }
    except Exception as e:
        print(f"AcoustID/MusicBrainz error: {e}")
        
    return {}
