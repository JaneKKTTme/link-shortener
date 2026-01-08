from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug)    
