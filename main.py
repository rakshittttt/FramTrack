
from flask import Flask, render_template, request, jsonify, session
import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict

try:
    from services.tractorguru_client import TractorGuruClient
    tg_client = TractorGuruClient()
except Exception:
    tg_client = None

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-sessions'

# Language translations
LANGUAGES = {
    'en': {
        'title': 'FarmTech Tractor Reviews',
        'tagline': 'Top 5 Tractor Companies Based on Sales Performance',
        'description': 'Discover the best tractor brands trusted by thousands of farmers. Rankings based on last year\'s sales data and farmer reviews.',
        'search_placeholder': 'Search tractors, companies...',
        'search_btn': 'Search',
        'why_top_5': 'Why These Top 5?',
        'highest_sales': 'Highest Sales',
        'best_value': 'Best Value', 
        'farmer_verified': 'Farmer Verified',
        'reliable_service': 'Reliable Service',
        'annual_sales': 'Annual Sales',
        'price_range': 'Price Range',
        'rating': 'Rating',
        'popular_models': 'Popular Models',
        'view_reviews': 'View Reviews & Details',
        'back_to_companies': 'Back to Top Companies',
        'sales_performance': 'Sales Performance',
        'market_position': 'Market Position',
        'pricing': 'Pricing',
        'customer_satisfaction': 'Customer Satisfaction',
        'farmer_reviews': 'Farmer Reviews',
        'verified_purchase': 'Verified Purchase',
        'model': 'Model',
        'no_reviews': 'No reviews available yet. Be the first to review!'
    },
    'hi': {
        'title': 'फार्मटेक ट्रैक्टर समीक्षा',
        'tagline': 'बिक्री प्रदर्शन के आधार पर शीर्ष 5 ट्रैक्टर कंपनियां',
        'description': 'हजारों किसानों द्वारा भरोसा किए गए सर्वोत्तम ट्रैक्टर ब्रांड खोजें। पिछले साल के बिक्री डेटा और किसान समीक्षाओं के आधार पर रैंकिंग।',
        'search_placeholder': 'ट्रैक्टर, कंपनियां खोजें...',
        'search_btn': 'खोजें',
        'why_top_5': 'ये शीर्ष 5 क्यों?',
        'highest_sales': 'उच्चतम बिक्री',
        'best_value': 'सर्वोत्तम मूल्य',
        'farmer_verified': 'किसान सत्यापित',
        'reliable_service': 'विश्वसनीय सेवा',
        'annual_sales': 'वार्षिक बिक्री',
        'price_range': 'मूल्य सीमा',
        'rating': 'रेटिंग',
        'popular_models': 'लोकप्रिय मॉडल',
        'view_reviews': 'समीक्षा और विवरण देखें',
        'back_to_companies': 'शीर्ष कंपनियों पर वापस जाएं',
        'sales_performance': 'बिक्री प्रदर्शन',
        'market_position': 'बाजार स्थिति',
        'pricing': 'मूल्य निर्धारण',
        'customer_satisfaction': 'ग्राहक संतुष्टि',
        'farmer_reviews': 'किसान समीक्षा',
        'verified_purchase': 'सत्यापित खरीद',
        'model': 'मॉडल',
        'no_reviews': 'अभी तक कोई समीक्षा उपलब्ध नहीं है। पहले समीक्षा करें!'
    },
    'pa': {
        'title': 'ਫਾਰਮਟੈਕ ਟਰੈਕਟਰ ਸਮੀਖਿਆਵਾਂ',
        'tagline': 'ਵਿਕਰੀ ਪ੍ਰਦਰਸ਼ਨ ਦੇ ਆਧਾਰ ਤੇ ਸਿਖਰਲੀਆਂ 5 ਟਰੈਕਟਰ ਕੰਪਨੀਆਂ',
        'description': 'ਹਜ਼ਾਰਾਂ ਕਿਸਾਨਾਂ ਦੁਆਰਾ ਭਰੋਸਾ ਕੀਤੇ ਗਏ ਸਭ ਤੋਂ ਵਧੀਆ ਟਰੈਕਟਰ ਬ੍ਰਾਂਡਾਂ ਦੀ ਖੋਜ ਕਰੋ। ਪਿਛਲੇ ਸਾਲ ਦੇ ਵਿਕਰੀ ਡੇਟਾ ਅਤੇ ਕਿਸਾਨ ਸਮੀਖਿਆਵਾਂ ਦੇ ਆਧਾਰ ਤੇ ਰੈਂਕਿੰਗ।',
        'search_placeholder': 'ਟਰੈਕਟਰ, ਕੰਪਨੀਆਂ ਖੋਜੋ...',
        'search_btn': 'ਖੋਜੋ',
        'why_top_5': 'ਇਹ ਸਿਖਰਲੇ 5 ਕਿਉਂ?',
        'highest_sales': 'ਸਭ ਤੋਂ ਵੱਧ ਵਿਕਰੀ',
        'best_value': 'ਸਭ ਤੋਂ ਵਧੀਆ ਮੁੱਲ',
        'farmer_verified': 'ਕਿਸਾਨ ਸਤਿਆਪਿਤ',
        'reliable_service': 'ਭਰੋਸੇਮੰਦ ਸੇਵਾ',
        'annual_sales': 'ਸਲਾਨਾ ਵਿਕਰੀ',
        'price_range': 'ਕੀਮਤ ਸੀਮਾ',
        'rating': 'ਰੇਟਿੰਗ',
        'popular_models': 'ਪ੍ਰਸਿੱਧ ਮਾਡਲ',
        'view_reviews': 'ਸਮੀਖਿਆਵਾਂ ਅਤੇ ਵੇਰਵੇ ਦੇਖੋ',
        'back_to_companies': 'ਸਿਖਰਲੀਆਂ ਕੰਪਨੀਆਂ ਤੇ ਵਾਪਸ ਜਾਓ',
        'sales_performance': 'ਵਿਕਰੀ ਪ੍ਰਦਰਸ਼ਨ',
        'market_position': 'ਬਾਜ਼ਾਰ ਸਥਿਤੀ',
        'pricing': 'ਕੀਮਤ ਨਿਰਧਾਰਨ',
        'customer_satisfaction': 'ਗ੍ਰਾਹਕ ਸੰਤੁਸ਼ਟੀ',
        'farmer_reviews': 'ਕਿਸਾਨ ਸਮੀਖਿਆਵਾਂ',
        'verified_purchase': 'ਸਤਿਆਪਿਤ ਖਰੀਦ',
        'model': 'ਮਾਡਲ',
        'no_reviews': 'ਅਜੇ ਤੱਕ ਕੋਈ ਸਮੀਖਿਆ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਪਹਿਲੇ ਸਮੀਖਿਆ ਕਰੋ!'
    }
}

def get_current_language():
    return session.get('language', 'en')

def get_text(key):
    lang = get_current_language()
    return LANGUAGES[lang].get(key, LANGUAGES['en'][key])

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
        "total_reviews": 1250,
        "financing_available": True,
        "emi_starting": 2800,
        "fuel_efficiency": "12-15 L/hr",
        "warranty_years": 4,
        "service_centers": 450,
        "availability_status": "In Stock",
        "delivery_time": "2-3 weeks"
    },
    {
        "id": 2,
        "name": "Mahindra",
        "sales_rank": 2,
        "annual_sales": 38000,
        "price_range": "$25,000 - $80,000",
        "popular_models": ["2638 HST", "4540 4WD", "6075 Power+"],
        "avg_rating": 4.3,
        "total_reviews": 890,
        "financing_available": True,
        "emi_starting": 2200,
        "fuel_efficiency": "10-13 L/hr",
        "warranty_years": 3,
        "service_centers": 380,
        "availability_status": "Limited Stock",
        "delivery_time": "3-4 weeks"
    },
    {
        "id": 3,
        "name": "New Holland",
        "sales_rank": 3,
        "annual_sales": 32000,
        "price_range": "$30,000 - $120,000",
        "popular_models": ["T4.75", "T6.180", "T7.315"],
        "avg_rating": 4.2,
        "total_reviews": 720,
        "financing_available": True,
        "emi_starting": 2500,
        "fuel_efficiency": "11-14 L/hr",
        "warranty_years": 3,
        "service_centers": 320,
        "availability_status": "In Stock",
        "delivery_time": "2-3 weeks"
    },
    {
        "id": 4,
        "name": "Kubota",
        "sales_rank": 4,
        "annual_sales": 28000,
        "price_range": "$20,000 - $90,000",
        "popular_models": ["M7-172", "L3901", "BX2380"],
        "avg_rating": 4.4,
        "total_reviews": 650,
        "financing_available": True,
        "emi_starting": 1800,
        "fuel_efficiency": "9-12 L/hr",
        "warranty_years": 5,
        "service_centers": 280,
        "availability_status": "Pre-Order",
        "delivery_time": "6-8 weeks"
    },
    {
        "id": 5,
        "name": "Case IH",
        "sales_rank": 5,
        "annual_sales": 25000,
        "price_range": "$40,000 - $180,000",
        "popular_models": ["Farmall 75A", "Maxxum 145", "Magnum 340"],
        "avg_rating": 4.1,
        "total_reviews": 580,
        "financing_available": True,
        "emi_starting": 3200,
        "fuel_efficiency": "13-16 L/hr",
        "warranty_years": 4,
        "service_centers": 250,
        "availability_status": "In Stock",
        "delivery_time": "3-4 weeks"
    }
]

# AI Recommendation system data
CROP_TRACTOR_MAP = {
    'wheat': [1, 2, 3],  # John Deere, Mahindra, New Holland
    'rice': [2, 4, 1],   # Mahindra, Kubota, John Deere
    'cotton': [1, 5, 3], # John Deere, Case IH, New Holland
    'sugarcane': [5, 1, 2], # Case IH, John Deere, Mahindra
    'vegetables': [4, 2, 3], # Kubota, Mahindra, New Holland
    'fruits': [4, 3, 1]  # Kubota, New Holland, John Deere
}

# Weather alerts data
WEATHER_ALERTS = [
    {
        "region": "Punjab",
        "alert": "Heavy rainfall expected. Check hydraulic systems and engine protection.",
        "severity": "High",
        "date": datetime.now().strftime("%Y-%m-%d")
    },
    {
        "region": "Gujarat", 
        "alert": "Dust storm warning. Clean air filters and check engine oil.",
        "severity": "Medium",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    },
    {
        "region": "Haryana",
        "alert": "High temperature forecast. Monitor coolant levels.",
        "severity": "Medium", 
        "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    }
]

# Community forum data
FORUM_POSTS = [
    {
        "id": 1,
        "title": "Best tractor for wheat farming in Punjab?",
        "author": "Farmer_Singh",
        "replies": 12,
        "last_activity": "2 hours ago",
        "category": "General Discussion"
    },
    {
        "id": 2,
        "title": "Maintenance tips for monsoon season",
        "author": "Expert_Mechanic",
        "replies": 8,
        "last_activity": "5 hours ago",
        "category": "Maintenance"
    },
    {
        "id": 3,
        "title": "Financing options comparison",
        "author": "Budget_Farmer",
        "replies": 15,
        "last_activity": "1 day ago",
        "category": "Finance"
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

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in LANGUAGES:
        session['language'] = lang
    return request.referrer or '/'

@app.route('/')
def home():
    return render_template('index.html', companies=TRACTOR_COMPANIES, get_text=get_text, current_lang=get_current_language())

@app.route('/company/<int:company_id>')
def company_details(company_id):
    company = next((c for c in TRACTOR_COMPANIES if c['id'] == company_id), None)
    if not company:
        return "Company not found", 404
    
    # Get reviews for this company
    company_reviews = [r for r in FARMER_REVIEWS if r['company_id'] == company_id]
    
    return render_template('company_details.html', company=company, reviews=company_reviews, get_text=get_text, current_lang=get_current_language())

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
    
    return render_template('search_results.html', results=results, query=query, get_text=get_text, current_lang=get_current_language())

@app.route('/ai-recommendations')
def ai_recommendations():
    return render_template('ai_recommendations.html', get_text=get_text, current_lang=get_current_language())

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    farm_size = float(data.get('farm_size', 10))
    crop_type = data.get('crop_type', 'wheat').lower()
    budget = float(data.get('budget', 50000))
    
    # AI recommendation logic
    recommended_ids = CROP_TRACTOR_MAP.get(crop_type, [1, 2, 3])
    recommendations = []
    
    for company_id in recommended_ids[:3]:  # Top 3 recommendations
        company = next((c for c in TRACTOR_COMPANIES if c['id'] == company_id), None)
        if company:
            # Calculate match score based on multiple factors
            score = random.randint(85, 98)  # Simulated AI score
            recommendation = {
                **company,
                'match_score': score,
                'reason': f"Perfect for {crop_type} farming on {farm_size} acres"
            }
            recommendations.append(recommendation)
    
    return jsonify(recommendations)

@app.route('/finance-calculator')
def finance_calculator():
    return render_template('finance_calculator.html', companies=TRACTOR_COMPANIES, get_text=get_text, current_lang=get_current_language())

@app.route('/weather-alerts')
def weather_alerts():
    return render_template('weather_alerts.html', alerts=WEATHER_ALERTS, get_text=get_text, current_lang=get_current_language())

@app.route('/community-forum')
def community_forum():
    return render_template('community_forum.html', posts=FORUM_POSTS, get_text=get_text, current_lang=get_current_language())

@app.route('/availability-tracker')
def availability_tracker():
    return render_template('availability_tracker.html', companies=TRACTOR_COMPANIES, get_text=get_text, current_lang=get_current_language())

@app.route('/analytics-dashboard')
def analytics_dashboard():
    # Generate sample analytics data
    analytics_data = {
        'total_tractors_sold': sum(c['annual_sales'] for c in TRACTOR_COMPANIES),
        'avg_price': 75000,
        'most_popular_brand': 'John Deere',
        'monthly_sales': [3200, 3800, 4100, 3900, 4500, 5200],
        'regional_preferences': {
            'Punjab': 'John Deere',
            'Gujarat': 'Mahindra', 
            'Haryana': 'New Holland',
            'UP': 'Kubota',
            'Rajasthan': 'Case IH'
        }
    }
    return render_template('analytics_dashboard.html', analytics=analytics_data, get_text=get_text, current_lang=get_current_language())

@app.route('/api/companies')
def api_companies():
    return jsonify(TRACTOR_COMPANIES)

# ========== TractorGuru integration (scraped public pages) ==========
@app.route('/api/tractorguru/brands')
def api_tg_brands():
    if not tg_client:
        return jsonify({"error": "TractorGuru client unavailable"}), 503
    try:
        brands = tg_client.get_brands()
        return jsonify(brands)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route('/api/tractorguru/brand_models')
def api_tg_brand_models():
    if not tg_client:
        return jsonify({"error": "TractorGuru client unavailable"}), 503
    brand_path = request.args.get('path', '')
    if not brand_path:
        return jsonify({"error": "Missing required query param: path"}), 400
    try:
        models = tg_client.get_brand_models(brand_path)
        return jsonify(models)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route('/api/tractorguru/model_details')
def api_tg_model_details():
    if not tg_client:
        return jsonify({"error": "TractorGuru client unavailable"}), 503
    model_path = request.args.get('path', '')
    if not model_path:
        return jsonify({"error": "Missing required query param: path"}), 400
    try:
        details = tg_client.get_model_details(model_path)
        return jsonify(details)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
