import requests
from datetime import datetime
import pytz

class WeatherService:
    BASE_URL = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"
    
    @staticmethod
    def get_weather_forecast(date=None):
        """
        Get 24-hour weather forecast from the API
        Args:
            date: Optional date in YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss format
        Returns:
            Dictionary containing weather forecast data
        """
        params = {}
        if date:
            params['date'] = date
            
        try:
            response = requests.get(WeatherService.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    @staticmethod
    def get_current_weather():
        """
        Get current weather conditions
        Returns:
            Dictionary containing current weather information
        """
        # Get current time in Singapore timezone
        sgt = pytz.timezone('Asia/Singapore')
        current_time = datetime.now(sgt)
        
        # Format current time for API
        date_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Get weather forecast
        forecast_data = WeatherService.get_weather_forecast(date_str)
        
        if not forecast_data or 'data' not in forecast_data:
            return None
            
        # Find the current period in the forecast
        current_period = None
        for period in forecast_data['data']['records'][0]['periods']:
            period_start = datetime.fromisoformat(period['timePeriod']['start'].replace('Z', '+00:00'))
            period_end = datetime.fromisoformat(period['timePeriod']['end'].replace('Z', '+00:00'))
            
            if period_start <= current_time <= period_end:
                current_period = period
                break
        
        if not current_period:
            return None
            
        # Get weather for central region (can be modified based on location)
        weather_info = {
            'forecast': current_period['regions']['central']['text'],
            'temperature': forecast_data['data']['records'][0]['general']['temperature'],
            'relative_humidity': forecast_data['data']['records'][0]['general']['relativeHumidity'],
            'wind': forecast_data['data']['records'][0]['general']['wind']
        }
        
        return weather_info
    
    @staticmethod
    def map_weather_to_condition(forecast_text):
        """
        Map weather forecast text to our weather condition choices
        """
        weather_mapping = {
            'Fair': 'sunny',
            'Fair (Day)': 'sunny',
            'Fair (Night)': 'sunny',
            'Fair and Warm': 'sunny',
            'Partly Cloudy': 'cloudy',
            'Partly Cloudy (Day)': 'cloudy',
            'Partly Cloudy (Night)': 'cloudy',
            'Cloudy': 'cloudy',
            'Light Rain': 'rainy',
            'Moderate Rain': 'rainy',
            'Heavy Rain': 'rainy',
            'Passing Showers': 'rainy',
            'Light Showers': 'rainy',
            'Showers': 'rainy',
            'Heavy Showers': 'rainy',
            'Thundery Showers': 'rainy',
            'Heavy Thundery Showers': 'rainy',
            'Heavy Thundery Showers with Gusty Winds': 'rainy',
            'Hazy': 'cloudy',
            'Slightly Hazy': 'cloudy',
            'Windy': 'cloudy',
            'Mist': 'cloudy',
            'Fog': 'cloudy'
        }
        
        return weather_mapping.get(forecast_text, 'cloudy')  # Default to cloudy if no match 