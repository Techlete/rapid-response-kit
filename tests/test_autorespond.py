from rapid_response_kit.app import app
from tests.base import KitTestCase


class AutorespondTestCase(KitTestCase):

    def setUp(self):
        self.app = app.test_client()
        self.start_patch('autorespond')

    def tearDown(self):
        self.stop_patch()

    def test_get(self):
        response = self.app.get('/auto-respond')
        self.assertEqual(response.status_code, 200)

    def test_post_invalid(self):
        response = self.app.post('/auto-respond', data={},
                                 follow_redirects=True)
        self.assertIn("Please provide a message", response.data.decode('utf8'))

    def test_post_valid_sms(self):
        self.app.post('/auto-respond', data={'sms-message': 'Test Message',
                                             'twilio_number': 'PNSid'})

        expected_url = 'http://twimlets.com/echo?Twiml=%3C%3Fxml+version%3D%221.0%22+encoding%3D%22UTF-8%22%3F%3E%3CResponse%3E%3CMessage%3ETest+Message%3C%2FMessage%3E%3C%2FResponse%3E'

        self.patchio.incoming_phone_numbers.update.assert_called_with(
            'PNSid',
            unique_name='[RRKit] Auto-Respond',
            voice_url='',
            voice_method='GET',
            sms_url=expected_url,
            sms_method='GET')

    def test_post_valid_mms(self):
        self.app.post('/auto-respond',
            data={
            'sms-message': 'test',
            'twilio_number': 'PNSid',
            'media': 'https://i.imgur.com/vhRYT3O.jpg'
        })

        expected_url = 'http://twimlets.com/echo?Twiml=%3C%3Fxml+version%3D%221.0%22+encoding%3D%22UTF-8%22%3F%3E%3CResponse%3E%3CMessage%3Etest%3CMedia%3Ehttps%3A%2F%2Fi.imgur.com%2FvhRYT3O.jpg%3C%2FMedia%3E%3C%2FMessage%3E%3C%2FResponse%3E'

        self.patchio.incoming_phone_numbers.update.assert_called_with(
            'PNSid',
            unique_name='[RRKit] Auto-Respond',
            voice_url='',
            voice_method='GET',
            sms_method='GET',
            sms_url=expected_url)

    def test_post_valid_voice(self):
        self.app.post('/auto-respond', data={'voice-message': 'Test Message',
                                             'twilio_number': 'PNSid'})

        expected_url = 'http://twimlets.com/echo?Twiml=%3CResponse%3E%3CSay%3ETest+Message%3C%2FSay%3E%3C%2FResponse%3E'

        self.patchio.incoming_phone_numbers.update.assert_called_with(
            'PNSid',
            unique_name='[RRKit] Auto-Respond',
            voice_url=expected_url,
            voice_method='GET',
            sms_method='GET',
            sms_url='')



