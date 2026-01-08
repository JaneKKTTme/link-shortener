from app import create_app
import os
from typing import NoReturn

app = create_app()

def main() -> NoReturn:
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug)

if __name__ == '__main__':
    main() 
