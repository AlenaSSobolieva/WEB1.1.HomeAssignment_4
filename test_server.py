import unittest
import eventlet
from main import app, socketio

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.socketio_client = socketio.test_client(app)

    def tearDown(self):
        self.socketio_client.disconnect()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Python can be easy to pick up', response.data)

    def test_message_post(self):
        response = self.app.post('/message', data=dict(username='test_user', message='test_message'))
        self.assertEqual(response.status_code, 200)


    def test_socket_connection(self):
        received_event = eventlet.Event()

        @socketio.on('connect')
        def on_connect():
            received_event.send(True)

        self.socketio_client.emit('connect')  # Manually emit the connect event

        # Wait for the event or timeout after 10 seconds
        with eventlet.Timeout(10):
            received_event.wait()

        # Check if the event was received
        self.assertTrue(received_event.ready())

if __name__ == '__main__':
    unittest.main()









