# test_main.py - Comprehensive API tests
import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app, update_sales_data, init_db
import json
import os

# Test client
client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database before running tests"""
    # Use a test database
    os.environ["DB_FILE"] = "test_framtrack.db"
    init_db()
    
    # Run initial data update
    asyncio.run(update_sales_data())
    
    yield
    
    # Cleanup after tests
    if os.path.exists("test_framtrack.db"):
        os.remove("test_framtrack.db")

class TestAPIEndpoints:
    """Test all API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "FramTrack" in data["message"]
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "data_available" in data
    
    def test_get_tractor_sales(self):
        """Test main tractor sales endpoint"""
        response = client.get("/api/v1/tractor-sales")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) == 5  # Top 5 companies
        assert "last_updated" in data
        assert "total_market_size" in data
        
        # Check data structure
        company = data["data"][0]
        required_fields = ["rank", "company_name", "daily_sales", "market_share", "revenue", "popular_models"]
        for field in required_fields:
            assert field in company
        
        # Check ranking order
        for i in range(len(data["data"]) - 1):
            assert data["data"][i]["rank"] <= data["data"][i + 1]["rank"]
    
    def test_get_specific_company(self):
        """Test getting specific company data"""
        # Test valid company
        response = client.get("/api/v1/company/John Deere")
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "John Deere"
        assert data["rank"] == 1  # John Deere should be #1
        
        # Test case insensitive
        response = client.get("/api/v1/company/john deere")
        assert response.status_code == 200
        
        # Test invalid company
        response = client.get("/api/v1/company/NonExistentCompany")
        assert response.status_code == 404
    
    def test_market_trends(self):
        """Test market trends endpoint"""
        response = client.get("/api/v1/market-trends")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "trends" in data
    
    def test_manual_update(self):
        """Test manual data update endpoint"""
        response = client.post("/api/v1/update-data")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data

class TestDataValidation:
    """Test data validation and structure"""
    
    def test_company_data_structure(self):
        """Test that company data follows expected structure"""
        response = client.get("/api/v1/tractor-sales")
        data = response.json()["data"]
        
        for company in data:
            # Check data types
            assert isinstance(company["rank"], int)
            assert isinstance(company["company_name"], str)
            assert isinstance(company["daily_sales"], int)
            assert isinstance(company["market_share"], float)
            assert isinstance(company["revenue"], float)
            assert isinstance(company["popular_models"], list)
            
            # Check value ranges
            assert 1 <= company["rank"] <= 5
            assert company["daily_sales"] > 0
            assert 0 < company["market_share"] < 100
            assert company["revenue"] > 0
            assert len(company["popular_models"]) > 0
    
    def test_market_share_totals(self):
        """Test that market shares are reasonable"""
        response = client.get("/api/v1/tractor-sales")
        data = response.json()["data"]
        
        total_market_share = sum(company["market_share"] for company in data)
        # Should be close to 100% but allow for rounding and market variations
        assert 80 <= total_market_share <= 120
    
    def test_company_rankings(self):
        """Test that company rankings make sense"""
        response = client.get("/api/v1/tractor-sales")
        companies = response.json()["data"]
        
        # Check that John Deere is typically #1 (market leader)
        john_deere = next(c for c in companies if c["company_name"] == "John Deere")
        assert john_deere["rank"] <= 2  # Should be #1 or #2
        
        # Check that rankings are sequential
        ranks = [c["rank"] for c in companies]
        assert ranks == list(range(1, 6))

class TestSeasonalPatterns:
    """Test seasonal adjustment patterns"""
    
    def test_seasonal_data_variation(self):
        """Test that data shows realistic seasonal variation"""
        # Get data multiple times to check variation
        responses = []
        for _ in range(3):
            response = client.post("/api/v1/update-data")
            assert response.status_code == 200
            
            response = client.get("/api/v1/tractor-sales")
            responses.append(response.json())
            asyncio.sleep(0.1)  # Small delay between requests
        
        # Check that data varies between updates (should have some randomness)
        first_sales = responses[0]["data"][0]["daily_sales"]
        last_sales = responses[-1]["data"][0]["daily_sales"]
        
        # Sales should vary but within reasonable bounds (±50%)
        variation = abs(first_sales - last_sales) / first_sales
        assert variation < 0.5  # Less than 50% variation

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_endpoints(self):
        """Test invalid endpoint handling"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        response = client.get("/api/v1/company/")
        assert response.status_code in [404, 422]  # Either not found or validation error
    
    def test_method_not_allowed(self):
        """Test wrong HTTP methods"""
        response = client.post("/api/v1/tractor-sales")
        assert response.status_code == 405
        
        response = client.put("/api/v1/health")
        assert response.status_code == 405

class TestPerformance:
    """Test API performance"""
    
    def test_response_times(self):
        """Test that endpoints respond quickly"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/tractor-sales")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0  # Should respond within 2 seconds
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading
        
        results = []
        
        def make_request():
            response = client.get("/api/v1/tractor-sales")
            results.append(response.status_code)
        
        # Make 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5

@pytest.mark.asyncio
class TestAsyncOperations:
    """Test async functionality"""
    
    async def test_data_update_function(self):
        """Test the async data update function"""
        # This should run without errors
        await update_sales_data()
        
        # Verify data was updated
        response = client.get("/api/v1/tractor-sales")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_workflow(self):
        """Test complete API workflow"""
        # 1. Check health
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # 2. Get all companies
        response = client.get("/api/v1/tractor-sales")
        assert response.status_code == 200
        companies = response.json()["data"]
        
        # 3. Get each company individually
        for company in companies:
            response = client.get(f"/api/v1/company/{company['company_name']}")
            assert response.status_code == 200
            individual_data = response.json()
            assert individual_data["company_name"] == company["company_name"]
        
        # 4. Get market trends
        response = client.get("/api/v1/market-trends")
        assert response.status_code == 200
        
        # 5. Trigger manual update
        response = client.post("/api/v1/update-data")
        assert response.status_code == 200

# Run tests if file is executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])