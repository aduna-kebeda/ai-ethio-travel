import os
import logging
import requests
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Load Gemini API key from environment or settings
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or settings.GEMINI_API_KEY
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def get_gemini_recommendations(user_preferences):
    """
    Generate travel recommendations for Ethiopia using Google's Gemini REST API.
    
    Args:
        user_preferences (dict): Dictionary containing 'interests' and 'budget'.
    
    Returns:
        dict: Recommendations or None if generation fails.
    """
    try:
        interests = user_preferences.get('interests', [])
        budget = user_preferences.get('budget', 'mid-range')
        
        logger.info(f"Generating recommendations for preferences: {user_preferences}")
        
        prompt = f"""Generate personalized travel recommendations for Ethiopia, the cradle of humanity, for a user with:
        - Interests: {', '.join(interests)}
        - Budget: {budget}
        
        Ethiopia is a land of ancient history, vibrant cultures, and stunning landscapes. Please include:
        1. Top 3 destination recommendations within Ethiopia, highlighting their unique appeal.
        2. Why these destinations match the user's interests, with specific historical or cultural details.
        3. Budget-friendly tips tailored to Ethiopia (e.g., local transport, affordable dining, bargaining).
        4. Cultural highlights, including traditions, festivals, or experiences (e.g., coffee ceremonies, Timkat).
        5. Recommend activities such as tours, dining options, and local experiences that match the user's preferences.
        
        Make the response engaging, vivid, and practical, capturing Ethiopia's soul—its ancient churches, diverse ethnic groups, and rugged beauty."""
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        logger.info(f"Request to Gemini API: {response.request.body}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"Response from Gemini API: {response_data}")
            
            # Correct parsing: Extract text from 'candidates' -> 'content' -> 'parts'
            candidates = response_data.get('candidates', [])
            if not candidates:
                logger.error("No candidates in API response")
                return None
            recommendations_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
            
            if not recommendations_text:
                logger.error("No text found in API response")
                return None
                
            recommendations = {
                'recommendations': recommendations_text,
                'based_on': {
                    'interests': interests,
                    'budget': budget
                }
            }
            logger.info(f"Generated recommendations: {recommendations}")
            return recommendations
        else:
            logger.error(f"Error fetching recommendations: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return None