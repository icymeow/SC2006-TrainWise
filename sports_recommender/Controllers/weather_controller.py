import requests
from datetime import datetime
import pytz
from django.conf import settings
from typing import Optional, Dict, Any
from django.core.cache import cache
import logging

# Set up logging
logger = logging.getLogger(__name__)

class WeatherController:
    """Controller for handling weather-related operations"""
    
    BASE_URL = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"
    CACHE_KEY_PREFIX = "weather_data_"
    CACHE_TIMEOUT = 1800  # 30 minutes cache

    @staticmethod
    def get_current_weather(latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
        """
        Get current weather conditions for a specific location
        
        Args:
            latitude (float, optional): Location latitude
            longitude (float, optional): Location longitude
            
        Returns:
            dict: Weather information including forecast, temperature, humidity, and wind
                  Returns None if there's an error
        """
        try:
            # Try to get cached data first
            cache_key = f"{WeatherController.CACHE_KEY_PREFIX}{latitude}_{longitude}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            # Get current time in Singapore timezone
            sgt = pytz.timezone('Asia/Singapore')
            current_time = datetime.now(sgt)
            date_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")

            # Make API request
            params = {'date': date_str}
            if latitude and longitude:
                params.update({'lat': latitude, 'lng': longitude})

            response = requests.get(
                WeatherController.BASE_URL,
                params=params,
                timeout=10  # 10 seconds timeout
            )
            response.raise_for_status()
            forecast_data = response.json()

            if not forecast_data or 'data' not in forecast_data:
                logger.error("Invalid response format from weather API")
                return None

            # Process the forecast data
            weather_info = WeatherController._process_forecast_data(forecast_data, current_time)
            
            if weather_info:
                # Cache the result
                cache.set(cache_key, weather_info, WeatherController.CACHE_TIMEOUT)
            
            return weather_info

        except requests.Timeout:
            logger.error("Timeout while fetching weather data")
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_current_weather: {str(e)}")
            return None

    @staticmethod
    def _process_forecast_data(forecast_data: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
        """
        Process the raw forecast data into a structured format
        
        Args:
            forecast_data (dict): Raw forecast data from API
            current_time (datetime): Current time in SGT
            
        Returns:
            dict: Processed weather information
        """
        try:
            records = forecast_data['data']['records'][0]
            
            # Find the current period in the forecast
            current_period = None
            for period in records['periods']:
                period_start = datetime.fromisoformat(period['timePeriod']['start'].replace('Z', '+00:00'))
                period_end = datetime.fromisoformat(period['timePeriod']['end'].replace('Z', '+00:00'))
                
                if period_start <= current_time <= period_end:
                    current_period = period
                    break

            if not current_period:
                logger.warning("No matching time period found in forecast data")
                return None

            # Get weather for central region (default)
            weather_info = {
                'forecast': current_period['regions']['central']['text'],
                'temperature': {
                    'low': records['general']['temperature']['low'],
                    'high': records['general']['temperature']['high']
                },
                'relative_humidity': {
                    'low': records['general']['relativeHumidity']['low'],
                    'high': records['general']['relativeHumidity']['high']
                },
                'wind': {
                    'speed': records['general']['wind']['speed'],
                    'direction': records['general']['wind']['direction']
                },
                'condition': WeatherController.map_weather_to_condition(
                    current_period['regions']['central']['text']
                )
            }

            return weather_info

        except KeyError as e:
            logger.error(f"Missing key in forecast data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing forecast data: {str(e)}")
            return None

    @staticmethod
    def map_weather_to_condition(forecast_text: str) -> str:
        """
        Map weather forecast text to standardized condition
        
        Args:
            forecast_text (str): Weather forecast text from API
            
        Returns:
            str: Standardized weather condition
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

    @staticmethod
    def is_outdoor_weather_suitable(weather_info: Dict[str, Any]) -> bool:
        """
        Determine if weather is suitable for outdoor activities
        
        Args:
            weather_info (dict): Weather information from get_current_weather
            
        Returns:
            bool: True if weather is suitable for outdoor activities
        """
        if not weather_info:
            return False

        try:
            # Check if it's raining
            if weather_info['condition'] == 'rainy':
                return False

            # Check temperature (if too hot)
            if weather_info['temperature']['high'] > 35:  # Above 35°C
                return False

            # Check humidity (if too high)
            if weather_info['relative_humidity']['high'] > 90:  # Above 90%
                return False

            return True

        except KeyError as e:
            logger.error(f"Missing key in weather info for suitability check: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error checking weather suitability: {str(e)}")
            return False 