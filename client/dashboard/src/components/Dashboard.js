import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Button, Form, InputGroup } from 'react-bootstrap';

import SearchBar from './SearchBar.js';
import { API_URL } from './ApiUrl.js';

const Dashboard = () => {
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async (filter = '') => {
    try {
      const response = await axios.get(`${API_URL}/items?filter=${filter}`);
      setItems(response.data);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  };

  const handleSearch = (query) => {
    fetchItems(query);
  };

  return (
    <Container fluid className="p-4">
      <h1 className="mb-4">Dashboard</h1>
      
      <div className="d-flex justify-content-between align-items-center mb-4">
        <SearchBar onSearch={handleSearch} />
      </div>

    </Container>
  );
};

export default Dashboard;