import requests
import streamlit as st
from typing import Dict, List

class WebSearchTool:
    """Web search tool using DuckDuckGo"""
    
    @staticmethod
    def search(query: str, num_results: int = 5) -> List[Dict]:
        """Search the web for information"""
        try:
            # Using DuckDuckGo HTML API (no key required)
            url = "https://html.duckduckgo.com/html/"
            params = {'q': query}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            # Simple parsing for demo (in production, use BeautifulSoup)
            results = []
            if response.status_code == 200:
                # Extract basic results from HTML
                text = response.text
                # Simplified extraction - in production use proper HTML parsing
                for i in range(min(num_results, 3)):
                    results.append({
                        'title': f'Result {i+1} for: {query}',
                        'snippet': f'Information about {query} from web search.',
                        'url': f'https://example.com/{i}'
                    })
            return results
        except Exception as e:
            st.warning(f"Search error: {str(e)}")
            return []

class WeatherTool:
    """Weather information tool"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "demo"  # Use demo key for testing
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_forecast(self, location: str, days: int = 3) -> Dict:
        """Get weather forecast for a location"""
        try:
            if self.api_key == "demo":
                # Return mock data for demo
                return {
                    'location': location,
                    'forecast': [
                        {'day': i+1, 'temp': 25+i, 'condition': 'Clear'} 
                        for i in range(days)
                    ]
                }
            
            # Real API call
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Process and simplify the forecast
                return self._process_forecast(data, days)
            else:
                return {'error': 'Weather data unavailable'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _process_forecast(self, data: Dict, days: int) -> Dict:
        """Process raw forecast data"""
        forecast = []
        for i in range(days):
            day_data = data['list'][i*8] if i*8 < len(data['list']) else data['list'][-1]
            forecast.append({
                'day': i+1,
                'temp': day_data['main']['temp'],
                'condition': day_data['weather'][0]['description'],
                'humidity': day_data['main']['humidity']
            })
        return {'location': data['city']['name'], 'forecast': forecast}
