import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Row, Col, Card, Spinner } from 'react-bootstrap';

import SearchBar from './SearchBar.js';

const API_BASE_URL = "http://127.0.0.1:1234";

const SearchResults = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const query = searchParams.get('q');

    const fetchSearchResults = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/api/search`, {
          params: { q: query }
        });
        setResults(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching search results:", error);
        setLoading(false);
      }
    };

    if (query) {
      fetchSearchResults();
    }
  }, [location.search]);

  const handleItemClick = (item) => {
    navigate(`/title/${item.id}-${item.slug}`, { 
      state: { 
        url: item.url  // Pass the full URL to the TitleDetail component
      } 
    });
  };

  return (
    <Container fluid className="p-4">
      <div className="mb-4">
        <SearchBar />
      </div>

      <h2 className="mb-4">Search Results</h2>

      {loading ? (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      ) : (
        <Row xs={2} md={4} lg={6} className="g-4">
          {results.map((item) => (
            <Col key={item.id}>
              <Card 
                className="h-100 hover-zoom" 
                onClick={() => handleItemClick(item)}
                style={{ cursor: 'pointer' }}
              >
                <Card.Img 
                  variant="top" 
                  src={item.images.poster || item.images.cover} 
                  alt={item.name}
                  style={{ 
                    height: '300px', 
                    objectFit: 'cover' 
                  }}
                />
                <Card.Body>
                  <Card.Title>{item.name}</Card.Title>
                  <Card.Text>
                    {item.year} • {item.type === 'tv' ? 'TV Series' : 'Movie'}
                    {item.type === 'tv' && ` • ${item.seasons_count} Seasons`}
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Container>
  );
};

export default SearchResults;