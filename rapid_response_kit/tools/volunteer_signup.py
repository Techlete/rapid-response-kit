# -*- coding: future_fstrings -*-
import base64
import os
import re

from flask import render_template, request, flash, redirect
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from rapid_response_kit.utils.clients import twilio, get_google_creds
from rapid_response_kit.utils.helpers import (
    parse_numbers,
    echo_twimlet,
    twilio_numbers,
    check_is_valid_url
)
from twilio.twiml.messaging_response import MessagingResponse


def non_empty_list(candidate):
    return candidate and len(candidate) > 0


def non_empty_list_of_lists(candidate):
    return non_empty_list(candidate) and non_empty_list(candidate[0])


def get_creds_env(credentials_obj=None, scopes=None):
    if not credentials_obj:
        try:
            data = os.getenv('GOOGLE_API_SERVICES_JSON')
            credentials_obj = json.loads(data)
        except json.decoder.JSONDecodeError:
            print("Could not read JSON")
            exit(-2)

    if not scopes:
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    try:
        return ServiceAccountCredentials._from_parsed_json_keyfile(credentials_obj, scopes)
    except ValueError:
        print("Error: Unable to parse credentials object")
        exit(-1)


def authorize(creds):
    try:
        return gspread.authorize(creds)
    except gspread.exceptions.GSpreadException:
        print("Error: Unable to Authorize with google")
        exit(-2)


def open_by_title(title, client):
    try:
        return client.open(title)
    except gspread.SpreadsheetNotFound:
        return client.create(title)


def open_sheet(spreadsheet, title, init_rows=None):
    if not non_empty_list_of_lists(init_rows):
        init_rows = [["Title"]]

    try:
        return spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(
            title,
            len(init_rows),
            max(len(row) for row in init_rows))
        for row in init_rows:
            sheet.insert_row(row)
        return sheet


def install(app):
    google_client = authorize(get_creds_env())
    spreadsheet = open_by_title("RapidResponseKit", google_client)

    active_sheet = open_sheet(spreadsheet, "VolunteerSignup", [['name', 'phone', 'response']])

    app.config.apps.register(
        'volunteer-signup',
        'Volunteer Signup',
        '/volunteer-signup'
    )

    phone_number = ''

    @app.route('/volunteer-signup', methods=['GET'])
    def show_volunteer_signup():
        numbers = twilio_numbers()
        return render_template("volunteer-signup.html", numbers=numbers)

    @app.route('/volunteer-signup', methods=['POST'])
    def do_volunteer_signup():

        # Update phone number url for replys
        url = "{}/handle?{}".format(request.base_url, request.query_string.decode('utf8'))
        twiml = '<Response><Say>System is down for maintenance</Say></Response>'
        fallback_url = echo_twimlet(twiml)

        try:
            client = twilio()
            client.incoming_phone_numbers.update(
                request.form['twilio_number'],
                unique_name='[RRKit] Volunteer Signup',
                sms_url=url,
                sms_method='POST',
                sms_fallback_url=fallback_url,
                sms_fallback_method='GET'
            )

        except Exception as e:
            print(e)
            flash('Error configuring phone number', 'danger')

        client = twilio()
        # Since the value of the form is a PN sid need to fetch the number

        numbers = parse_numbers(request.form['numbers'])
        for number in numbers:
            try:
                client.messages.create(
                    number,
                    body=request.form['message'],
                    from_=request.form['twilio_number'],
                    media_url=check_is_valid_url(request.form.get('media', ''))
                )
                flash(f"Sent {number} the message.", 'success')
            except Exception:
                flash(f"Failed to send to {number}", 'danger')

        return redirect('/volunteer-signup')

    @app.route('/volunteer-signup/handle', methods=['POST'])
    def add_volunteer():

        def insert_row():
            row = [f"{f_name} {l_name}", from_number, response.upper()]
            active_sheet.append_row(row)

        response = MessagingResponse()
        from_number = request.values.get('From')
        body = request.values.get('Body')

        client = twilio()

        text_body = ""
        try:
            (f_name, l_name, response) = body.strip().split(' ')
            insert_row()
            text_body = "Thanks!  Your response has been recorded."
        except ValueError:
            text_body = "Please enter a valid format."
        except Exception:
            text_body = '''There was a problem recording your response.
            Please try again.'''

        client.messages.create(
            from_number,
            body=text_body,
            from_=phone_number
        )

        return str(response)
