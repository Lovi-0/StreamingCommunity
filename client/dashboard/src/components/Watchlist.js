import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Button, Badge, Alert, Modal } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaTrash, FaDownload } from 'react-icons/fa';

import { SERVER_WATCHLIST_URL, API_URL } from './ApiUrl';

const Watchlist = () => {
  const [watchlistItems, setWatchlistItems] = useState([]);
  const [newSeasons, setNewSeasons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newSeasonsMessage, setNewSeasonsMessage] = useState("");  // Stato per il messaggio delle nuove stagioni

  // Nuovo stato per la gestione del modal di download
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [seasonsToDownload, setSeasonsToDownload] = useState([]);
  const [downloadProgress, setDownloadProgress] = useState({
    status: 'idle', // 'idle', 'downloading', 'completed', 'error'
    current: 0,
    total: 0
  });

  // Funzione per recuperare i dati della watchlist
  const fetchWatchlistData = async () => {
    try {
      const watchlistResponse = await axios.get(`${SERVER_WATCHLIST_URL}/get`);
      setWatchlistItems(watchlistResponse.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching watchlist:", error);
      setLoading(false);
    }
  };

  // Funzione per controllare se ci sono nuove stagioni (attivata dal bottone)
  const checkNewSeasons = async () => {
    try {
      const newSeasonsResponse = await axios.get(`${SERVER_WATCHLIST_URL}/checkNewSeason`);
      
      if (Array.isArray(newSeasonsResponse.data) && newSeasonsResponse.data.length > 0) {
        setNewSeasons(newSeasonsResponse.data);
        setSeasonsToDownload(newSeasonsResponse.data);
        setShowDownloadModal(true);

        const titlesWithNewSeasons = newSeasonsResponse.data.map(season => season.name);
        setNewSeasonsMessage(`Nuove stagioni disponibili per: ${titlesWithNewSeasons.join(", ")}`);
      } else {
        setNewSeasons([]);
        setNewSeasonsMessage("Nessuna nuova stagione disponibile.");
      }
    } catch (error) {
      console.error("Error fetching new seasons:", error);
      setNewSeasonsMessage("Errore nel recuperare le nuove stagioni.");
    }
  };

  // Funzione per inviare la richiesta POST per aggiornare il titolo nella watchlist
  const updateTitlesWithNewSeasons = async (newSeasonsList) => {
    try {
      for (const season of newSeasonsList) {
        // Manda una richiesta POST per ogni titolo con nuove stagioni
        console.log(`Updated watchlist for ${season.name} with new season ${season.nNewSeason}, url: ${season.title_url}`);
        
        await axios.post(`${SERVER_WATCHLIST_URL}/update`, {
          url: season.title_url,
          season: season.season
        });
        
      }
    } catch (error) {
      console.error("Error updating title watchlist:", error);
    }
  };

  const downloadNewSeasons = async () => {
    try {
      setDownloadProgress({
        status: 'downloading',
        current: 0,
        total: seasonsToDownload.length
      });
      for (const [index, season] of seasonsToDownload.entries()) {
        try {
          // Request complete series information
          const seriesInfoResponse = await axios.get(`${API_URL}/getInfo`, {
            params: { url: season.title_url }
          });
          
          // Download entire season
          const seasonResponse = await axios.get(`${API_URL}/getInfoSeason`, {
            params: { 
              url: season.title_url,
              n: season.nNewSeason 
            }
          });
          
          // Download each episode of the season
          for (const episode of seasonResponse.data) {
            await axios.get(`${API_URL}/download/episode`, {
              params: {
                n_s: season.nNewSeason,
                n_ep: episode.number,
                media_id: seriesInfoResponse.data.id,
                series_name: seriesInfoResponse.data.slug
              }
            });
          }
          
          // Update watchlist with new season
          await axios.post(`${SERVER_WATCHLIST_URL}/update`, {
            url: season.title_url,
            season: season.season
          });
          
          // Update progress
          setDownloadProgress(prev => ({
            ...prev,
            current: index + 1,
            status: index + 1 === seasonsToDownload.length ? 'completed' : 'downloading'
          }));
        } catch (error) {
          console.error(`Errore durante lo scaricamento della stagione ${season.name}:`, error);
        }
      }
      
      // Close modal after completion
      setShowDownloadModal(false);
      
      // Reload watchlist to show updates
      fetchWatchlistData();
    } catch (error) {
      console.error("Errore durante lo scaricamento delle nuove stagioni:", error);
      setDownloadProgress({
        status: 'error',
        current: 0,
        total: 0
      });
    }
  };

  // Funzione per rimuovere un elemento dalla watchlist
  const handleRemoveFromWatchlist = async (serieName) => {
    try {
      await axios.post(`${SERVER_WATCHLIST_URL}/remove`, { name: serieName });

      // Aggiorna lo stato locale per rimuovere l'elemento dalla watchlist
      setWatchlistItems((prev) => prev.filter((item) => item.name !== serieName));
    } catch (error) {
      console.error("Error removing from watchlist:", error);
    }
  };

  // Carica inizialmente la watchlist
  useEffect(() => {
    fetchWatchlistData();
  }, []);

  if (loading) {
    return <div className="text-center mt-5">Loading...</div>;
  }

  return (
    <Container fluid className="p-0">
      <Container className="mt-4">
        <h2 className="mb-4">My Watchlist</h2>
        
        <Button onClick={checkNewSeasons} variant="primary" className="mb-4">
          Check for New Seasons
        </Button>

        {/* Mostra il messaggio sulle nuove stagioni */}
        {newSeasonsMessage && (
          <Alert variant={newSeasonsMessage.includes("Nuove stagioni") ? "success" : "info"}>
            {newSeasonsMessage}
          </Alert>
        )}

        {watchlistItems.length === 0 ? (
          <p>Your watchlist is empty.</p>
        ) : (
          <Row xs={1} md={3} className="g-4">
            {watchlistItems.map((item) => {
              const hasNewSeason = newSeasons && Array.isArray(newSeasons) && newSeasons.some(
                (season) => season.name === item.name
              );

              return (
                <Col key={item.name}>
                  <Card>
                    <Card.Body>
                      <div className="d-flex justify-content-between align-items-start">
                        <Card.Title>
                          {item.name.replace(/-/g, ' ')}
                          {hasNewSeason && (
                            <Badge bg="danger" className="ms-2">New Season</Badge>
                          )}
                        </Card.Title>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleRemoveFromWatchlist(item.name)}
                        >
                          <FaTrash />
                        </Button>
                      </div>
                      <Card.Text>
                        <small>
                          Added on: {new Date(item.added_on).toLocaleDateString()}
                        </small>
                        <br />
                        <small>Seasons: {item.season}</small>
                      </Card.Text>
                      <Link
                        to={`/title/${item.name}`}
                        state={{ url: item.title_url }}
                        className="btn btn-primary btn-sm mt-2"
                      >
                        View Details
                      </Link>
                    </Card.Body>
                  </Card>
                </Col>
              );
            })}
          </Row>
        )}
      </Container>


     <Modal show={showDownloadModal} onHide={() => setShowDownloadModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Nuove Stagioni Disponibili</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Sono disponibili nuove stagioni per i seguenti titoli:</p>
          <ul>
            {seasonsToDownload.map((season) => (
              <li key={season.name}>
                {season.name.replace(/-/g, ' ')} - Stagione {season.nNewSeason}
              </li>
            ))}
          </ul>

          {downloadProgress.status !== 'idle' && (
            <div className="mt-3">
              <p>Progresso download:</p>
              <div className="progress">
                <div 
                  className={`progress-bar ${
                    downloadProgress.status === 'completed' ? 'bg-success' : 
                    downloadProgress.status === 'error' ? 'bg-danger' : 'bg-primary'
                  }`} 
                  role="progressbar" 
                  style={{width: `${(downloadProgress.current / downloadProgress.total) * 100}%`}}
                  aria-valuenow={(downloadProgress.current / downloadProgress.total) * 100}
                  aria-valuemin="0" 
                  aria-valuemax="100"
                >
                  {downloadProgress.current}/{downloadProgress.total} Stagioni
                </div>
              </div>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDownloadModal(false)}>
            Annulla
          </Button>
          <Button 
            variant="primary" 
            onClick={downloadNewSeasons}
            disabled={downloadProgress.status === 'downloading'}
          >
            <FaDownload className="me-2" />
            Scarica Nuove Stagioni
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Watchlist;
