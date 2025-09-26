# Baseball Statistics Aggregator

## Overview

A comprehensive Streamlit-based web application for tracking and analyzing baseball statistics from MLB games you've attended. The application allows users to add games they've watched, automatically fetch game data from the MLB API, and generate detailed statistical analysis and visualizations for individual players and teams. Built with a modular architecture featuring separate components for data management, statistics calculation, and API integration.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid prototyping and deployment
- **Navigation**: Multi-page application with sidebar navigation including Add Game, My Games, Player Stats, Dashboard, and Export Data pages
- **Visualization**: Plotly integration for interactive charts and graphs
- **State Management**: Streamlit session state for maintaining application state across user interactions

### Backend Architecture
- **Data Layer**: JSON-based file storage system managed by DataManager class
- **Business Logic**: Modular design with separate classes for different responsibilities:
  - `DataManager`: Handles all data persistence operations and CRUD functionality
  - `StatsCalculator`: Computes aggregate statistics, batting averages, and performance metrics
  - `MLBApiClient`: Interfaces with MLB's official API for real-time game data
- **Data Flow**: Clean separation between data access, business logic, and presentation layers

### Data Storage
- **Primary Storage**: JSON file (`baseball_data.json`) for local data persistence
- **Schema**: Game-centric data model storing complete game information including:
  - Game metadata (date, teams, scores, venue)
  - Player statistics (batting and pitching for both teams)
  - User annotations (notes, attendance tracking)
- **Caching**: In-memory caching for team data to reduce API calls

### API Integration
- **MLB API**: Integration with statsapi library for official MLB data
- **Data Enrichment**: Automatic fetching of complete game statistics when users add games they attended
- **Error Handling**: Graceful degradation when API is unavailable

## External Dependencies

### Core Framework
- **Streamlit**: Web application framework for building the user interface
- **Pandas**: Data manipulation and analysis library for statistical calculations
- **Plotly**: Interactive visualization library for charts and graphs

### MLB Data Integration
- **statsapi**: Official MLB statistics API client for fetching real-time game data and historical statistics

### Data Processing
- **JSON**: Built-in Python library for data serialization and persistence
- **datetime**: Built-in Python library for date and time handling
- **collections**: Built-in Python library for specialized data structures (defaultdict for statistics aggregation)

### Development Dependencies
- **os**: File system operations for data file management
- **typing**: Type hints for better code documentation and IDE support