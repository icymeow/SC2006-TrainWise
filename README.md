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
- Email notifications for workout reminders
- Responsive design for mobile and desktop
- Location-based weather updates

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL (for production)
- Git (optional, for version control)

## Setup Instructions

1. **Clone the Repository**
```bash
git clone <repository-url>
cd SC2006-TrainWise
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
pip install -r requirements.txt
```

Current dependencies include:
- Django 5.0.2+
- django-allauth 0.57.0+
- django-crispy-forms 2.1+
- crispy-bootstrap5 0.7+
- python-dotenv 1.0.0+
- requests 2.31.0+
- Pillow 10.0.0+
- django-environ 0.11.2+
- pytz 2024.1+
- psycopg2-binary 2.9.9+
- django-cors-headers 4.3.1+
- whitenoise 6.6.0+
- gunicorn 21.2.0+
- django-debug-toolbar 4.3.0+

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
WEATHER_API_KEY=your-weather-api-key
DATABASE_URL=your-database-url  # For PostgreSQL in production
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
SC2006-TrainWise/
├── sports_recommender/
│   ├── activities/      # Sports activities and workout history
│   ├── users/          # User management and authentication
│   ├── services/       # External services (weather, etc.)
│   ├── controllers/    # Business logic
│   └── database/       # Database models and operations
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/            # User-uploaded files
└── manage.py         # Django management script
```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use meaningful variable and function names
   - Add docstrings for functions and classes
   - Keep functions small and focused

2. **Testing**
   - Write unit tests for new features
   - Run tests before committing: `python manage.py test`
   - Ensure test coverage for critical paths

3. **Version Control**
   - Create feature branches from `main`
   - Write clear commit messages
   - Review code before merging

## Deployment

1. **Production Setup**
   - Set DEBUG=False in settings
   - Configure PostgreSQL database
   - Set up static files with whitenoise
   - Configure gunicorn for production server

2. **Environment Variables**
   - Ensure all sensitive data is in environment variables
   - Use different settings for development and production

3. **Security Checklist**
   - Enable CSRF protection
   - Set secure SSL/HTTPS settings
   - Configure allowed hosts
   - Set up proper CORS headers

## Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database URL format
   - Ensure database user has proper permissions

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT and STATIC_URL settings
   - Verify whitenoise configuration

3. **Email Configuration**
   - Verify SMTP settings
   - Check email credentials
   - Test email backend configuration

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