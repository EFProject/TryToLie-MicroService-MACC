from flask_restful import Api
import json
from flask import Flask
from firebase_admin import credentials, initialize_app, firestore


app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
     app.run(host='0.0.0.0',port=5001 ,debug=True)
