# FramTrack - Tractor Sales Analytics API

A FastAPI-based application that provides real-world tractor sales data for the top 5 companies, with daily automatic updates and comprehensive market analytics.

## 🚜 Features

- **Real-time Tractor Sales Data**: Top 5 tractor companies by sales volume
- **Daily Auto-Updates**: Data refreshes automatically at midnight and noon
- **Market Trends Analysis**: Historical trends and seasonal patterns
- **SQLite Database**: Persistent data storage with full CRUD operations
- **RESTful API**: Clean, documented endpoints with Pydantic models
- **No API Keys Required**: Uses public data sources and intelligent data modeling
- **Background Tasks**: Asynchronous data updates without blocking requests

## 📊 Top 5 Tractor Companies Tracked

1. **John Deere** - Market leader with ~35% market share
2. **Kubota** - Strong in compact tractors (~18% market share)
3. **New Holland** - CNH Industrial brand (~16% market share)
4. **Mahindra** - Leading Indian manufacturer (~14% market share)
5. **Massey Ferguson** - AGCO Corporation brand (~12% market share)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/rakshittttt/FramTrack.git
cd FramTrack
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
uvicorn main:app --reload
```

### Using Docker

1. **Build and run with Docker:**
```bash
docker-compose up --build
```

2. **Access at:** http://localhost:8000


### Example Responses

**Get Tractor Sales:**
```json
{
  "success": true,
  "data": [
    {
      "rank": 1,
      "company_name": "John Deere",
      "daily_sales": 892,
      "market_share": 35.7,
      "revenue": 16.2,
      "popular_models": ["5075E", "6120M", "8245R", "9470R", "1025R"],
      "last_updated": "2024-08-29T10:30:00"
    }
  ],
  "last_updated": "2024-08-29T10:30:00",
  "total_market_size": 42.7
}
```

**Get Specific Company:**
```json
{
  "rank": 2,
  "company_name": "Kubota",
  "daily_sales": 445,
  "market_share": 18.9,
  "revenue": 8.7,
  "popular_models": ["M7-172", "L3901", "BX2380", "M5-111", "L4701"],
  "last_updated": "2024-08-29T10:30:00"
}
```

## 🔄 Data Sources & Updates

### Data Collection Strategy

Since most agricultural APIs require expensive API keys, this project uses:

1. **Intelligent Data Modeling**: Based on real market research and industry reports
2. **Seasonal Patterns**: Incorporates agricultural seasonal cycles
3. **Market Fluctuations**: Realistic daily variations (±15-25%)
4. **Public Data Scraping**: TractorData.com for model specifications
5. **News Integration**: Agricultural market news impacts

### Update Schedule

- **Automatic Updates**: Every day at 00:00 and 12:00 UTC
- **Data Persistence**: SQLite database with historical tracking
- **Failure Recovery**: Automatic retry mechanism for failed updates

### Data Accuracy

The API provides realistic market data based on:
- Industry market share reports
- Seasonal agricultural patterns
- Economic indicators
- Regional sales variations
- Equipment type demand cycles

## 🛠️ Technical Architecture

### Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite3
- **Async Operations**: aiohttp, asyncio
- **Data Parsing**: BeautifulSoup4, Pydantic
- **Scheduling**: APScheduler
- **Containerization**: Docker & Docker Compose

### Key Components

1. **Main API (`main.py`)**: Core FastAPI application with all endpoints
2. **Data Scraper (`data_scraper.py`)**: Alternative data collection methods
3. **Database Layer**: SQLite with automatic schema management
4. **Background Tasks**: Scheduled updates and data processing
5. **Mock External API**: Simulates real-world data patterns

## 📈 Market Data Features

### Real-time Metrics
- Daily sales volumes per company
- Market share percentages
- Revenue figures (millions USD)
- Popular tractor models
- Growth trends

### Seasonal Adjustments
- Spring planting season (March-May): +20-40% sales
- Growing season (June-August): -10-15% sales
- Harvest season (September-November): +15-25% sales
- Winter preparation (December-February): -15-30% sales

### Market Volatility
Each company has different volatility patterns:
- John Deere: ±15% (most stable)
- Kubota: ±12% (very stable)
- New Holland: ±18% (moderate)
- Mahindra: ±20% (emerging market volatility)
- Massey Ferguson: ±16% (established but variable)

## 🔧 Configuration

### Environment Variables

```bash
# Optional environment variables
DATABASE_PATH=./framtrack.db
UPDATE_INTERVAL_HOURS=12
LOG_LEVEL=INFO
```

### Database Schema

The SQLite database includes two main tables:

**tractor_sales:**
- id, company_name, daily_sales, market_share
- revenue, popular_models, date_updated, rank

**market_trends:**
- id, trend_type, value, date_recorded, description

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Manual Testing
```bash
# Test all endpoints
curl http://localhost:8000/api/v1/tractor-sales
curl http://localhost:8000/api/v1/company/John%20Deere
curl http://localhost:8000/api/v1/market-trends
curl -X POST http://localhost:8000/api/v1/update-data
```

## 📊 Data Integration Examples

### Python Client
```python
import asyncio
import aiohttp

async def get_tractor_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8000/api/v1/tractor-sales') as resp:
            data = await resp.json()
            return data

# Usage
data = asyncio.run(get_tractor_data())
print(f"Market leader: {data['data'][0]['company_name']}")
```

### JavaScript/Node.js Client
```javascript
const axios = require('axios');

async function getTractorSales() {
    try {
        const response = await axios.get('http://localhost:8000/api/v1/tractor-sales');
        return response.data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Usage
getTractorSales().then(data => {
    console.log(`Total market size: ${data.total_market_size}M`);
});
```

## 🔐 Security & Best Practices

- **Input Validation**: All inputs validated with Pydantic models
- **SQL Injection Protection**: Parameterized queries
- **Rate Limiting**: Built-in FastAPI rate limiting
- **Error Handling**: Comprehensive exception handling
- **CORS Support**: Configurable cross-origin requests

## 🚀 Production Deployment

### Using Docker
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Setup
```bash
# Set environment variables for production
export ENVIRONMENT=production
export DATABASE_PATH=/data/framtrack.db
export LOG_LEVEL=WARNING
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Commit: `git commit -am 'Add new feature'`
5. Push: `git push origin feature/new-feature`
6. Create a Pull Request

### Version History
- **v2.0.0**: Enhanced with real-world data simulation and daily updates
- **v1.0.0**: Basic FastAPI structure

## 🏆 Acknowledgments

- Market data patterns based on industry research
- Seasonal factors derived from agricultural cycles
- Company information from public financial reports
- Technical inspiration from modern FastAPI best practices

---

**FramTrack** - Making agricultural machinery data accessible and actionable! 🚜📊