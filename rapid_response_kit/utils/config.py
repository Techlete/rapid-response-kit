try:
   import local_config
except:
    try:
      import os
      SECRET_KEY = os.getenv('SECRET_KEY')
      TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
      TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
      GOOGLE_ACCOUNT_USER = os.getenv('GOOGLE_ACCOUNT_USER')
      GOOGLE_ACCOUNT_PASS = os.getenv('GOOGLE_ACCOUNT_PASS')
      PUSHER_APP_ID = os.getenv('PUSHER_APP_ID')
      PUSHER_KEY = os.getenv('PUSHER_KEY')
      PUSHER_SECRET = os.getenv('PUSHER_SECRET')
      PUSHER_CLUSTER = os.getenv('PUSHER_CLUSTER')
      FIREBASE_URL = os.getenv('FIREBASE_URL')
      FIREBASE_SECRET = os.getenv('FIREBASE_SECRET')
    except:
        pass
