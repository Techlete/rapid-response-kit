# -*- coding: future_fstrings -*-
import os

print("")
print("")
print(" --- Enter your Twilio information below to complete install --- ")
print("")
print("")

account_sid = input('Twilio Account Sid: ')
auth_token = input('Twilio Auth Token: ')

config = f"""\n\n# Configuration Auto-generated during installation
SECRET_KEY = {repr(os.urandom(20))}
TWILIO_ACCOUNT_SID = '{account_sid}'
TWILIO_AUTH_TOKEN = '{auth_token}'"""

f = open('rapid_response_kit/utils/config.py', 'r')
contents = f.read()
f.close()
f = open('rapid_response_kit/utils/config.py', 'w')
f.write(contents + config)
f.close()

print("")
print("")
print(" --- Would you like to add other credentials now? ---")
print("")
print("")

decision = input("Type 'yes' or 'no': ")

if decision == 'yes':
    firebase_url = input('Firebase Url (optional): ')
    firebase_secret = input('Firebase Secret Key (optional): ')
    pusher_app_id = input('Pusher App ID (optional): ')
    pusher_key = input('Pusher Key (optional): ')
    pusher_secret = input('Pusher Secret (optional): ')
    google_user = input('Google email (optional): ')
    google_pass = input('Google password (optional): ')

    new_config = f'''
GOOGLE_ACCOUNT_USER = '{google_user}'
GOOGLE_ACCOUNT_PASS = '{google_pass}'
PUSHER_APP_ID = '{pusher_app_id}'
PUSHER_KEY = '{pusher_key}'
PUSHER_SECRET = '{pusher_secret}'
FIREBASE_URL = '{firebase_url}'
FIREBASE_SECRET = '{firebase_secret}'
    '''
    f = open('rapid_response_kit/utils/config.py', 'rw')
    contents = f.read()
    f.close()
    f = open('rapid_response_kit/utils/config.py', 'w')
    f.write(contents + new_config)
    f.close()
