# -*- coding: future_fstrings -*-
from rapid_response_kit.utils.clients import twilio
from flask import render_template, request, redirect, flash
from rapid_response_kit.utils.helpers import (
    echo_twimlet,
    twilio_numbers,
    check_is_valid_url
)
from twilio.twiml.messaging_response import MessagingResponse


def install(app):
    app.config.apps.register('autorespond', 'Auto Respond', '/auto-respond')

    @app.route('/auto-respond', methods=['GET'])
    def show_auto_respond():
        numbers = twilio_numbers()
        return render_template("auto-respond.html", numbers=numbers)

    @app.route('/auto-respond', methods=['POST'])
    def do_auto_respond():
        sms_message = request.form.get('sms-message', '')
        voice_message = request.form.get('voice-message', '')

        if len(sms_message) == 0 and len(voice_message) == 0:
            flash('Please provide a message', 'danger')
            return redirect('/auto-respond')

        sms_url = ''
        voice_url = ''

        if len(sms_message) > 0:
            r = MessagingResponse()
            mms_media = check_is_valid_url(request.form.get('media', ''))
            if mms_media:
                r.message(sms_message).media(mms_media)
            else:
                r.message(sms_message)
            sms_url = echo_twimlet(r.to_xml())

        if len(voice_message) > 0:
            twiml = f"<Response><Say>{voice_message}</Say></Response>"
            voice_url = echo_twimlet(twiml)

        try:
            client = twilio()
            client.incoming_phone_numbers.update(
                request.form['twilio_number'],
                unique_name='[RRKit] Auto-Respond',
                voice_url=voice_url,
                voice_method='GET',
                sms_url=sms_url,
                sms_method='GET')

            flash('Auto-Respond has been configured', 'success')
        except Exception:
            flash('Error configuring number', 'danger')

        return redirect('/auto-respond')
