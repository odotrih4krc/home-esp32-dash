import network
import socket
import machine
import time
from machine import Pin
from dht import DHT22

# Wi-Fi credentials
SSID = 'your_SSID'
PASSWORD = 'your_PASSWORD'

# Setup sensors
dht_sensor = DHT22(Pin(22))
motion_sensor = Pin(23, Pin.IN)
relay = Pin(21, Pin.OUT)

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())

# Read temperature and humidity
def read_dht():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity

# HTML for the dashboard
def web_page():
    temperature, humidity = read_dht()
    motion_detected = motion_sensor.value()
    light_status = "ON" if relay.value() == 1 else "OFF"

    html = f"""
    <html>
    <head>
        <title>CAM CAM/title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .card {{ border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin: 10px; }}
            .container {{ display: flex; flex-wrap: wrap; }}
            .card {{ flex: 1; min-width: 200px; }}
            .btn {{ padding: 10px 15px; background-color: #007BFF; color: white; border: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>CAM CAM DASH</h1>
        <div class="container">
            <div class="card">
                <h2>Temperature</h2>
                <p>{temperature} °C</p>
            </div>
            <div class="card">
                <h2>Humidity</h2>
                <p>{humidity} %</p>
            </div>
            <div class="card">
                <h2>Motion Detection</h2>
                <p>{'Detected' if motion_detected else 'Not Detected'}</p>
            </div>
            <div class="card">
                <h2>Light Control</h2>
                <p>Status: {light_status}</p>
                <button class="btn" onclick="toggle_light()">Toggle Light</button>
            </div>
        </div>
        <script>
            function toggle_light() {{
                fetch('/toggle_light');
                location.reload();
            }}
        </script>
    </body>
    </html>
    """
    return html

# Start the web server
def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        if '/toggle_light' in request:
            relay.value(not relay.value())
        response = web_page()
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

# Main function
def main():
    connect_wifi()
    start_server()

if __name__ == '__main__':
    main()