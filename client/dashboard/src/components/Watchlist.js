import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Button, Badge, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaTrash } from 'react-icons/fa';

const API_BASE_URL = "http://127.0.0.1:1234";

const Watchlist = () => {
  const [watchlistItems, setWatchlistItems] = useState([]);
  const [newSeasons, setNewSeasons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newSeasonsMessage, setNewSeasonsMessage] = useState("");  // Stato per il messaggio delle nuove stagioni

  // Funzione per recuperare i dati della watchlist
  const fetchWatchlistData = async () => {
    try {
      const watchlistResponse = await axios.get(`${API_BASE_URL}/api/getWatchlist`);
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
      const newSeasonsResponse = await axios.get(`${API_BASE_URL}/api/checkWatchlist`);
      
      if (Array.isArray(newSeasonsResponse.data)) {
        setNewSeasons(newSeasonsResponse.data);

        // Crea un messaggio per i titoli con nuove stagioni
        const titlesWithNewSeasons = newSeasonsResponse.data.map(season => season.name);
        if (titlesWithNewSeasons.length > 0) {
          setNewSeasonsMessage(`Nuove stagioni disponibili per: ${titlesWithNewSeasons.join(", ")}`);
          
          // Dopo aver mostrato il messaggio, aggiorniamo i titoli con le nuove stagioni
          updateTitlesWithNewSeasons(newSeasonsResponse.data);
        } else {
          setNewSeasonsMessage("Nessuna nuova stagione disponibile.");
        }
      } else {
        setNewSeasons([]);  // In caso contrario, non ci sono nuove stagioni
        setNewSeasonsMessage("Nessuna nuova stagione disponibile.");
      }
    } catch (error) {
      console.error("Error fetching new seasons:", error);
    }
  };

  // Funzione per inviare la richiesta POST per aggiornare il titolo nella watchlist
  const updateTitlesWithNewSeasons = async (newSeasonsList) => {
    try {
      for (const season of newSeasonsList) {
        // Manda una richiesta POST per ogni titolo con nuove stagioni
        console.log(`Updated watchlist for ${season.name} with new season ${season.nNewSeason}, url: ${season.title_url}`);
        
        await axios.post(`${API_BASE_URL}/api/updateTitleWatchlist`, {
          url: season.title_url,
          season: season.season
        });
        
      }
    } catch (error) {
      console.error("Error updating title watchlist:", error);
    }
  };

  // Funzione per rimuovere un elemento dalla watchlist
  const handleRemoveFromWatchlist = async (serieName) => {
    try {
      await axios.post(`${API_BASE_URL}/api/removeWatchlist`, { name: serieName });

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
    </Container>
  );
};

export default Watchlist;
