from firebase_admin import credentials, firestore
import firebase_admin

cred = credentials.Certificate('secrets/socraticos-c19b6-firebase-adminsdk-u2xvd-203d1933ef.json')
firebase_admin.initialize_app(cred)
fireClient = firestore.client()