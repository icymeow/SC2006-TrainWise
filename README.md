# TrainWise - Sports Activities Recommender

A Django-based web application that recommends sports activities based on user preferences, weather conditions, and location.

## 🚀 Quick Start for Testing

1. **Clone the Repository**
```bash
git clone https://github.com/icymeow/SC2006-TrainWise.git
cd SC2006-TrainWise
```

2. **Set Up Python Environment**
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix/MacOS

# Install dependencies
pip install -r requirements.txt
```

3. **Initialize the Database**
```bash
cd sports_recommender
python manage.py migrate
python manage.py loaddata activities/fixtures/initial_data.json
```

4. **Create a Superuser (Optional)**
```bash
python manage.py createsuperuser
```

5. **Run the Development Server**
```bash
python manage.py runserver
```

6. **Access the Application**
- Open your web browser
- Go to http://127.0.0.1:8000/
- Register a new account using your email
- Start exploring activities and getting recommendations!

Note: Email verification is required for registration. You will receive a verification email to activate your account.

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
- Caching system for improved performance
- Weather service integration

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL (for production) or SQLite (for development)
- Git
- Redis (optional, for caching)

## Setup Instructions

1. **Clone the Repository**
```bash
git clone https://github.com/icymeow/SC2006-TrainWise.git
cd SC2006-TrainWise
```

2. **Set Up Virtual Environment**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Unix or MacOS:
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Database Setup**

For Development (SQLite):
```bash
cd sports_recommender
python manage.py migrate
python manage.py loaddata activities/fixtures/initial_data.json
```

For Production (PostgreSQL):
```bash
# Install PostgreSQL and create database
createdb trainwise_db

# Set DATABASE_URL in .env
DATABASE_URL=postgres://user:password@localhost:5432/trainwise_db

# Run migrations
python manage.py migrate
python manage.py loaddata activities/fixtures/initial_data.json
```

5. **Environment Configuration**
Create a `.env` file in the project root with the following variables:
```
# Django Settings
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (choose one)
# For SQLite (development):
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL (production):
# DATABASE_URL=postgres://user:password@localhost:5432/trainwise_db

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Authentication
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# Weather API
WEATHER_API_KEY=your-weather-api-key

# Cache Settings (optional)
REDIS_URL=redis://localhost:6379/1
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Run Development Server**
```bash
python manage.py runserver
```

## Project Structure
```
SC2006-TrainWise/
├── sports_recommender/
│   ├── activities/          # Sports activities app
│   │   ├── migrations/     # Database migrations
│   │   ├── fixtures/      # Initial data
│   │   ├── models.py      # Database models
│   │   └── views.py       # View logic
│   ├── Controllers/        # Business logic
│   │   ├── activity_controller.py
│   │   ├── recommendation_controller.py
│   │   ├── user_controller.py
│   │   └── weather_controller.py
│   ├── templates/         # HTML templates
│   ├── static/           # Static files
│   └── sports_recommender/  # Project settings
├── requirements.txt       # Project dependencies
└── README.md            # This file
```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints for better code maintainability
   - Add docstrings for functions and classes
   - Keep functions small and focused

2. **Database Management**
   - Always make migrations after model changes:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```
   - Backup data regularly:
     ```bash
     python manage.py dumpdata > backup.json
     ```
   - Load data when needed:
     ```bash
     python manage.py loaddata backup.json
     ```

3. **Testing**
   - Run tests before committing:
     ```bash
     python manage.py test
     ```
   - Check test coverage:
     ```bash
     coverage run manage.py test
     coverage report
     ```

## Production Deployment

1. **Security Settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

2. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate --no-input
   ```

4. **Gunicorn Setup**
   ```bash
   gunicorn sports_recommender.wsgi:application
   ```

## Troubleshooting

1. **Database Issues**
   - Check database connection settings in .env
   - Verify PostgreSQL is running (for production)
   - Run migrations in order:
     ```bash
     python manage.py migrate auth
     python manage.py migrate
     ```

2. **Static Files Not Loading**
   - Run collectstatic
   - Check STATIC_ROOT and STATIC_URL settings
   - Verify whitenoise configuration

3. **Email Configuration**
   - Verify SMTP settings
   - Test email backend:
     ```python
     python manage.py shell
     from django.core.mail import send_mail
     send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
     ```

4. **Cache Issues**
   - Verify Redis is running (if using Redis)
   - Clear cache if needed:
     ```python
     python manage.py shell
     from django.core.cache import cache
     cache.clear()
     ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support:
1. Check the troubleshooting section
2. Open an issue on GitHub
3. Contact the development team 