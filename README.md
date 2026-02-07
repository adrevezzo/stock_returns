# Stock Returns Application

A Flask web application for analyzing stock returns with historical price data and statistical analysis.

## Features

- **Real-time Stock Prices**: Fetches current prices using Yahoo Finance API
- **Historical Analysis**: Analyze price trends over custom date ranges
- **Return Statistics**: Calculate mean, standard deviation, confidence intervals, and more
- **Visual Charts**: Blue/orange color-coded charts for price action and return distributions
- **Options Strategy**: Suggests short put strike prices based on statistical analysis

## Technologies

- **Backend**: Flask 3.0.3, Python 3.11
- **Data**: yfinance, pandas, pandas-datareader
- **Visualization**: Matplotlib
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Security**: python-dotenv for environment variables, Flask-WTF for form handling

## Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd stock_returns
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Set your `FLASK_KEY` to a secure random string
   ```bash
   cp .env.example .env
   # Edit .env and set FLASK_KEY
   ```

5. **Run the application**
   ```bash
   python main.py
   ```
   Visit `http://localhost:5000` in your browser

## Deployment on Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create Render account**
   - Go to [render.com](https://render.com) and sign up

3. **Deploy**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` file
   - Click "Create Web Service"

4. **Environment Variables**
   - Render will auto-generate `FLASK_KEY`
   - Add any optional API keys if needed (not required for basic functionality)

## Usage

1. Enter a stock ticker symbol (e.g., AAPL, TSLA, MSFT)
2. Select start and end dates for historical analysis
3. Choose a return period (number of days)
4. Click "Get Data" to see:
   - Current stock price
   - Historical price chart
   - Return distribution histogram
   - Statistical metrics
   - Suggested options strike prices

## API Keys (Optional)

The app works out-of-the-box with Yahoo Finance (free, no API key needed). Optional alternative data sources:
- **Finnhub**: Set `FINN_STOCK_API_KEY` in `.env`
- **Alpha Vantage**: Set `ALPHA_STOCK_API_KEY` in `.env`

## License

MIT License - feel free to use and modify!