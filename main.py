
from flask import Flask, render_template, request, jsonify, session
import json

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

@app.route('/api/companies')
def api_companies():
    return jsonify(TRACTOR_COMPANIES)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
