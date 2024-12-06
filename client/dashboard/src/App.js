import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

import Navbar from './components/Navbar.js';
import Dashboard from './components/Dashboard.js';
import SearchResults from './components/SearchResult.js';
import TitleDetail from './components/TitleDetail.js';
import Watchlist from './components/Watchlist.js';
import Downloads from './components/Downloads.js';

function App() {
  return (
    <Router>
      <Navbar />
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