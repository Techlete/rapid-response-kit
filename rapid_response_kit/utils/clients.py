from flask import current_app as app
from twilio.rest import Client
from pusher import Pusher


def twilio():
    return Client(
        app.config['TWILIO_ACCOUNT_SID'],
        app.config['TWILIO_AUTH_TOKEN'])


def pusher_connect(config=None):
    if config is None:
        config = app.config

    pusher_key = config.get('PUSHER_KEY', None)
    pusher_secret = config.get('PUSHER_SECRET', None)
    pusher_app_id = config.get('PUSHER_APP_ID', None)
    pusher_cluster = config.get('PUSHER_CLUSTER', None)

    try:
        Pusher(
            app_id=pusher_app_id,
            key=pusher_key,
            secret=pusher_secret,
            cluster=pusher_cluster,
            ssl=True)
        return True
    except:
        return False


def get_google_creds(config=None):
    if config is None:
        config = app.config

    user = config.get('GOOGLE_ACCOUNT_USER', None)
    password = config.get('GOOGLE_ACCOUNT_PASS', None)
    return user, password
