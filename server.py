import http.server
import socketserver
import requests
import json
import threading
import time
from requests.auth import HTTPDigestAuth

PORT = 1234

# Lista de módulos a serem monitorados para cada servidor
modulos_servidor1 = ["activemq-rar.rar", "channel-receiver-js.ear", "channel-transmitter-ft.ear", "channel-transmitter-http.ear", "processor-ft.ear", "processor-mq.ear", "wmq.jmsra.rar", "worker.ear"]
modulos_servidor2 = ["channel-receiver-js.ear", "channel-transmitter-ft.ear", "channel-transmitter-http.ear","connector-ft.ear", "processor-ft.ear", "processor-mq.ear", "wmq.jmsra.rar", "worker.ear"]
modulos_servidor3 = ["channel-receiver-js.ear", "channel-transmitter-ft.ear", "channel-transmitter-http.ear","connector-ft.ear", "processor-ft.ear", "processor-mq.ear", "wmq.jmsra.rar", "worker.ear"]

# Configurações de proxy
proxies = {
    "http": None,
    "https": None
}

# Servidor JBoss 1
jboss1_url = 'http://localhost:9990/management'
jboss1_username = 'user'
jboss1_password = 'pass'
statuses1 = {modulo: "Offline" for modulo in modulos_servidor1}

# Servidor JBoss 2
jboss2_url = 'http://address/management'
jboss2_username = 'user'
jboss2_password = 'pass'
statuses2 = {modulo: "Offline" for modulo in modulos_servidor2}

# Servidor JBoss 3 - Novo servidor
jboss3_url = 'http://address/management'
jboss3_username = 'user'
jboss3_password = 'pass'
statuses3 = {modulo: "Offline" for modulo in modulos_servidor3}

HTML_CONTENT = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoramento com Curl</title>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Open Sans', sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            width: 95%;
            max-width: 1200px;
            gap: 20px;
            margin-top: 20px;
        }
        .server {
            flex: 1;
            min-width: 300px;
            max-width: 600px;
            background-color: #ffffff;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 10px;
        }
        .statusItem {
            display: flex;
            align-items: center;
            margin: 5px 0;
            border-bottom: 1px solid #ccc;
            padding: 5px 0;
        }
        .statusName {
            flex: 1;
            font-weight: 600;
            margin-right: 10px;
        }
        .statusBox {
            width: 100px;
            height: 30px;
            line-height: 30px;
            text-align: center;
            font-weight: bold;
            color: white;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .online {
            background-color: #4CAF50;
        }
        .offline {
            background-color: #F44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="server">
            <h1>JBOSS Local</h1>
            <div id="statusContainer1"></div>
        </div>
        <div class="server">
            <h1>JBOSS Hint 1</h1>
            <div id="statusContainer2"></div>
        </div>
        <div class="server">
            <h1>JBOSS Hint 2</h1>
            <div id="statusContainer3"></div>
        </div>
    </div>
    <script>
        async function fetchStatus() {
            try {
                const responses = await Promise.all([
                    fetch('/status1'),
                    fetch('/status2'),
                    fetch('/status3')
                ]);
                const datas = await Promise.all(responses.map(res => res.json()));
                const containers = ['statusContainer1', 'statusContainer2', 'statusContainer3'];
                containers.forEach((containerId, index) => {
                    const statusContainer = document.getElementById(containerId);
                    statusContainer.innerHTML = '';
                    for (const [name, status] of Object.entries(datas[index].statuses)) {
                        const div = document.createElement('div');
                        div.className = 'statusItem';
                        const nameDiv = document.createElement('div');
                        nameDiv.className = 'statusName ' + (status === 'Online' ? 'text-online' : 'text-offline');
                        nameDiv.textContent = name;
                        const statusDiv = document.createElement('div');
                        statusDiv.className = 'statusBox ' + (status === 'Online' ? 'online' : 'offline');
                        statusDiv.textContent = status;
                        div.appendChild(nameDiv);
                        div.appendChild(statusDiv);
                        statusContainer.appendChild(div);
                    }
                });
            } catch (error) {
                console.error('Error fetching status:', error);
            }
        }

        setInterval(fetchStatus, 2000); // Atualiza a cada 2 segundos
        fetchStatus(); // Atualiza na inicialização
    </script>
</body>
</html>
'''

class MonitorHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif self.path == '/status1':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"statuses": statuses1}).encode('utf-8'))
        elif self.path == '/status2':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"statuses": statuses2}).encode('utf-8'))
        elif self.path == '/status3':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"statuses": statuses3}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def monitor_jboss1(url, username, password, statuses, modulos):
    while True:
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "operation": "read-children-resources",
            "child-type": "deployment",
            "include-runtime": True
        }

        try:
            response = requests.post(url, headers=headers, json=data, auth=HTTPDigestAuth(username, password))
            print(f'Response status code from {url}: {response.status_code}')
            response.raise_for_status()
            result = response.json()
            print(f'Response JSON from {url}: {result}')

            if result.get('outcome') == 'success':
                for modulo in modulos:
                    if modulo in result['result']:
                        deployment_status = result['result'][modulo].get('status', 'FAILED')
                        statuses[modulo] = 'Online' if deployment_status != 'FAILED' else 'Offline'
                    else:
                        statuses[modulo] = 'Offline'
            else:
                statuses.update({modulo: 'Offline' for modulo in modulos})
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            statuses.update({modulo: 'Offline' for modulo in modulos})

        time.sleep(2)

def monitor_jboss2(url, username, password, statuses, modulos):
    while True:
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "operation": "read-children-resources",
            "child-type": "deployment",
            "include-runtime": True,
            "address": [
                {"host": "msgp01"},
                {"server": "server"}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data, auth=HTTPDigestAuth(username, password), proxies=proxies)
            print(f'Response status code from {url}: {response.status_code}')
            result = response.json()
            print(f'Response JSON from {url}: {result}')

            if result.get('outcome') == 'success':
                for modulo in modulos:
                    if modulo in result['result']:
                        deployment_status = result['result'][modulo].get('status', 'FAILED')
                        statuses[modulo] = 'Online' if deployment_status != 'FAILED' else 'Offline'
                    else:
                        statuses[modulo] = 'Offline'
            else:
                statuses.update({modulo: 'Offline' for modulo in modulos})
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            statuses.update({modulo: 'Offline' for modulo in modulos})
        time.sleep(2)

def monitor_jboss3(url, username, password, statuses, modulos):
    while True:
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "operation": "read-children-resources",
            "child-type": "deployment",
            "include-runtime": True,
            "address": [
                {"host": "msgp01"},
                {"server": "server"}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data, auth=HTTPDigestAuth(username, password), proxies=proxies)
            print(f'Response status code from {url}: {response.status_code}')
            result = response.json()
            print(f'Response JSON from {url}: {result}')

            if result.get('outcome') == 'success':
                for modulo in modulos:
                    if modulo in result['result']:
                        deployment_status = result['result'][modulo].get('status', 'FAILED')
                        statuses[modulo] = 'Online' if deployment_status != 'FAILED' else 'Offline'
                    else:
                        statuses[modulo] = 'Offline'
            else:
                statuses.update({modulo: 'Offline' for modulo in modulos})
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            statuses.update({modulo: 'Offline' for modulo in modulos})
        time.sleep(2)

Handler = MonitorHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    threading.Thread(target=monitor_jboss1, args=(jboss1_url, jboss1_username, jboss1_password, statuses1, modulos_servidor1), daemon=True).start()
    threading.Thread(target=monitor_jboss2, args=(jboss2_url, jboss2_username, jboss2_password, statuses2, modulos_servidor2), daemon=True).start()
    threading.Thread(target=monitor_jboss3, args=(jboss3_url, jboss3_username, jboss3_password, statuses3, modulos_servidor3), daemon=True).start()

    httpd.serve_forever()
