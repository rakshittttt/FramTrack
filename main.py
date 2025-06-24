
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Sample data for top 5 tractor companies based on sales
TRACTOR_COMPANIES = [
    {
        "id": 1,
        "name": "John Deere",
        "sales_rank": 1,
        "annual_sales": 45000,
        "price_range": "$35,000 - $150,000",
        "popular_models": ["5075E", "6120M", "8R Series"],
        "avg_rating": 4.5,
        "total_reviews": 1250
    },
    {
        "id": 2,
        "name": "Mahindra",
        "sales_rank": 2,
        "annual_sales": 38000,
        "price_range": "$25,000 - $80,000",
        "popular_models": ["2638 HST", "4540 4WD", "6075 Power+"],
        "avg_rating": 4.3,
        "total_reviews": 890
    },
    {
        "id": 3,
        "name": "New Holland",
        "sales_rank": 3,
        "annual_sales": 32000,
        "price_range": "$30,000 - $120,000",
        "popular_models": ["T4.75", "T6.180", "T7.315"],
        "avg_rating": 4.2,
        "total_reviews": 720
    },
    {
        "id": 4,
        "name": "Kubota",
        "sales_rank": 4,
        "annual_sales": 28000,
        "price_range": "$20,000 - $90,000",
        "popular_models": ["M7-172", "L3901", "BX2380"],
        "avg_rating": 4.4,
        "total_reviews": 650
    },
    {
        "id": 5,
        "name": "Case IH",
        "sales_rank": 5,
        "annual_sales": 25000,
        "price_range": "$40,000 - $180,000",
        "popular_models": ["Farmall 75A", "Maxxum 145", "Magnum 340"],
        "avg_rating": 4.1,
        "total_reviews": 580
    }
]

# Sample farmer reviews
FARMER_REVIEWS = [
    {
        "company_id": 1,
        "farmer_name": "Rajesh Kumar",
        "location": "Punjab",
        "model": "John Deere 5075E",
        "rating": 5,
        "review": "Excellent fuel efficiency and reliability. Perfect for my 25-acre farm.",
        "verified_purchase": True
    },
    {
        "company_id": 2,
        "farmer_name": "Suresh Patel",
        "location": "Gujarat",
        "model": "Mahindra 4540 4WD",
        "rating": 4,
        "review": "Good value for money. Strong performance in heavy soil conditions.",
        "verified_purchase": True
    },
    {
        "company_id": 1,
        "farmer_name": "Ravi Singh",
        "location": "Haryana",
        "model": "John Deere 6120M",
        "rating": 5,
        "review": "Outstanding build quality and after-sales service. Highly recommended!",
        "verified_purchase": True
    },
    {
        "company_id": 3,
        "farmer_name": "Mohan Reddy",
        "location": "Andhra Pradesh",
        "model": "New Holland T4.75",
        "rating": 4,
        "review": "Smooth operation and comfortable cabin. Good for long working hours.",
        "verified_purchase": True
    },
    {
        "company_id": 4,
        "farmer_name": "Anil Sharma",
        "location": "Rajasthan",
        "model": "Kubota L3901",
        "rating": 4,
        "review": "Compact yet powerful. Perfect for small to medium farms.",
        "verified_purchase": True
    }
]

@app.route('/')
def home():
    return render_template('index.html', companies=TRACTOR_COMPANIES)

@app.route('/company/<int:company_id>')
def company_details(company_id):
    company = next((c for c in TRACTOR_COMPANIES if c['id'] == company_id), None)
    if not company:
        return "Company not found", 404
    
    # Get reviews for this company
    company_reviews = [r for r in FARMER_REVIEWS if r['company_id'] == company_id]
    
    return render_template('company_details.html', company=company, reviews=company_reviews)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = []
    
    if query:
        # Search in company names and models
        for company in TRACTOR_COMPANIES:
            if query in company['name'].lower():
                results.append(company)
            else:
                # Check if query matches any model
                for model in company['popular_models']:
                    if query in model.lower():
                        results.append(company)
                        break
    
    return render_template('search_results.html', results=results, query=query)

@app.route('/api/companies')
def api_companies():
    return jsonify(TRACTOR_COMPANIES)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
