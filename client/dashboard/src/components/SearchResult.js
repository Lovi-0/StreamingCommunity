import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Row, Col, Card, Spinner } from 'react-bootstrap';

import SearchBar from './SearchBar.js';
import { API_URL } from './ApiUrl.js';

const SearchResults = ({ theme }) => {
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
        const response = await axios.get(`${API_URL}/search`, {
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
    <Container fluid className="p-4" style={{ 
      backgroundColor: theme === 'dark' ? '#121212' : '#ffffff', 
      color: theme === 'dark' ? '#ffffff' : '#000000' 
    }}>
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

SearchResults.propTypes = {
  toggleTheme: PropTypes.func.isRequired,
  theme: PropTypes.oneOf(['light', 'dark']).isRequired,
};


export default SearchResults;