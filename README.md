# TrainWise - Sports Activities Recommender

TrainWise is a web application that helps users discover, track, and manage sports activities based on their preferences, location, and current weather conditions.

## Features

- User authentication and profile management
- Activity search with location and weather-based filtering
- Favorite activities management
- Workout history tracking
- Real-time weather information
- Distance-based activity recommendations

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Setup Instructions

1. **Clone the Repository** (if using Git)
   ```bash
   git clone [repository-url]
   cd SC2006 28-3-2025
   ```

2. **Set Up Virtual Environment**
   ```powershell
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```powershell
   pip install django django-allauth django-crispy-forms crispy-bootstrap5
   ```

4. **Navigate to Project Directory**
   ```powershell
   cd sports_recommender
   ```

5. **Apply Database Migrations**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run the Development Server**
   ```powershell
   python manage.py runserver
   ```

7. **Access the Application**
   - Open your web browser
   - Navigate to http://127.0.0.1:8000/
   - The application should now be running

## Troubleshooting

Common issues and solutions:

1. **Python Command Not Found**
   - Ensure Python is installed correctly
   - Add Python to your system's PATH environment variable
   - Try using `python3` instead of `python`

2. **Permission Errors**
   - Run PowerShell as administrator
   - Check file and directory permissions

3. **Package Installation Failures**
   - Verify internet connection
   - Update pip: `python -m pip install --upgrade pip`
   - Try installing packages individually

4. **Port Already in Use**
   - Stop other applications using port 8000
   - Use a different port: `python manage.py runserver 8080`

## Project Structure

```
sports_recommender/
├── activities/          # Activities app
├── sports_recommender/  # Main project directory
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
├── data/              # Data files for activities and weather
│   ├── Cleaned_Activities_Data.csv  # Sports facilities data
│   └── 24hourWeatherForecast.json  # Weather forecast data
├── manage.py           # Django management script
└── requirements.txt    # Project dependencies
```

### Data Files

The `data/` directory contains essential data files for the application:

1. `Cleaned_Activities_Data.csv` - Sports facilities and activities information:
   - Facility names
   - Activity types
   - Location information (latitude, longitude)
   - Indoor/outdoor status
   - Available activities
   - Intensity levels

2. `24hourWeatherForecast.json` - Weather forecast data:
   - Temperature
   - Weather conditions
   - Air quality
   - Updated every 24 hours

These files are used to populate the database and provide real-time weather information for activity recommendations.

## Features Usage

1. **User Authentication**
   - Sign up for a new account
   - Log in with existing credentials
   - Reset password if forgotten
   - Manage email preferences

2. **Activity Search**
   - Search for activities based on location
   - Filter by current weather conditions
   - View activity details

3. **Favorites Management**
   - Save activities to favorites
   - Remove activities from favorites
   - View all favorite activities

4. **Workout History**
   - Add completed activities to history
   - View workout history
   - Track progress over time

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any queries or support, please contact the development team. 