from rapid_response_kit.app import app
from tests.base import KitTestCase


class ConferenceLineTestCase(KitTestCase):

    def setUp(self):
        self.app = app.test_client()
        self.start_patch('conference_line')

    def tearDown(self):
        self.stop_patch()

    def test_get(self):
        response = self.app.get('/conference-line')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.app.post('/conference-line', data={'whitelist': '14158675309\n14158675310',
                                                'room': '1234',
                                                'twilio_number': 'PNSid'})

        expected_fallback_url = 'http://twimlets.com/echo?Twiml=%3CResponse%3E%3CSay%3ESorry+the+service+is+down+for+maintenance%3C%2FSay%3E%3C%2FResponse%3E'
        expected_voice_url = 'http://localhost/conference-line/handle?whitelist=%2B14158675309&whitelist=%2B14158675310&room=1234'

        self.patchio.incoming_phone_numbers.update.assert_called_with(
            'PNSid',
            fallback_voice_url=expected_fallback_url,
            unique_name='[RRKit] Conference Line',
            voice_method='GET',
            fallback_voice_method='GET',
            voice_url=expected_voice_url)

    def test_handle_not_in_whitelist(self):
        response = self.app.get('/conference-line/handle?whitelist=%2B14158675309&whitelist=%2B14158675310&room=1234&From=%2B14155551234')
        self.assertIn("Sorry, you are not authorized to call this number", response.data.decode('utf8'))

    def test_handle_fully_qualifed(self):
        response = self.app.get('/conference-line/handle?whitelist=%2B14158675309&whitelist=%2B14158675310&room=1234&From=%2B14158675309')
        self.assertIn("<Conference>1234</Conference>", response.data.decode('utf8'))

    def test_handle_partially_qualified(self):
        response = self.app.get('/conference-line/handle?whitelist=%2B14158675309&whitelist=%2B14158675310&From=%2B14158675309')
        self.assertIn("<Gather action=\"/conference-line/connect\" method=\"GET\" numDigits=\"3\">", response.data.decode('utf8'))

    def test_connect(self):
        response = self.app.get('/conference-line/connect?Digits=1234')
        self.assertIn("<Conference>1234</Conference>", response.data.decode('utf8'))
