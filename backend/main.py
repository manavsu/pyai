    
from waitress import serve
from flask_api import app

if __name__ == "__main__":
    print("Serving on http://localhost:80/")
    serve(app, host='0.0.0.0', port=80)


