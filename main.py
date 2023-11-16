from flask import Flask, render_template, request
from flask_socketio import SocketIO
import socket
import json
from datetime import datetime
import os
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Set the path for static files (CSS, images)
app._static_folder = 'static'

# Define the path to the data.json file
data_file_path = 'storage/data.json'

# Check if the storage directory and data.json file exist, create them if not
if not os.path.exists('storage'):
    os.makedirs('storage')
if not os.path.exists(data_file_path):
    with open(data_file_path, 'w') as f:
        json.dump({}, f)

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        user_message = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Send data to the socket server
        message_data = {"username": username, "message": user_message}
        socketio.emit('new_message', message_data)

        # Save data to data.json file
        with open(data_file_path, 'r') as f:
            data = json.load(f)
        data[timestamp] = message_data
        with open(data_file_path, 'w') as f:
            json.dump(data, f)

    return render_template('message.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

# Socket server functionality
@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == '__main__':
    def run_flask():
        socketio.run(app, port=3000, debug=True, use_reloader=False)

    def run_socket_server():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(('127.0.0.1', 5000))
            while True:
                data, addr = server_socket.recvfrom(1024)
                print(f'Received data from {addr}: {data.decode()}')

    flask_thread = Thread(target=run_flask)
    socket_thread = Thread(target=run_socket_server)

    flask_thread.start()
    socket_thread.start()

    flask_thread.join()
    socket_thread.join()
