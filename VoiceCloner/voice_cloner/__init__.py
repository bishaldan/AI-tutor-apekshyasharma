from flask import Flask
from voice_cloner.routes import main
import os
from flask_cors import CORS  

def create_app():
    # Create Flask app with correct template and static folders
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )

    # Enable CORS for all routes (adjust origins as needed)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        expose_headers=["Content-Type", "Range"],
        supports_credentials=False
    )

    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)  # for generated audio

    # Register blueprint
    app.register_blueprint(main)

    return app