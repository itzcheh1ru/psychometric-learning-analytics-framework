"""
app.py – Application entry point for the
Psychometric Learning Analytics Framework (J26-DS-310).

Run locally with:
    python app.py
Or with Flask CLI:
    flask --app app run --debug
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
