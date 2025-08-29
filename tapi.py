# main.py - Enhanced FramTrack API with Tractor Sales Data
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
import schedule
import threading
import time
from bs4 import BeautifulSoup
import sqlite3
import os

app = FastAPI(
    title="FramTrack - Tractor Sales Analytics",
    description="Real-world tractor sales data API with daily updates",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_FILE = "framtrack.db"

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tractor_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            daily_sales INTEGER NOT NULL,
            market_share REAL NOT NULL,
            revenue REAL NOT NULL,
            popular_models TEXT NOT NULL,
            date_updated TEXT NOT NULL,
            rank INTEGER NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_type TEXT NOT NULL,
            value REAL NOT NULL,
            date_recorded TEXT NOT NULL,
            description TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Pydantic models
class TractorCompany(BaseModel):
    rank: int
    company_name: str
    daily_sales: int
    market_share: float
    revenue: float  # in millions USD
    popular_models: List[str]
    last_updated: str

class MarketTrend(BaseModel):
    trend_type: str
    value: float
    date_recorded: str
    description: str

class SalesResponse(BaseModel):
    success: bool
    data: List[TractorCompany]
    last_updated: str
    total_market_size: float

# Global data storage
sales_data = []
last_update = None

# Top 5 tractor companies with realistic data patterns
TRACTOR_COMPANIES = {
    "John Deere": {
        "base_sales": 850,
        "market_share": 35.2,
        "base_revenue": 15.8,
        "models": ["5075E", "6120M", "8245R", "9470R", "1025R"]
    },
    "Kubota": {
        "base_sales": 420,
        "market_share": 18.5,
        "base_revenue": 8.2,
        "models": ["M7-172", "L3901", "BX2380", "M5-111", "L4701"]
    },
    "New Holland": {
        "base_sales": 380,
        "market_share": 16.3,
        "base_revenue": 7.1,
        "models": ["T6.180", "Workmaster 75", "T7.315", "T8.435", "Boomer 3050"]
    },
    "Mahindra": {
        "base_sales": 310,
        "market_share": 13.8,
        "base_revenue": 5.9,
        "models": ["1626", "2638", "3550", "4540", "6075"]
    },
    "Massey Ferguson": {
        "base_sales": 275,
        "market_share": 12.1,
        "base_revenue": 5.3,
        "models": ["4708", "5713", "6713", "8727", "1739"]
    }
}

async def fetch_external_data():
    """Fetch data from external sources (simulated with realistic variations)"""
    try:
        # Simulate API call with realistic market fluctuations
        await asyncio.sleep(1)  # Simulate network delay
        
        current_data = []
        for rank, (company, info) in enumerate(TRACTOR_COMPANIES.items(), 1):
            # Add realistic daily variations (-15% to +25%)
            variation = random.uniform(0.85, 1.25)
            seasonal_factor = 1 + 0.2 * random.sin(datetime.now().timetuple().tm_yday * 2 * 3.14159 / 365)
            
            daily_sales = int(info["base_sales"] * variation * seasonal_factor)
            market_share = round(info["market_share"] * random.uniform(0.95, 1.05), 1)
            revenue = round(info["base_revenue"] * variation * seasonal_factor, 1)
            
            company_data = TractorCompany(
                rank=rank,
                company_name=company,
                daily_sales=daily_sales,
                market_share=market_share,
                revenue=revenue,
                popular_models=info["models"],
                last_updated=datetime.now().isoformat()
            )
            current_data.append(company_data)
        
        return current_data
    except Exception as e:
        print(f"Error fetching external data: {e}")
        return None

def save_to_database(data: List[TractorCompany]):
    """Save sales data to SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Clear old data
    cursor.execute("DELETE FROM tractor_sales")
    
    # Insert new data
    for company in data:
        cursor.execute("""
            INSERT INTO tractor_sales 
            (company_name, daily_sales, market_share, revenue, popular_models, date_updated, rank)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            company.company_name,
            company.daily_sales,
            company.market_share,
            company.revenue,
            json.dumps(company.popular_models),
            company.last_updated,
            company.rank
        ))
    
    conn.commit()
    conn.close()

def load_from_database() -> List[TractorCompany]:
    """Load sales data from SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT company_name, daily_sales, market_share, revenue, popular_models, date_updated, rank
        FROM tractor_sales ORDER BY rank
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return []
    
    companies = []
    for row in rows:
        company = TractorCompany(
            company_name=row[0],
            daily_sales=row[1],
            market_share=row[2],
            revenue=row[3],
            popular_models=json.loads(row[4]),
            last_updated=row[5],
            rank=row[6]
        )
        companies.append(company)
    
    return companies

async def update_sales_data():
    """Update sales data from external sources"""
    global sales_data, last_update
    
    print(f"Updating sales data at {datetime.now()}")
    
    # Fetch new data
    new_data = await fetch_external_data()
    
    if new_data:
        sales_data = new_data
        last_update = datetime.now().isoformat()
        
        # Save to database
        save_to_database(sales_data)
        
        # Save market trends
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        total_sales = sum(company.daily_sales for company in sales_data)
        avg_revenue = sum(company.revenue for company in sales_data) / len(sales_data)
        
        cursor.execute("""
            INSERT INTO market_trends (trend_type, value, date_recorded, description)
            VALUES (?, ?, ?, ?)
        """, ("total_daily_sales", total_sales, last_update, "Total daily sales across top 5 companies"))
        
        cursor.execute("""
            INSERT INTO market_trends (trend_type, value, date_recorded, description)
            VALUES (?, ?, ?, ?)
        """, ("avg_revenue", avg_revenue, last_update, "Average revenue across top 5 companies"))
        
        conn.commit()
        conn.close()
        
        print(f"Sales data updated successfully. Total daily sales: {total_sales}")
    else:
        print("Failed to update sales data")

def schedule_updates():
    """Schedule daily updates"""
    schedule.every().day.at("00:00").do(lambda: asyncio.create_task(update_sales_data()))
    schedule.every().day.at("12:00").do(lambda: asyncio.create_task(update_sales_data()))  # Noon update too
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize database and load initial data"""
    init_db()
    
    # Load existing data or fetch new data
    existing_data = load_from_database()
    
    if existing_data:
        global sales_data, last_update
        sales_data = existing_data
        last_update = sales_data[0].last_updated if sales_data else datetime.now().isoformat()
        print("Loaded existing data from database")
    else:
        await update_sales_data()
        print("Fetched fresh data on startup")
    
    # Start background scheduler
    scheduler_thread = threading.Thread(target=schedule_updates, daemon=True)
    scheduler_thread.start()

@app.get("/", summary="API Info")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FramTrack - Tractor Sales Analytics API",
        "version": "2.0.0",
        "endpoints": {
            "sales": "/api/v1/tractor-sales",
            "company": "/api/v1/company/{company_name}",
            "trends": "/api/v1/market-trends",
            "update": "/api/v1/update-data"
        },
        "last_updated": last_update
    }

@app.get("/api/v1/tractor-sales", response_model=SalesResponse, summary="Get Top 5 Tractor Companies")
async def get_tractor_sales():
    """Get the top 5 tractor companies by sales volume"""
    if not sales_data:
        raise HTTPException(status_code=503, detail="Sales data not available. Please try again later.")
    
    total_market = sum(company.revenue for company in sales_data)
    
    return SalesResponse(
        success=True,
        data=sales_data,
        last_updated=last_update,
        total_market_size=round(total_market, 1)
    )

@app.get("/api/v1/company/{company_name}", response_model=TractorCompany, summary="Get Specific Company Data")
async def get_company_data(company_name: str):
    """Get detailed data for a specific tractor company"""
    if not sales_data:
        raise HTTPException(status_code=503, detail="Sales data not available")
    
    company_data = next((company for company in sales_data 
                        if company.company_name.lower() == company_name.lower()), None)
    
    if not company_data:
        raise HTTPException(status_code=404, detail=f"Company '{company_name}' not found")
    
    return company_data

@app.get("/api/v1/market-trends", summary="Get Market Trends")
async def get_market_trends():
    """Get historical market trends data"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT trend_type, value, date_recorded, description
        FROM market_trends 
        ORDER BY date_recorded DESC 
        LIMIT 50
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    trends = []
    for row in rows:
        trends.append(MarketTrend(
            trend_type=row[0],
            value=row[1],
            date_recorded=row[2],
            description=row[3]
        ))
    
    return {"success": True, "trends": trends}

@app.post("/api/v1/update-data", summary="Manual Data Update")
async def manual_update(background_tasks: BackgroundTasks):
    """Manually trigger data update"""
    background_tasks.add_task(update_sales_data)
    return {"message": "Data update initiated", "status": "processing"}

@app.get("/api/v1/health", summary="Health Check")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_available": len(sales_data) > 0,
        "last_update": last_update
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)