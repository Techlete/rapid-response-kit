# -*- coding: future_fstrings -*-
from rapid_response_kit.utils.clients import twilio, pusher_connect
from rapid_response_kit.utils.helpers import (
    parse_numbers,
    echo_twimlet,
    twilio_numbers,
    check_is_valid_url
)

from twilio.twiml.messaging_response import MessagingResponse
from pusher import Pusher
from flask import render_template, request, flash, redirect


def install(app):
    if pusher_connect(app.config):
        app.config.apps.register('noticeboard', 'Noticeboard', '/noticeboard')
    else:
        print('''
        Noticeboard requires Pusher credentials.
        Please add PUSHER_APP_ID, PUSHER_KEY and PUSHER_SECRET
        to rapid_response_kit/utils/config.py''')
        exit(-2)

    @app.route('/noticeboard', methods=['GET'])
    def show_noticeboard():
        numbers = twilio_numbers()
        client = twilio()

        # Build a list of numbers that are being used for Noticeboard
        noticeboard_numbers = []
        for p in client.incoming_phone_numbers.list():
            if '[RRKit] Noticeboard' in p.unique_name:
                noticeboard_numbers.append(p.phone_number)

        return render_template(
            "noticeboard.html",
            url=f'{request.base_url}/live',
            numbers=numbers,
            noticeboards=noticeboard_numbers
        )

    @app.route('/noticeboard', methods=['POST'])
    def do_noticeboard():
        client = twilio()

        url = f"{request.url_root}noticeboard/post"
        client.incoming_phone_numbers.update(request.form['twilio_number'],
                                    sms_url=url,
                                    sms_method='POST',
                                    unique_name='[RRKit] Noticeboard')

        from_number = request.form['twilio_number']
        live_url = f'{request.url_root}noticeboard/live/{from_number}'
        numbers = parse_numbers(request.form['numbers'])
        body = request.form.get('message', '').replace('{URL}', live_url)
        media = check_is_valid_url(request.form.get('media', ''))

        for num in numbers:
            client.messages.create(
                num,
                from_=from_number,
                body=body,
                media_url=media
            )
            flash(f'Sent {num} the message', 'success')


        return redirect('/noticeboard')

    @app.route('/noticeboard/post', methods=['POST'])
    def handle_noticeboard_inbound():

        pusher_key = app.config.get('PUSHER_KEY', None)
        pusher_secret = app.config.get('PUSHER_SECRET', None)
        pusher_app_id = app.config.get('PUSHER_APP_ID', None)

        try:
            p = Pusher(pusher_app_id, pusher_key, pusher_secret)

            p['rrk_noticeboard_live'].trigger(
                'new_message',
                {
                    'image': request.values.get('MediaUrl0', None),
                    'body': request.values.get('Body', None),
                    'from': request.values.get('From', None)
                }
            )
        except:
            return '<Response />'

        to = request.values.get('To', '')
        r = MessagingResponse()
        r.message(
            f'''Thank you, your image has been posted
            to {request.url_root}noticeboard/live/{to}''')
        return r.to_xml()

    @app.route('/noticeboard/live/<number>', methods=['GET'])
    def show_noticeboard_live(number=None):
        pusher_key = app.config.get('PUSHER_KEY', '')
        twilio_client = twilio()
        try:
            cleaned_number = number
        except:
            flash('We did not receive a correct number', 'danger')
            return redirect('/noticeboard')

        # Build a list of messages to our number that has media attached
        msgs = []
        for m in twilio_client.messages.list(cleaned_number):
            if int(m.num_media) > 0:
                msgs.append(m)

        '''
        Super janky because media is seperate from message resources.

        Let's mash the bits we want together and then add them to a list
        - Paul Hallett
        '''
        msg_media_list = []
        for m in msgs:
            d = {}
            d['image_url'] = twilio_client.media(m.sid).list()[0].uri
            d['body'] = m.body
            d['from'] = m.from_
            msg_media_list.append(d)

        return render_template(
            'noticeboard_live.html',
            pusher_key=pusher_key,
            messages=msg_media_list,
            number=number
        )
