# 13.12.24

import os
import logging
#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
import datetime
from urllib.parse import urlparse, unquote
from typing import Optional


# External
import uvicorn
from rich.console import Console
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


# Util
from StreamingCommunity.Util.os import os_summary
os_summary.get_system_summary()
from StreamingCommunity.Util.logger import Logger
log = Logger()
from StreamingCommunity.Util._jsonConfig import config_manager
from server_type import WatchlistItem, UpdateWatchlistItem
from server_util import updateUrl


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
    allow_headers=["*"]
)


# Site variable
version, domain = get_version_and_domain()
season_name = None
scrape_serie = ScrapeSerie("streamingcommunity")
video_source = VideoSource("streamingcommunity", True)

DOWNLOAD_DIRECTORY = os.getcwd()
console = Console()


# Mongo variable
client = MongoClient(config_manager.get("EXTRA", "mongodb"))
db = client[config_manager.get("EXTRA", "database")]
watchlist_collection = db['watchlist']
downloads_collection = db['downloads'] 



# ---------- SITE API ------------
@app.get("/", summary="Health Check")
async def index():
    logging.info("Health check endpoint accessed")
    return "Server is operational"

@app.get("/api/search")
async def get_list_search(q: Optional[str] = Query(None)):
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

@app.get("/api/getInfo")
async def get_info_title(url: Optional[str] = Query(None)):
    if not url or "http" not in url:
        logging.warning("GetInfo request without URL parameter")
        raise HTTPException(status_code=400, detail="Missing URL parameter")
    
    
    try:
        result = get_infoSelectTitle(url, domain, version)

        if result.get('type') == "tv":
            global season_name, scrape_serie, video_source

            season_name = result.get('slug')

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

@app.get("/api/getInfoSeason")
async def get_info_season(url: Optional[str] = Query(None), n: Optional[str] = Query(None)):
    if not url or not n:
        logging.warning("GetInfoSeason request with missing parameters")
        raise HTTPException(status_code=400, detail="Missing URL or season number")
    
    try:
        result = get_infoSelectSeason(url, n, domain, version)
        logging.info(f"Season info retrieved for season {n}")
        return result
    
    except Exception as e:
        logging.error(f"Error retrieving season info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve season information")

@app.get("/api/getdomain")
async def get_domain():
    try:
        global version, domain
        version, domain = get_version_and_domain()
        logging.info(f"Domain retrieved: {domain}, Version: {version}")

        return {"domain": domain, "version": version}
    
    except Exception as e:
        logging.error(f"Error retrieving domain: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve domain information")


# ---------- DOWNLOAD API ------------
@app.get("/api/download/film")
async def call_download_film(id: Optional[str] = Query(None), slug: Optional[str] = Query(None)):
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

@app.get("/api/download/episode")
async def call_download_episode(n_s: Optional[int] = Query(None), n_ep: Optional[int] = Query(None), titleID: Optional[int] = Query(None), slug: Optional[str] = Query(None)):
    global scrape_serie

    if not n_s or not n_ep:
        logging.warning("Download episode request with missing parameters")
        raise HTTPException(status_code=400, detail="Missing season or episode number")
    
    try:

        scrape_serie.setup(
            version=version, 
            media_id=int(titleID), 
            series_name=slug
        )
        video_source.setup(int(titleID))

        scrape_serie.collect_info_title()
        scrape_serie.collect_info_season(n_s)

        path_download = download_video(
            season_name, 
            n_s, 
            n_ep, 
            scrape_serie, 
            video_source
        )

        download_data = {
            'type': 'tv',
            'id': scrape_serie.media_id,
            'slug': scrape_serie.series_name,
            'n_s': n_s,
            'n_ep': n_ep,
            'path': path_download,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }

        downloads_collection.insert_one(download_data) 

        logging.info(f"Episode downloaded: S{n_s}E{n_ep}")
        return {"path": path_download}
    
    except Exception as e:
        logging.error(f"Error downloading episode: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download episode")

@app.get("/api/downloaded/{filename:path}")
async def serve_downloaded_file(filename: str):
    try:
        # Decodifica il nome file
        decoded_filename = unquote(filename)
        logging.info(f"Decoded filename: {decoded_filename}")

        # Normalizza il percorso
        file_path = os.path.normpath(os.path.join(DOWNLOAD_DIRECTORY, decoded_filename))

        # Verifica che il file sia all'interno della directory
        if not file_path.startswith(os.path.abspath(DOWNLOAD_DIRECTORY)):
            logging.error(f"Path traversal attempt detected: {file_path}")
            raise HTTPException(status_code=400, detail="Invalid file path")

        # Verifica che il file esista
        if not os.path.isfile(file_path):
            logging.error(f"File not found: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")

        # Restituisci il file
        return FileResponse(file_path)
    except Exception as e:
        logging.error(f"Error serving file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------- WATCHLIST UTIL MONGO ------------
@app.post("/server/watchlist/add")
async def add_to_watchlist(item: WatchlistItem):
    existing_item = watchlist_collection.find_one({
        'name': item.name, 
        'url': item.url, 
        'season': item.season
    })

    if existing_item:
        logging.warning(f"Item already in watchlist: {item.name}")
        raise HTTPException(status_code=400, detail="Il titolo è già nella watchlist")

    watchlist_collection.insert_one({
        'name': item.name,
        'title_url': item.url,
        'season': item.season,
        'added_on': datetime.datetime.utcnow()
    })

    logging.info(f"Added to watchlist: {item.name}")
    return {"message": "Titolo aggiunto alla watchlist"}

@app.post("/server/watchlist/update")
async def update_title_watchlist(update: UpdateWatchlistItem):
    result = watchlist_collection.update_one(
        {'title_url': update.url},
        {'$set': {'season': update.season}}
    )

    if result.matched_count == 0:
        logging.warning(f"Item not found for update: {update.url}")
        raise HTTPException(status_code=404, detail="Titolo non trovato nella watchlist")
    
    if result.modified_count == 0:
        logging.info(f"Season unchanged for: {update.url}")
        return {"message": "La stagione non è cambiata"}

    logging.info(f"Updated season for: {update.url}")
    return {"message": "Stagione aggiornata con successo"}

@app.post("/server/watchlist/remove")
async def remove_from_watchlist(item: WatchlistItem):
    # You can handle just the 'name' field here
    result = watchlist_collection.delete_one({'name': item.name})

    if result.deleted_count == 0:
        logging.warning(f"Item not found for removal: {item.name}")
        raise HTTPException(status_code=404, detail="Titolo non trovato nella watchlist")
    
    logging.info(f"Successfully removed from watchlist: {item.name}")
    return {"message": "Titolo rimosso dalla watchlist"}

@app.get("/server/watchlist/get")
async def get_watchlist():
    watchlist_items = list(watchlist_collection.find({}, {'_id': 0}))

    if not watchlist_items:
        logging.info("Watchlist is empty")
        return {"message": "La watchlist è vuota"}

    logging.info("Watchlist retrieved")
    return watchlist_items
    
@app.get("/server/watchlist/check")
async def get_new_season():
    title_new_seasons = []
    watchlist_items = list(watchlist_collection.find({}, {'_id': 0}))
    logging.error("GET: ", watchlist_items)

    if not watchlist_items:
        logging.info("Watchlist is empty")
        return {"message": "La watchlist è vuota"}

    for item in watchlist_items:
        try:
            new_url = updateUrl(item['title_url'], domain)

            result = get_infoSelectTitle(new_url, domain, version)
            if not result or 'season_count' not in result:
                continue

            number_season = result.get("season_count")
            if number_season > item.get("season"):
                title_new_seasons.append({
                    'title_url': item['title_url'],
                    'name': item['name'],
                    'season': number_season,
                    'nNewSeason': number_season - item['season']
                })

        except Exception as e:
            logging.error(f"Error checking new season for {item['title_url']}: {e}")

    if title_new_seasons:
        logging.info(f"New seasons found: {len(title_new_seasons)}")
        return title_new_seasons

    return {"message": "Nessuna nuova stagione disponibile"}


# ---------- DOWNLOAD UTIL MONGO ------------
def ensure_collections_exist(db):
    required_collections = ['watchlist', 'downloads']
    existing_collections = db.list_collection_names()

    for collection_name in required_collections:
        if collection_name not in existing_collections:
            # Creazione della collezione
            db.create_collection(collection_name)
            logging.info(f"Created missing collection: {collection_name}")
        else:
            logging.info(f"Collection already exists: {collection_name}")


@app.get("/server/path/get")
async def fetch_all_downloads():
    try:
        downloads = list(downloads_collection.find({}, {'_id': 0}))
        logging.info("Downloads retrieved")
        return downloads
    
    except Exception as e:
        logging.error(f"Error fetching downloads: {e}")
        raise HTTPException(status_code=500, detail="Errore nel recupero dei download")

@app.get("/server/path/movie")
async def fetch_movie_path(id: Optional[int] = Query(None)):
    if not id:
        logging.warning("Movie path request without ID parameter")
        raise HTTPException(status_code=400, detail="Missing movie ID")

    try:
        movie = downloads_collection.find_one(
            {'type': 'movie', 'id': id}, 
            {'_id': 0, 'path': 1}
        )

        if movie and 'path' in movie:
            logging.info(f"Movie path retrieved: {movie['path']}")
            return {"path": movie['path']}
        
        else:
            logging.warning(f"Movie not found: ID {id}")
            raise HTTPException(status_code=404, detail="Movie not found")
        
    except Exception as e:
        logging.error(f"Error fetching movie path: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch movie path")

@app.get("/server/path/episode")
async def fetch_episode_path(id: Optional[int] = Query(None), season: Optional[int] = Query(None), episode: Optional[int] = Query(None)):
    if not id or not season or not episode:
        logging.warning("Episode path request with missing parameters")
        raise HTTPException(status_code=400, detail="Missing parameters (id, season, episode)")

    try:
        episode_data = downloads_collection.find_one(
            {'type': 'tv', 'id': id, 'n_s': season, 'n_ep': episode},
            {'_id': 0, 'path': 1}
        )

        if episode_data and 'path' in episode_data:
            logging.info(f"Episode path retrieved: {episode_data['path']}")
            return {"path": episode_data['path']}
        
        else:
            logging.warning(f"Episode not found: ID {id}, Season {season}, Episode {episode}")
            raise HTTPException(status_code=404, detail="Episode not found")
        
    except Exception as e:
        logging.error(f"Error fetching episode path: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch episode path")

@app.delete("/server/delete/episode")
async def remove_episode(series_id: int = Query(...), season_number: int = Query(...), episode_number: int = Query(...)):
    episode = downloads_collection.find_one({
        'type': 'tv',
        'id': series_id,
        'n_s': season_number,
        'n_ep': episode_number
    }, {'_id': 0, 'path': 1})

    if not episode:
        logging.warning(f"Episode not found: S{season_number}E{episode_number}")
        raise HTTPException(status_code=404, detail="Episodio non trovato")

    file_path = episode.get('path')
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Episode file deleted: {file_path}")

    downloads_collection.delete_one({
        'type': 'tv',
        'id': series_id,
        'n_s': season_number,
        'n_ep': episode_number
    })

    return {"success": True}

@app.delete("/server/delete/movie")
async def remove_movie(movie_id: int = Query(...)):
    movie = downloads_collection.find_one({'type': 'movie', 'id': movie_id}, {'_id': 0, 'path': 1})

    if not movie:
        logging.warning(f"Movie not found: ID {movie_id}")
        raise HTTPException(status_code=404, detail="Film non trovato")

    file_path = movie.get('path')
    parent_folder = os.path.dirname(file_path)

    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Movie file deleted: {file_path}")

    if os.path.exists(parent_folder) and not os.listdir(parent_folder):
        os.rmdir(parent_folder)
        logging.info(f"Parent folder deleted: {parent_folder}")

    downloads_collection.delete_one({'type': 'movie', 'id': movie_id})
    return {"success": True}


if __name__ == "__main__":

    ensure_collections_exist(db)
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=1234,
        reload=False
    )