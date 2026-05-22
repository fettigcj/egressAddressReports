"""
WSGI entrypoint for the IP Reports Dashboard.

This file is used by WSGI servers (e.g., Gunicorn, uWSGI, mod_wsgi) to
serve the Flask application in production. It exposes the WSGI callable
named `application` as required by the WSGI spec.
"""
import os
import sys

# Ensure the project root is on the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import the Flask app object as `application`
from app import app as application  # noqa: E402, F401

# Optional: allow running this module directly for local testing
if __name__ == '__main__':
    # In production, a WSGI server imports `application`; this block is not used.
    # For local/adhoc testing, you can run: `python wsgi.py`
    port = int(os.environ.get('PORT', '5000'))
    application.run(host='0.0.0.0', port=port, debug=False)
