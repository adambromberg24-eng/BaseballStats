# Baseball Statistics Aggregator

A Streamlit web application for tracking and analyzing baseball statistics from MLB games you've attended.

## Features

- **User Authentication**: Secure login and registration system
- **Game Tracking**: Add games you've attended with automatic MLB data fetching
- **Player Statistics**: Comprehensive batting and pitching statistics
- **Interactive Dashboard**: Visualizations and analytics
- **Data Export**: Export your data in JSON or CSV format

## Deployment to Streamlit Cloud

### Prerequisites

1. GitHub account
2. Streamlit Cloud account (free at https://share.streamlit.io)

### Setup Steps

1. **Push to GitHub**: Push this repository to your GitHub account
2. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Click "New app"
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to `app.py`
   - Click "Deploy"

### Configuration

The app uses local file storage for data persistence. For production deployment, consider:

- Using a cloud database (PostgreSQL, MongoDB, etc.)
- Implementing proper user session management
- Setting up environment-specific configuration

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

3. Open your browser to `http://localhost:8501`

## Project Structure

- `app.py` - Main Streamlit application
- `auth_manager.py` - User authentication management
- `data_manager.py` - Data persistence and management
- `stats_calculator.py` - Statistical calculations
- `mlb_api_client.py` - MLB API integration
- `config.yaml` - User credentials configuration
- `requirements.txt` - Python dependencies

## Authentication

Default users (for demo purposes):
- Username: `admin` / Password: `admin123`
- Username: `adambromberg` / Password: `password123`
- Username: `Ethanshulman15` / Password: `password123`

**Note**: Change these credentials before production deployment!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.
