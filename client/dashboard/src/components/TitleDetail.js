import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { Container, Row, Col, Image, Button, Dropdown, Modal, Alert } from 'react-bootstrap';
import { FaDownload, FaPlay, FaPlus, FaTrash } from 'react-icons/fa';

import SearchBar from './SearchBar.js';

const API_BASE_URL = "http://127.0.0.1:1234";

const TitleDetail = () => {
  const [titleDetails, setTitleDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSeason, setSelectedSeason] = useState(1);
  const [episodes, setEpisodes] = useState([]);
  const [hoveredEpisode, setHoveredEpisode] = useState(null);
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [downloadStatus, setDownloadStatus] = useState({});
  const [showPlayer, setShowPlayer] = useState(false);
  const [currentVideo, setCurrentVideo] = useState("");
  const location = useLocation();

  useEffect(() => {
    const fetchTitleDetails = async () => {
      try {
        setLoading(true);
        const titleUrl = location.state?.url || location.pathname.split('/title/')[1];

        // Fetch title information
        const response = await axios.get(`${API_BASE_URL}/api/getInfo`, {
          params: { url: titleUrl }
        });
        
        const titleData = response.data;
        setTitleDetails(titleData);

        // Check download status
        await checkDownloadStatus(titleData);

        // Check watchlist status
        await checkWatchlistStatus(titleData.slug);

        // For TV shows, fetch first season episodes directly
        if (titleData.type === 'tv') {
          setEpisodes(titleData.episodes || []);
        }

        setLoading(false);
      } catch (error) {
        console.error("Error fetching title details:", error);
        setLoading(false);
      }
    };

    fetchTitleDetails();
  }, [location]);

  // Check if the movie/series is already downloaded
  const checkDownloadStatus = async (titleData) => {
    try {
      if (titleData.type === 'movie') {
        const response = await axios.get(`${API_BASE_URL}/downloads`);
        const downloadedMovie = response.data.find(
          download => download.type === 'movie' && download.slug === titleData.slug
        );
        setDownloadStatus({ 
          movie: { 
            downloaded: !!downloadedMovie, 
            path: downloadedMovie ? downloadedMovie.path : null 
          } 
        });
      } else if (titleData.type === 'tv') {
        const response = await axios.get(`${API_BASE_URL}/downloads`);
        const downloadedEpisodes = response.data.filter(
          download => download.type === 'tv' && download.slug === titleData.slug
        );
        
        const episodeStatus = {};
        downloadedEpisodes.forEach(episode => {
          episodeStatus[`S${episode.n_s}E${episode.n_ep}`] = {
            downloaded: true,
            path: episode.path
          };
        });
        setDownloadStatus({ tv: episodeStatus });
      }
    } catch (error) {
      console.error("Error checking download status:", error);
    }
  };

  // Check watchlist status
  const checkWatchlistStatus = async (slug) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/getWatchlist`);
      const inWatchlist = response.data.some(item => item.name === slug);
      setIsInWatchlist(inWatchlist);
    } catch (error) {
      console.error("Error checking watchlist status:", error);
    }
  };

  const handleSeasonSelect = async (seasonNumber) => {
    if (titleDetails.type === 'tv') {
      try {
        setLoading(true);
        const seasonResponse = await axios.get(`${API_BASE_URL}/api/getInfoSeason`, {
          params: { 
            url: location.state?.url,
            n: seasonNumber 
          }
        });
        
        setSelectedSeason(seasonNumber);
        setEpisodes(seasonResponse.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching season details:", error);
        setLoading(false);
      }
    }
  };

  const handleDownloadFilm = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/downloadFilm`, {
        params: {
          id: titleDetails.id,
          slug: titleDetails.slug
        }
      });
      const videoPath = response.data.path;
      
      // Update download status
      setDownloadStatus({
        movie: { 
          downloaded: true, 
          path: videoPath 
        }
      });
    } catch (error) {
      console.error("Error downloading film:", error);
      alert("Error downloading film. Please try again.");
    }
  };

  const handleDownloadEpisode = async (seasonNumber, episodeNumber) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/downloadEpisode`, {
        params: {
          n_s: seasonNumber,
          n_ep: episodeNumber
        }
      });
      const videoPath = response.data.path;
      
      // Update download status for this specific episode
      setDownloadStatus(prev => ({
        tv: {
          ...prev.tv,
          [`S${seasonNumber}E${episodeNumber}`]: {
            downloaded: true,
            path: videoPath
          }
        }
      }));
    } catch (error) {
      console.error("Error downloading episode:", error);
      alert("Error downloading episode. Please try again.");
    }
  };

  const handleWatchVideo = async (videoPath) => {
    if (!videoPath) {
      // If no path provided, attempt to get path from downloads
      try {
        let path;
        if (titleDetails.type === 'movie') {
          const response = await axios.get(`${API_BASE_URL}/moviePath`, {
            params: { id: titleDetails.id }
          });
          path = response.data.path;
        } else {
          alert("Please select a specific episode to watch.");
          return;
        }
        
        setCurrentVideo(path);
      } catch (error) {
        alert("Please download the content first.");
        return;
      }
    } else {
      setCurrentVideo(videoPath);
    }
    setShowPlayer(true);
  };

  const handleAddToWatchlist = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/addWatchlist`, {
        name: titleDetails.slug,
        url: location.state?.url || location.pathname.split('/title/')[1],
        season: titleDetails.season_count
      });
      setIsInWatchlist(true);
    } catch (error) {
      console.error("Error adding to watchlist:", error);
      alert("Error adding to watchlist. Please try again.");
    }
  };

  const handleRemoveFromWatchlist = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/removeWatchlist`, {
        name: titleDetails.slug
      });
      setIsInWatchlist(false);
    } catch (error) {
      console.error("Error removing from watchlist:", error);
      alert("Error removing from watchlist. Please try again.");
    }
  };

  if (loading) {
    return <div className="text-center mt-5">Loading...</div>;
  }

  if (!titleDetails) {
    return <Container>Title not found</Container>;
  }

  return (
    <Container fluid className="p-0">
      <SearchBar />
      
      {/* Background Image */}
      <div 
        style={{
          backgroundImage: `url(${titleDetails.image.background})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          height: '50vh',
          position: 'relative'
        }}
      >
        <div 
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)',
            padding: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <h1 className="text-white">{titleDetails.name}</h1>
          
          {/* Watchlist Button */}
          {titleDetails.type === 'tv' && (
            <div>
              {isInWatchlist ? (
                <Button 
                  variant="outline-light" 
                  onClick={handleRemoveFromWatchlist}
                >
                  <FaTrash className="me-2" /> Remove from Watchlist
                </Button>
              ) : (
                <Button 
                  variant="outline-light" 
                  onClick={handleAddToWatchlist}
                >
                  <FaPlus className="me-2" /> Add to Watchlist
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      <Container className="mt-4">
        {/* Plot */}
        <Row className="mb-4">
          <Col>
            <p>{titleDetails.plot}</p>
          </Col>
        </Row>

        {/* Download/Watch Button for Movies */}
        {titleDetails.type === 'movie' && (
          <Row className="mb-4">
            <Col>
              {downloadStatus.movie?.downloaded ? (
                <Button 
                  variant="success" 
                  onClick={() => handleWatchVideo(downloadStatus.movie.path)}
                >
                  <FaPlay className="me-2" /> Watch
                </Button>
              ) : (
                <Button 
                  variant="primary" 
                  onClick={handleDownloadFilm}
                >
                  <FaDownload className="me-2" /> Download Film
                </Button>
              )}
            </Col>
          </Row>
        )}

        {/* TV Show Seasons and Episodes */}
        {titleDetails.type === 'tv' && (
          <>
            <Row className="mb-3">
              <Col>
                <Dropdown>
                  <Dropdown.Toggle variant="secondary">
                    Season {selectedSeason}
                  </Dropdown.Toggle>

                  <Dropdown.Menu>
                    {[...Array(titleDetails.season_count)].map((_, index) => (
                      <Dropdown.Item 
                        key={index + 1} 
                        onClick={() => handleSeasonSelect(index + 1)}
                      >
                        Season {index + 1}
                      </Dropdown.Item>
                    ))}
                  </Dropdown.Menu>
                </Dropdown>
              </Col>
            </Row>

            <Row xs={2} md={4} className="g-4">
              {episodes.map((episode) => {
                const episodeKey = `S${selectedSeason}E${episode.number}`;
                const isDownloaded = downloadStatus.tv?.[episodeKey]?.downloaded;
                
                return (
                  <Col key={episode.id}>
                    <div className="episode-thumbnail-wrapper position-relative">
                      <Image 
                        src={episode.image} 
                        alt={`Episode ${episode.number}`} 
                        fluid 
                        rounded 
                        className="mb-2"
                      />
                      <div 
                        className="episode-number position-absolute top-0 start-0 m-2 px-2 py-1" 
                        style={{
                          backgroundColor: 'rgba(255, 255, 255, 0.7)', 
                          color: '#333', 
                          borderRadius: '4px',
                          fontSize: '0.8rem'
                        }}
                      >
                        Ep {episode.number}
                      </div>
                      <h6>{episode.name}</h6>
                      
                      {isDownloaded ? (
                        <Button 
                          variant="success" 
                          onClick={() => handleWatchVideo(downloadStatus.tv[episodeKey].path)}
                        >
                          <FaPlay className="me-2" /> Watch
                        </Button>
                      ) : (
                        <Button 
                          variant="primary" 
                          onClick={() => handleDownloadEpisode(selectedSeason, episode.number)}
                        >
                          <FaDownload className="me-2" /> Download
                        </Button>
                      )}
                    </div>
                  </Col>
                );
              })}
            </Row>
          </>
        )}
      </Container>

      {/* Modal Video Player */}
      <Modal show={showPlayer} onHide={() => setShowPlayer(false)} size="lg" centered>
        <Modal.Body>
          <video 
            src={`http://127.0.0.1:1234/downloaded/${currentVideo}`} 
            controls 
            autoPlay 
            style={{ width: '100%' }}
          />
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default TitleDetail;