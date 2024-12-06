import os
import logging
import shutil
import datetime
from urllib.parse import urlparse
from pymongo import MongoClient
from urllib.parse import unquote
from flask_cors import CORS 
from flask import Flask, jsonify, request
from flask import send_from_directory

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
app = Flask(__name__)
CORS(app)

version, domain = get_version_and_domain()
season_name = None
scrape_serie = ScrapeSerie("streamingcommunity")
video_source = VideoSource("streamingcommunity", True)
DOWNLOAD_DIRECTORY = os.getcwd()


client = MongoClient(config_manager.get("EXTRA", "mongodb"))
db = client[config_manager.get("EXTRA", "database")]
watchlist_collection = db['watchlist']
downloads_collection = db['downloads'] 



# ---------- SITE API ------------
@app.route('/')
def index():
    """
    Health check endpoint to confirm server is operational.
    
    Returns:
        str: Operational status message
    """
    logging.info("Health check endpoint accessed")
    return 'Server is operational'

@app.route('/api/search', methods=['GET'])
def get_list_search():
    """
    Search for titles based on query parameter.
    
    Returns:
        JSON response with search results or error message
    """
    try:
        query = request.args.get('q')
        
        if not query:
            logging.warning("Search request without query parameter")
            return jsonify({'error': 'Missing query parameter'}), 400
        
        result = search_titles(query, domain)
        logging.info(f"Search performed for query: {query}")
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"Error in search: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/getInfo', methods=['GET'])
def get_info_title():
    """
    Retrieve information for a specific title.
    
    Returns:
        JSON response with title information or error message
    """
    try:
        title_url = request.args.get('url')
        
        if not title_url:
            logging.warning("GetInfo request without URL parameter")
            return jsonify({'error': 'Missing URL parameter'}), 400
        
        result = get_infoSelectTitle(title_url, domain, version)
        
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
        
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"Error retrieving title info: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve title information'}), 500

@app.route('/api/getInfoSeason', methods=['GET'])
def get_info_season():
    """
    Retrieve season information for a specific title.
    
    Returns:
        JSON response with season information or error message
    """
    try:
        title_url = request.args.get('url')
        number_season = request.args.get('n')
        
        if not title_url or not number_season:
            logging.warning("GetInfoSeason request with missing parameters")
            return jsonify({'error': 'Missing URL or season number'}), 400
        
        result = get_infoSelectSeason(title_url, number_season, domain, version)
        logging.info(f"Season info retrieved for season {number_season}")
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"Error retrieving season info: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve season information'}), 500

@app.route('/api/getdomain', methods=['GET'])
def get_domain():
    """
    Retrieve current domain and version.
    
    Returns:
        JSON response with domain and version
    """
    try:
        global version, domain
        version, domain = get_version_and_domain()
        logging.info(f"Domain retrieved: {domain}, Version: {version}")
        return jsonify({'domain': domain, 'version': version}), 200
    
    except Exception as e:
        logging.error(f"Error retrieving domain: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve domain information'}), 500



# ---------- DOWNLOAD API ------------
@app.route('/downloadFilm', methods=['GET'])
def call_download_film():
    """
    Download a film by its ID and slug.
    
    Returns:
        JSON response with download path or error message
    """
    try:
        film_id = request.args.get('id')
        slug = request.args.get('slug')
        
        if not film_id or not slug:
            logging.warning("Download film request with missing parameters")
            return jsonify({'error': 'Missing film ID or slug'}), 400
        
        item_media = MediaItem(**{'id': film_id, 'slug': slug})
        path_download = download_film(item_media)

        download_data = {
            'type': 'movie',
            'id': film_id,
            'slug': slug,
            'path': path_download,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }
        downloads_collection.insert_one(download_data) 
        
        logging.info(f"Film downloaded: {slug}")
        return jsonify({'path': path_download}), 200
    
    except Exception as e:
        logging.error(f"Error downloading film: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to download film'}), 500

@app.route('/downloadEpisode', methods=['GET'])
def call_download_episode():
    """
    Download a specific TV series episode.
    
    Returns:
        JSON response with download path or error message
    """
    try:
        season_number = request.args.get('n_s')
        episode_number = request.args.get('n_ep')
        
        if not season_number or not episode_number:
            logging.warning("Download episode request with missing parameters")
            return jsonify({'error': 'Missing season or episode number'}), 400
        
        season_number = int(season_number)
        episode_number = int(episode_number)
        
        scrape_serie.collect_title_season(season_number)
        path_download = download_video(
            season_name, 
            season_number, 
            episode_number, 
            scrape_serie, 
            video_source
        )

        download_data = {
            'type': 'tv',
            'id': scrape_serie.media_id,
            'slug': scrape_serie.series_name,
            'n_s': season_number,
            'n_ep': episode_number,
            'path': path_download,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }
        downloads_collection.insert_one(download_data) 
        
        logging.info(f"Episode downloaded: S{season_number}E{episode_number}")
        return jsonify({'path': path_download}), 200
    
    except ValueError:
        logging.error("Invalid season or episode number format")
        return jsonify({'error': 'Invalid season or episode number'}), 400
    
    except Exception as e:
        logging.error(f"Error downloading episode: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to download episode'}), 500

@app.route('/downloaded/<path:filename>', methods=['GET'])
def serve_downloaded_file(filename):
    """
    Serve downloaded files with proper URL decoding and error handling.
    
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
            return jsonify({'error': 'File not found'}), 404
        
        # Serve the file
        return send_from_directory(DOWNLOAD_DIRECTORY, decoded_filename, as_attachment=False)
    
    except Exception as e:
        logging.error(f"Error serving file: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500



# ---------- WATCHLIST MONGO ------------
@app.route('/api/addWatchlist', methods=['POST'])
def add_to_watchlist():
    title_name = request.json.get('name')
    title_url = request.json.get('url')
    season = request.json.get('season')

    if title_url and season:

        existing_item = watchlist_collection.find_one({'name': title_name, 'url': title_url, 'season': season})
        if existing_item:
            return jsonify({'message': 'Il titolo è già nella watchlist'}), 400

        watchlist_collection.insert_one({
            'name': title_name,
            'title_url': title_url,
            'season': season,
            'added_on': datetime.datetime.utcnow()
        })
        return jsonify({'message': 'Titolo aggiunto alla watchlist'}), 200
    else:
        return jsonify({'message': 'Missing title_url or season'}), 400

@app.route('/api/updateTitleWatchlist', methods=['POST'])
def update_title_watchlist():
    print(request.json)

    title_url = request.json.get('url')
    new_season = request.json.get('season')

    if title_url is not None and new_season is not None:
        result = watchlist_collection.update_one(
            {'title_url': title_url},
            {'$set': {'season': new_season}}
        )

        if result.matched_count == 0:
            return jsonify({'message': 'Titolo non trovato nella watchlist'}), 404

        if result.modified_count == 0:
            return jsonify({'message': 'La stagione non è cambiata'}), 200

        return jsonify({'message': 'Stagione aggiornata con successo'}), 200
    
    else:
        return jsonify({'message': 'Missing title_url or season'}), 400
    
@app.route('/api/removeWatchlist', methods=['POST'])
def remove_from_watchlist():
    title_name = request.json.get('name')

    if title_name:
        result = watchlist_collection.delete_one({'name': title_name})

        if result.deleted_count == 1:
            return jsonify({'message': 'Titolo rimosso dalla watchlist'}), 200
        else:
            return jsonify({'message': 'Titolo non trovato nella watchlist'}), 404
    else:
        return jsonify({'message': 'Missing title_url or season'}), 400
    
@app.route('/api/getWatchlist', methods=['GET'])
def get_watchlist():
    watchlist_items = list(watchlist_collection.find({}, {'_id': 0}))

    if watchlist_items:
        return jsonify(watchlist_items), 200
    else:
        return jsonify({'message': 'La watchlist è vuota'}), 200
    
@app.route('/api/checkWatchlist', methods=['GET'])
def get_newSeason():
    title_newSeasons = []
    watchlist_items = list(watchlist_collection.find({}, {'_id': 0}))

    if not watchlist_items:
        return jsonify({'message': 'La watchlist è vuota'}), 200

    for item in watchlist_items:
        title_url = item.get('title_url')
        if not title_url:
            continue

        try:
            parsed_url = urlparse(title_url)
            hostname = parsed_url.hostname
            domain_part = hostname.split('.')[1]
            new_url = title_url.replace(domain_part, domain)

            result = get_infoSelectTitle(new_url, domain, version)

            if not result or 'season_count' not in result:
                continue 

            number_season = result.get("season_count")

            if number_season > item.get("season"):
                title_newSeasons.append({
                    'title_url': item.get('title_url'),
                    'name': item.get('name'),
                    'season': int(number_season),
                    'nNewSeason': int(number_season) - int(item.get("season"))
                })

        except Exception as e:
            print(f"Errore nel recuperare informazioni per {item.get('title_url')}: {e}")

    if title_newSeasons:
        return jsonify(title_newSeasons), 200
    else:
        return jsonify({'message': 'Nessuna nuova stagione disponibile'}), 200



# ---------- DOWNLOAD MONGO ------------
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

@app.route('/downloads', methods=['GET'])
def fetch_all_downloads():
    """
    Endpoint to fetch all downloads.
    """
    try:
        downloads = list(downloads_collection.find({}, {'_id': 0}))
        return jsonify(downloads), 200
    
    except Exception as e:
        logging.error(f"Error fetching all downloads: {str(e)}")
        return []

@app.route('/deleteEpisode', methods=['DELETE'])
def remove_episode():
    """
    Endpoint to delete a specific episode and its file.
    """
    try:
        series_id = request.args.get('id')
        season_number = request.args.get('season')
        episode_number = request.args.get('episode')

        if not series_id or not season_number or not episode_number:
            return jsonify({'error': 'Missing parameters (id, season, episode)'}), 400
        
        try:
            series_id = int(series_id)
            season_number = int(season_number)
            episode_number = int(episode_number)
        except ValueError:
            return jsonify({'error': 'Invalid season or episode number'}), 400

        # Trova il percorso del file
        episode = downloads_collection.find_one({
            'type': 'tv',
            'id': series_id,
            'n_s': season_number,
            'n_ep': episode_number
        }, {'_id': 0, 'path': 1})

        if not episode or 'path' not in episode:
            return jsonify({'error': 'Episode not found'}), 404

        file_path = episode['path']

        # Elimina il file fisico
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted episode file: {file_path}")
            else:
                logging.warning(f"Episode file not found: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting episode file: {str(e)}")

        # Rimuovi l'episodio dal database
        result = downloads_collection.delete_one({
            'type': 'tv',
            'id': series_id,
            'n_s': season_number,
            'n_ep': episode_number
        })

        if result.deleted_count > 0:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to delete episode from database'}), 500

    except Exception as e:
        logging.error(f"Error deleting episode: {str(e)}")
        return jsonify({'error': 'Failed to delete episode'}), 500

@app.route('/deleteMovie', methods=['DELETE'])
def remove_movie():
    """
    Endpoint to delete a specific movie, its file, and its parent folder if empty.
    """
    try:
        movie_id = request.args.get('id')

        if not movie_id:
            return jsonify({'error': 'Missing movie ID'}), 400

        # Trova il percorso del file
        movie = downloads_collection.find_one({'type': 'movie', 'id': movie_id}, {'_id': 0, 'path': 1})

        if not movie or 'path' not in movie:
            return jsonify({'error': 'Movie not found'}), 404

        file_path = movie['path']
        parent_folder = os.path.dirname(file_path)

        # Elimina il file fisico
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted movie file: {file_path}")
            else:
                logging.warning(f"Movie file not found: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting movie file: {str(e)}")

        # Elimina la cartella superiore se vuota
        try:
            if os.path.exists(parent_folder) and not os.listdir(parent_folder):
                os.rmdir(parent_folder)
                logging.info(f"Deleted empty parent folder: {parent_folder}")
        except Exception as e:
            logging.error(f"Error deleting parent folder: {str(e)}")

        # Rimuovi il film dal database
        result = downloads_collection.delete_one({'type': 'movie', 'id': movie_id})

        if result.deleted_count > 0:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to delete movie from database'}), 500

    except Exception as e:
        logging.error(f"Error deleting movie: {str(e)}")
        return jsonify({'error': 'Failed to delete movie'}), 500

@app.route('/moviePath', methods=['GET'])
def fetch_movie_path():
    """
    Endpoint to fetch the path of a specific movie.
    """
    try:
        movie_id = int(request.args.get('id'))

        if not movie_id:
            return jsonify({'error': 'Missing movie ID'}), 400

        movie = downloads_collection.find_one({'type': 'movie', 'id': movie_id}, {'_id': 0, 'path': 1})

        if movie and 'path' in movie:
            return jsonify({'path': movie['path']}), 200
        else:
            return jsonify({'error': 'Movie not found'}), 404

    except Exception as e:
        logging.error(f"Error fetching movie path: {str(e)}")
        return jsonify({'error': 'Failed to fetch movie path'}), 500

@app.route('/episodePath', methods=['GET'])
def fetch_episode_path():
    """
    Endpoint to fetch the path of a specific episode.
    """
    try:
        series_id = request.args.get('id')
        season_number = request.args.get('season')
        episode_number = request.args.get('episode')

        if not series_id or not season_number or not episode_number:
            return jsonify({'error': 'Missing parameters (id, season, episode)'}), 400

        try:
            series_id = int(series_id)
            season_number = int(season_number)
            episode_number = int(episode_number)
        except ValueError:
            return jsonify({'error': 'Invalid season or episode number'}), 400

        episode = downloads_collection.find_one({
            'type': 'tv',
            'id': series_id,
            'n_s': season_number,
            'n_ep': episode_number
        }, {'_id': 0, 'path': 1})

        if episode and 'path' in episode:
            return jsonify({'path': episode['path']}), 200
        else:
            return jsonify({'error': 'Episode not found'}), 404

    except Exception as e:
        logging.error(f"Error fetching episode path: {str(e)}")
        return jsonify({'error': 'Failed to fetch episode path'}), 500




if __name__ == '__main__':
    ensure_collections_exist(db)
    app.run(debug=True, port=1234, threaded=True)
