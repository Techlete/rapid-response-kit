from rapid_response_kit.app import app
from mock import ANY
from tests.base import KitTestCase


class RingdownTestCase(KitTestCase):

    def setUp(self):
        self.app = app.test_client()
        self.start_patch('ringdown')

    def tearDown(self):
        self.stop_patch()

    def test_get(self):
        response = self.app.get('/ringdown')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.app.post('/ringdown', data={'numbers': '4158675309\n4158675310',
                                         'twilio_number': 'PNSid'})

        expected_voice_url = 'http://localhost/ringdown/handle?stack=%2B14158675309&stack=%2B14158675310&sorry='
        expected_fallback_url = 'http://twimlets.com/echo?Twiml=%3C%3Fxml+version%3D%221.0%22+encoding%3D%22UTF-8%22%3F%3E%3CResponse%3E%3CSay%3ESystem+is+down+for+maintenance%3C%2FSay%3E%3C%2FResponse%3E'

        self.patchio.incoming_phone_numbers.update.assert_called_with(
            'PNSid',
            unique_name='[RRKit] Ringdown',
            voice_url=ANY,
            voice_method='GET',
            voice_fallback_url=ANY,
            voice_fallback_method='GET')

    def test_handle_remaining_stack(self):
        response = self.app.get('/ringdown/handle?stack=%2B14158675309')
        self.assertIn("<Dial", response.data.decode('utf8'))
        self.assertIn("+14158675309", response.data.decode('utf8'))

    def test_handle_exhausted_stack(self):
        response = self.app.get('/ringdown/handle')
        self.assertIn("Sorry, no one answered", response.data.decode('utf8'))

    def test_handle_exhausted_stack_custom(self):
        response = self.app.get('/ringdown/handle?sorry=Custom+Message')
        self.assertIn("Custom Message", response.data.decode('utf8'))
