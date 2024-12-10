import React from 'react';
import PropTypes from 'prop-types'; // Importa PropTypes
import { Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

const Navbar = ({ toggleTheme, theme }) => {
  return (
    <nav className={`navbar navbar-expand-lg ${theme === 'dark' ? 'navbar-dark bg-dark' : 'navbar-light bg-light'}`}>
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">Home</Link> {/* Link alla Home */}
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav">
            <li className="nav-item">
              <Link className="nav-link" to="/watchlist">Watchlist</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/downloads">Downloads</Link>
            </li>
          </ul>
          <button
            className="btn btn-outline-secondary ms-auto"
            onClick={toggleTheme}
          >
            {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
          </button>
        </div>
      </div>
    </nav>
  );
};

// Validazione delle proprietà
Navbar.propTypes = {
  toggleTheme: PropTypes.func.isRequired, // Deve essere una funzione
  theme: PropTypes.oneOf(['light', 'dark']).isRequired, // Deve essere 'light' o 'dark'
};

export default Navbar;