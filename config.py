import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Automatically locks onto your project directory folder
base_dir = os.path.dirname(os.path.abspath(__file__))

# Safely joins the path without using tricky backslashes
cert_path = os.path.join(base_dir, "lulu-7cb00-firebase-adminsdk-fbsvc-aadcfcc9f0.json")

# Initializing firebase
cred = credentials.Certificate(cert_path) 
firebase_admin.initialize_app(cred)

# Initializing firestore database
db = firestore.client()