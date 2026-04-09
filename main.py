"""Application entry point for running the Flask development server."""

from app import create_app
import os
from typing import NoReturn


__author__ = 'JaneKKTTme'
__license__ = 'MIT'
__version__ = '1.0.0'


app = create_app()
"""Flask application instance created by the application factory."""

def main() -> NoReturn:
    """Start the Flask development server.
    
    Reads DEBUG environment variable to determine if debug mode should be enabled.
    Debug mode is enabled when DEBUG=true (case-insensitive).
    
    Environment Variables:
        DEBUG: Set to 'true' to enable debug mode (default: 'False')
        
    Example:
        >>> # Run with debug mode enabled
        >>> export DEBUG=true
        >>> python run.py
        
        >>> # Run in production mode
        >>> python run.py
    """
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug)

if __name__ == '__main__':
    main() 
