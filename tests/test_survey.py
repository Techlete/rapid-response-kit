from mock import call, ANY
from rapid_response_kit.app import app
from tests.base import KitTestCase


class SurveyTestCase(KitTestCase):

    def setUp(self):
        app.config['FIREBASE_URL'] = 'ApplicationID'
        app.config['FIREBASE_SECRET'] = 'REST API key'
        self.app = app.test_client()
        self.start_patch('survey')

    def tearDown(self):
        self.stop_patch()

    def test_post_sms(self):
        self.app.post('/survey', data=
          {
            'twilio_number': '1415TWILIO',
            'numbers': '14158675309',
            'question': 'Will you take part in a quick survey?'
          })

        self.patchio.incoming_phone_numbers.update.assert_called_with(
            '1415TWILIO',
            unique_name='[RRKit] Survey',
            sms_url=ANY,
            sms_method=ANY,
        )

        self.patchio.messages.create.assert_called_with(
            '+14158675309',
            body='Will you take part in a quick survey? Reply YES / NO',
            from_='1415TWILIO'
        )

    def test_post_sms_multi(self):
        self.app.post('/survey', data=
          {
            'twilio_number': '1415TWILIO',
            'numbers': '14158675309\n14158675310',
            'question': 'Are you reporting yourself as safe?'
          })

        self.patchio.messages.create.has_calls([
            call(
                '+14158675309',
                body='Are you reporting yourself as safe? Reply YES / NO',
                from_='1415TWILIO'
            ),
            call(
                '+14158675310',
                body='Are you reporting yourself as safe? Reply YES / NO',
                from_='1415TWILIO'
            ),
        ])
