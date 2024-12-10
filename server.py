import os
import logging
import datetime
from urllib.parse import urlparse
from pymongo import MongoClient
from urllib.parse import unquote
from pydantic import BaseModel
from typing import List, Optional

# Fast api
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# Util
from StreamingCommunity.Util._jsonConfig import config_manager


# Internal
from StreamingCommunity.Api.Template.Class.SearchType import MediaItem
from StreamingCommunity.Api.Site.streamingcommunity.api import get_version_and_domain, search_titles, get_infoSelectTitle, get_infoSelectSeason
from StreamingCommunity.Api.Site.streamingcommunity.film import download_film
from StreamingCommunity.Api.Site.streamingcommunity.series import download_video
from StreamingCommunity.Api.Site.streamingcommunity.util.ScrapeSerie import ScrapeSerie


# Player
from StreamingCommunity.Api.Player.vixcloud import VideoSource


# Variable
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Site variable
version, domain = get_version_and_domain()
season_name = None
scrape_serie = ScrapeSerie("streamingcommunity")
video_source = VideoSource("streamingcommunity", True)
DOWNLOAD_DIRECTORY = os.getcwd()


# Mongo 
client = MongoClient(config_manager.get("EXTRA", "mongodb"))
db = client[config_manager.get("EXTRA", "database")]
watchlist_collection = db['watchlist']
downloads_collection = db['downloads'] 



def update_domain(url: str):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    domain_part = hostname.split('.')[1]
    new_url = url.replace(domain_part, domain)

    return new_url




# ---------- SITE API ------------
@app.get("/", summary="Health Check")
async def index():
    """
    Health check endpoint to confirm server is operational.
    
    Returns:
        str: Operational status message
    """
    logging.info("Health check endpoint accessed")
    return {"status": "Server is operational"}

@app.get("/api/search", summary="Search Titles")
async def get_list_search(q):
    """
    Search for titles based on query parameter.
    
    Args:
        q (str, optional): Search query parameter
    
    Returns:
        JSON response with search results
    """
    if not q:
        logging.warning("Search request without query parameter")
        raise HTTPException(status_code=400, detail="Missing query parameter")
    
    try:
        result = search_titles(q, domain)
        logging.info(f"Search performed for query: {q}")
        return result
    
    except Exception as e:
        logging.error(f"Error in search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/getInfo", summary="Get Title Information")
async def get_info_title(url):
    """
    Retrieve information for a specific title.
    
    Args:
        url (str, optional): Title URL parameter
    
    Returns:
        JSON response with title information
    """
    if not url:
        logging.warning("GetInfo request without URL parameter")
        raise HTTPException(status_code=400, detail="Missing URL parameter")
    
    try:
        result = get_infoSelectTitle(update_domain(url), domain, version)
        
        # Global state management for TV series
        if result.get('type') == "tv":
            global season_name, scrape_serie, video_source
            season_name = result.get('slug')
            
            # Setup for TV series (adjust based on your actual implementation)
            scrape_serie.setup(
                version=version, 
                media_id=int(result.get('id')), 
                series_name=result.get('slug')
            )
            video_source.setup(result.get('id'))
            
            logging.info(f"TV series info retrieved: {season_name}")
        
        return result
    
    except Exception as e:
        logging.error(f"Error retrieving title info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve title information")

@app.get("/api/getInfoSeason", summary="Get Season Information")
async def get_info_season(url, n):
    """
    Retrieve season information for a specific title.
    
    Args:
        url (str, optional): Title URL parameter
        n (str, optional): Season number
    
    Returns:
        JSON response with season information
    """
    if not url or not n:
        logging.warning("GetInfoSeason request with missing parameters")
        raise HTTPException(status_code=400, detail="Missing URL or season number")
    
    try:
        result = get_infoSelectSeason(update_domain(url), n, domain, version)
        logging.info(f"Season info retrieved for season {n}")
        return result
    
    except Exception as e:
        logging.error(f"Error retrieving season info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve season information")

@app.get("/api/getDomain", summary="Get Current Domain")
async def get_domain():
    """
    Retrieve current domain and version.
    
    Returns:
        JSON response with domain and version
    """
    try:
        global version, domain
        version, domain = get_version_and_domain()
        logging.info(f"Domain retrieved: {domain}, Version: {version}")
        return {"domain": domain, "version": version}
    
    except Exception as e:
        logging.error(f"Error retrieving domain: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve domain information")



# ---------- CALL DOWNLOAD API ------------
@app.get("/api/download/film", summary="Download Film")
async def call_download_film(id, slug):
    """
    Download a film by its ID and slug.
    
    Args:
        id (str, optional): Film ID
        slug (str, optional): Film slug
    
    Returns:
        JSON response with download path or error message
    """
    if not id or not slug:
        logging.warning("Download film request with missing parameters")
        raise HTTPException(status_code=400, detail="Missing film ID or slug")
    
    try:
        item_media = MediaItem(**{'id': id, 'slug': slug})
        path_download = download_film(item_media)

        download_data = {
            'type': 'movie',
            'id': id,
            'slug': slug,
            'path': path_download,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }
        downloads_collection.insert_one(download_data) 
        
        logging.info(f"Film downloaded: {slug}")
        return {"path": path_download}
    
    except Exception as e:
        logging.error(f"Error downloading film: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download film")

@app.get("/api/download/episode", summary="Download TV Episode")
async def call_download_episode(n_s: str, n_ep: str, media_id: Optional[int] = None, series_name: Optional[str] = None):
    """
    Download a specific TV series episode.
    
    Args:
        n_s (str, optional): Season number
        n_ep (str, optional): Episode number
        media_id (int, optional): Media ID of the series
        series_name (str, optional): Series slug
    
    Returns:
        JSON response with download path or error message
    """
    if not n_s or not n_ep:
        logging.warning("Download episode request with missing parameters")
        raise HTTPException(status_code=400, detail="Missing season or episode number")
    
    try:
        season_number = int(n_s)
        episode_number = int(n_ep)
        
        # Se i parametri opzionali sono presenti, impostare la serie con setup
        if media_id is not None and series_name is not None:
            scrape_serie.setup(
                version=version,
                media_id=media_id,
                series_name=series_name
            )
        else:
            scrape_serie.collect_title_season(season_number)
        
        # Scaricare il video
        path_download = download_video(
            scrape_serie.series_name, 
            season_number, 
            episode_number, 
            scrape_serie, 
            video_source
        )

        # Salvare i dati del download
        download_data = {
            'type': 'tv',
            'id': media_id if media_id else scrape_serie.media_id,
            'slug': series_name if series_name else scrape_serie.series_name,
            'n_s': season_number,
            'n_ep': episode_number,
            'path': path_download,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }
        downloads_collection.insert_one(download_data) 
        
        logging.info(f"Episode downloaded: S{season_number}E{episode_number}")
        return {"path": path_download}
    
    except ValueError:
        logging.error("Invalid season or episode number format")
        raise HTTPException(status_code=400, detail="Invalid season or episode number")
    
    except Exception as e:
        logging.error(f"Error downloading episode: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download episode")

@app.get("/api/downloaded/{filename:path}", summary="Serve Downloaded Files")
async def serve_downloaded_file(filename: str):
    """
    Serve downloaded files with proper URL decoding and error handling.
    
    Args:
        filename (str): Encoded filename path
    
    Returns:
        Downloaded file or error message
    """
    try:
        # URL decode the filename
        decoded_filename = unquote(filename)
        logging.debug(f"Requested file: {decoded_filename}")
        
        # Construct full file path
        file_path = os.path.join(DOWNLOAD_DIRECTORY, decoded_filename)
        logging.debug(f"Full file path: {file_path}")
        
        # Verify file exists
        if not os.path.isfile(file_path):
            logging.warning(f"File not found: {decoded_filename}")
            HTTPException(status_code=404, detail="File not found")
        
        # Serve the file
        return FileResponse(
            path=file_path, 
            filename=decoded_filename, 
            media_type='application/octet-stream'
        )
    
    except Exception as e:
        logging.error(f"Error serving file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")



# ---------- WATCHLIST MONGO ------------
class WatchlistItem(BaseModel):
    name: str
    url: str
    season: int

class UpdateWatchlistItem(BaseModel):
    url: str
    season: int

class RemoveWatchlistItem(BaseModel):
    name: str

@app.post("/server/watchlist/add", summary="Add Item to Watchlist")
async def add_to_watchlist(item: WatchlistItem):
    """
    Add a new item to the watchlist.
    
    Args:
        item (WatchlistItem): Details of the item to add
    
    Returns:
        JSON response with success or error message
    """
    try:
        # Check if item already exists
        existing_item = watchlist_collection.find_one({
            'name': item.name, 
            'title_url': item.url, 
            'season': item.season
        })
        
        if existing_item:
            raise HTTPException(status_code=400, detail="Il titolo è già nella watchlist")
        
        # Insert new item
        watchlist_collection.insert_one({
            'name': item.name,
            'title_url': item.url,
            'season': item.season,
            'added_on': datetime.datetime.utcnow()
        })
        
        return {"message": "Titolo aggiunto alla watchlist"}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error adding to watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@app.post("/server/watchlist/update", summary="Update Watchlist Item")
async def update_title_watchlist(item: UpdateWatchlistItem):
    """
    Update the season for an existing watchlist item.
    
    Args:
        item (UpdateWatchlistItem): Details of the item to update
    
    Returns:
        JSON response with update status
    """
    try:
        result = watchlist_collection.update_one(
            {'title_url': item.url},
            {'$set': {'season': item.season}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Titolo non trovato nella watchlist")
        
        if result.modified_count == 0:
            return {"message": "La stagione non è cambiata"}
        
        return {"message": "Stagione aggiornata con successo"}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@app.post("/server/watchlist/remove", summary="Remove Item from Watchlist")
async def remove_from_watchlist(item: RemoveWatchlistItem):
    """
    Remove an item from the watchlist.
    
    Args:
        item (RemoveWatchlistItem): Details of the item to remove
    
    Returns:
        JSON response with removal status
    """
    try:
        result = watchlist_collection.delete_one({'name': item.name})
        
        if result.deleted_count == 1:
            return {"message": "Titolo rimosso dalla watchlist"}
        
        raise HTTPException(status_code=404, detail="Titolo non trovato nella watchlist")
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error removing from watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@app.get("/server/watchlist/get", summary="Get Watchlist Items")
async def get_watchlist():
    """
    Retrieve all items in the watchlist.
    
    Returns:
        List of watchlist items or empty list message
    """
    try:
        watchlist_items = list(watchlist_collection.find({}, {'_id': 0}))
        
        if not watchlist_items:
            return {"message": "La watchlist è vuota"}
        
        return watchlist_items
    
    except Exception as e:
        logging.error(f"Error retrieving watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@app.get("/server/watchlist/checkNewSeason", summary="Check for New Seasons")
async def get_new_seasons():
    """
    Check for new seasons of watchlist items.
    
    Returns:
        List of items with new seasons or message
    """
    try:
        watchlist_items = list(watchlist_collection.find({}, {'_id': 0}))
        
        if not watchlist_items:
            return {"message": "La watchlist è vuota"}
        
        title_new_seasons = []
        
        for item in watchlist_items:
            title_url = item.get('title_url')
            if not title_url:
                continue
            
            try:
                new_url = update_domain(title_url)
                
                # Fetch title info
                result = get_infoSelectTitle(new_url, domain, version)
                
                if not result or 'season_count' not in result:
                    continue
                
                number_season = result.get("season_count")
                
                # Check for new seasons
                if number_season > item.get("season"):
                    title_new_seasons.append({
                        'title_url': item.get('title_url'),
                        'name': item.get('name'),
                        'season': int(number_season),
                        'nNewSeason': int(number_season) - int(item.get("season"))
                    })
            
            except Exception as e:
                logging.error(f"Error checking seasons for {item.get('title_url')}: {str(e)}")
        
        if title_new_seasons:
            return title_new_seasons
        
        return {"message": "Nessuna nuova stagione disponibile"}
    
    except Exception as e:
        logging.error(f"Error in check watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore interno del server")



# ---------- REMOVE DOWNLOAD FILE WITH MONGO ------------
def ensure_collections_exist(db):
    """
    Ensures that the required collections exist in the database.
    If they do not exist, they are created.

    Args:
        db: The MongoDB database object.
    """
    required_collections = ['watchlist', 'downloads']
    existing_collections = db.list_collection_names()

    for collection_name in required_collections:
        if collection_name not in existing_collections:
            # Creazione della collezione
            db.create_collection(collection_name)
            logging.info(f"Created missing collection: {collection_name}")
        else:
            logging.info(f"Collection already exists: {collection_name}")

class Episode(BaseModel):
    id: int
    season: int
    episode: int

class Movie(BaseModel):
    id: int

# Fetch all downloads
@app.get("/server/path/getAll", response_model=List[dict], summary="Get all download from disk")
async def fetch_all_downloads():
    """
    Endpoint to fetch all downloads.
    """
    try:
        downloads = list(downloads_collection.find({}, {'_id': 0}))
        return downloads
    
    except Exception as e:
        logging.error(f"Error fetching all downloads: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching all downloads")

# Remove a specific episode and its file
@app.delete("/server/delete/episode", summary="Remove episode from disk")
async def remove_episode(series_id: int, season_number: int, episode_number: int):
    """
    Endpoint to delete a specific episode and its file.
    """
    try:
        # Find the episode in the database
        episode = downloads_collection.find_one({
            'type': 'tv',
            'id': series_id,
            'n_s': season_number,
            'n_ep': episode_number
        }, {'_id': 0, 'path': 1})

        logging.info("FIND => ", episode)

        if not episode or 'path' not in episode:
            raise HTTPException(status_code=404, detail="Episode not found")

        file_path = episode['path']
        logging.info("PATH => ", file_path)

        # Delete the file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted episode file: {file_path}")
            else:
                logging.warning(f"Episode file not found: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting episode file: {str(e)}")

        # Remove the episode from the database
        result = downloads_collection.delete_one({
            'type': 'tv',
            'id': series_id,
            'n_s': season_number,
            'n_ep': episode_number
        })

        if result.deleted_count > 0:
            return JSONResponse(status_code=200, content={'success': True})
        else:
            raise HTTPException(status_code=500, detail="Failed to delete episode from database")

    except Exception as e:
        logging.error(f"Error deleting episode: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete episode")

# Remove a specific movie, its file, and its parent folder if empty
@app.delete("/server/delete/movie", summary="Remove a movie from disk")
async def remove_movie(movie_id: int):
    """
    Endpoint to delete a specific movie, its file, and its parent folder if empty.
    """
    try:
        # Find the movie in the database
        movie = downloads_collection.find_one({'type': 'movie', 'id': str(movie_id)}, {'_id': 0, 'path': 1})

        if not movie or 'path' not in movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        file_path = movie['path']
        parent_folder = os.path.dirname(file_path)

        # Delete the movie file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted movie file: {file_path}")
            else:
                logging.warning(f"Movie file not found: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting movie file: {str(e)}")

        # Delete the parent folder if empty
        try:
            if os.path.exists(parent_folder) and not os.listdir(parent_folder):
                os.rmdir(parent_folder)
                logging.info(f"Deleted empty parent folder: {parent_folder}")
        except Exception as e:
            logging.error(f"Error deleting parent folder: {str(e)}")

        # Remove the movie from the database
        result = downloads_collection.delete_one({'type': 'movie', 'id': str(movie_id)})

        if result.deleted_count > 0:
            return JSONResponse(status_code=200, content={'success': True})
        else:
            raise HTTPException(status_code=500, detail="Failed to delete movie from database")

    except Exception as e:
        logging.error(f"Error deleting movie: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete movie")

# Fetch the path of a specific movie
@app.get("/server/path/movie", response_model=dict, summary="Get movie download path on disk")
async def fetch_movie_path(movie_id: int):
    """
    Endpoint to fetch the path of a specific movie.
    """
    try:
        movie = downloads_collection.find_one({'type': 'movie', 'id': movie_id}, {'_id': 0, 'path': 1})

        if movie and 'path' in movie:
            return {"path": movie['path']}
        else:
            raise HTTPException(status_code=404, detail="Movie not found")

    except Exception as e:
        logging.error(f"Error fetching movie path: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch movie path")

# Fetch the path of a specific episode
@app.get("/server/path/episode", response_model=dict, summary="Get episode download path on disk")
async def fetch_episode_path(series_id: int, season_number: int, episode_number: int):
    """
    Endpoint to fetch the path of a specific episode.
    """
    try:
        episode = downloads_collection.find_one({
            'type': 'tv',
            'id': series_id,
            'n_s': season_number,
            'n_ep': episode_number
        }, {'_id': 0, 'path': 1})

        if episode and 'path' in episode:
            return {"path": episode['path']}
        else:
            raise HTTPException(status_code=404, detail="Episode not found")

    except Exception as e:
        logging.error(f"Error fetching episode path: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch episode path")
        



# ---------- MAIN ------------
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=1234, loop="asyncio")
