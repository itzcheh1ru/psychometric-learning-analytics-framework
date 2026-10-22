"""
wsgi.py – WSGI entry point for production deployments (e.g. gunicorn wsgi:app).

Psychometric Learning Analytics Framework (J26-DS-310)
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
