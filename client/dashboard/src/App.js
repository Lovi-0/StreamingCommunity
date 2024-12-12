import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

import Navbar from './components/Navbar.js';
import Dashboard from './components/Dashboard.js';
import SearchResults from './components/SearchResult.js';
import TitleDetail from './components/TitleDetail.js';
import Watchlist from './components/Watchlist.js';
import Downloads from './components/Downloads.js';

function App() {
  const [theme, setTheme] = useState('dark'); // Default to dark mode

  // Toggle the theme
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('app-theme', newTheme); // Save user preference
  };

  // Load the saved theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('app-theme') || 'dark'; // Default to dark if no saved theme
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme); // Apply theme globally
  }, []);

  // Update the theme dynamically
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme); // Apply theme when changed
  }, [theme]);

  return (
    <Router>
      <Navbar toggleTheme={toggleTheme} theme={theme} />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/search" element={<SearchResults />} />
        <Route path="/title/:id" element={<TitleDetail />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/downloads" element={<Downloads />} />
      </Routes>
    </Router>
  );
}

export default App;