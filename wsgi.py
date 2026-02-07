"""
WSGI entry point for production deployment.
This file is used by Gunicorn to start the Flask application.
"""
from main import app

if __name__ == "__main__":
    app.run()