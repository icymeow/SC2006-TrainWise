# TrainWise - Sports Activities Recommender

A Django-based web application that recommends sports activities based on user preferences, weather conditions, and location.

## Features

- User registration and authentication (email, Google, Facebook)
- Activity browsing and searching with location-based filtering
- Personalized activity recommendations
- Favorite activities management
- Workout history tracking
- Weather-based activity suggestions
- Real-time distance calculations

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Setup Instructions

1. **Clone the Repository**
```bash
git clone <repository-url>
cd sports_recommender
```

2. **Set Up Virtual Environment**
```powershell
# Create a virtual environment
python -m venv venv

# If you get a PowerShell execution policy error, run these commands as administrator:
# Open PowerShell as administrator and run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Now activate the virtual environment (try one of these commands):
.\venv\Scripts\activate
# OR if the above doesn't work:
& .\venv\Scripts\Activate.ps1
```

3. **Install Dependencies**
```powershell
# Option 1: Install from requirements.txt
pip install -r requirements.txt

# Option 2: Install packages directly
pip install django django-allauth django-crispy-forms crispy-bootstrap5
```

4. **Environment Setup**
Create a `.env` file in the project root with the following variables:
```
DJANGO_SECRET_KEY=your-secret-key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

5. **Database Setup**
```powershell
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

6. **Run the Development Server**
```powershell
python manage.py runserver
```

7. **Access the Application**
- Open your web browser
- Navigate to http://127.0.0.1:8000/
- The application should now be running

## Project Structure

```
sports_recommender/
├── apps/
│   ├── users/           # User management
│   ├── activities/      # Sports activities
│   ├── recommendations/ # Activity recommendations
│   └── workout_history/ # User workout tracking
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/            # User-uploaded files
└── manage.py         # Django management script
```

## Troubleshooting

Common issues and solutions:

1. **Python Command Not Found**
   - Ensure Python is installed correctly
   - Add Python to your system's PATH environment variable
   - Try using `python3` instead of `python`

2. **Permission Errors**
   - Run PowerShell as administrator
   - Check file and directory permissions
   - For virtual environment activation errors:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

3. **Package Installation Failures**
   - Verify internet connection
   - Update pip: `python -m pip install --upgrade pip`
   - Try installing packages individually

4. **Port Already in Use**
   - Stop other applications using port 8000
   - Use a different port: `python manage.py runserver 8080`

## Features Usage

1. **User Authentication**
   - Sign up for a new account (email or social login)
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