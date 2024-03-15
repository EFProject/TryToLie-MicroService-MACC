from flask_restful import Api
from flask import Flask
from firebase_admin import credentials, initialize_app, firestore
from services.serviceUser import UserAPI, UserImageResource
from services.serviceHome import homeAPI


app = Flask(__name__)
api = Api(app)
# Load the configuration from the config module
app.config.from_object('config')

# Initialize Firebase Admin SDK with credentials from the JSON file
firebaseConfig = credentials.Certificate("firebaseConfig.json")
fireBaseApp = initialize_app(firebaseConfig)

# Initialize Firestore database
db = firestore.client()

api.add_resource(homeAPI, '/')
api.add_resource(UserAPI, '/api/v1/user', '/api/v1/user/<string:id>')
api.add_resource(UserImageResource,'/api/v1/user/image/<string:id>')

if __name__ == "__main__":
     app.run(host='0.0.0.0',port=5001 ,debug=True)
