import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

def run_tests():
    # Set up Django environment
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sports_recommender.settings'
    django.setup()

    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Run tests
    failures = test_runner.run_tests([
        'users.tests.test_auth',
        'activities.tests.test_activities',
        'activities.tests.test_recommendations',
        'activities.tests.test_weather',
        'activities.tests.test_history',
        'activities.tests.test_location'
    ])

    # Return appropriate exit code
    sys.exit(bool(failures))

if __name__ == '__main__':
    run_tests() 