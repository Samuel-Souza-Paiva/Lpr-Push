import sys
import os
import base64
import logging
import threading
import socket
from datetime import datetime

from flask import Flask, request, jsonify
from werkzeug.serving import make_server

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QSplitter, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QObject

# --- Utilitário para obter IP local ---
def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# --- Configuração do Flask ---
flask_app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Sinal para comunicar notificações à GUI
class NotificationSignal(QObject):
    new_notification = Signal(dict)

notif_signal = NotificationSignal()

def save_image(data):
    """Salva a imagem no Desktop/Tollgate_Images e retorna caminho e placa."""
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    folder = os.path.join(desktop, 'Tollgate_Images')
    os.makedirs(folder, exist_ok=True)

    pic = data['Picture']['NormalPic']
    file_name = pic.get('PicName', 'image.jpg')
    image_bytes = base64.b64decode(pic['Content'])
    path = os.path.join(folder, file_name)
    with open(path, 'wb') as f:
        f.write(image_bytes)

    plate_number = data['Picture'].get('Plate', {}).get('PlateNumber', 'Unknown')
    return path, plate_number

@flask_app.route('/NotificationInfo/<action>', methods=['POST'])
def handle_notification(action):
    try:
        if not request.is_json:
            return jsonify({"Result": True}), 200  # Mesmo se inválido

        nd = request.json
        pic = nd.get('Picture', {}).get('NormalPic', {})
        if not pic.get('Content'):
            return jsonify({"Result": True}), 200  # Mesmo sem imagem

        path, plate_number = save_image(nd)
        client_ip = request.remote_addr
        notif_signal.new_notification.emit({
            'file_path': path,
            'plate_number': plate_number,
            'client_ip': client_ip
        })

    except Exception as e:
        logging.error(f"[ERRO] Falha ao processar notificação: {e}", exc_info=True)

    return jsonify({"Result": True}), 200


# --- Servidor Flask em thread ---
class FlaskThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.server = make_server('0.0.0.0', 8080, flask_app)
        self.ctx = flask_app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

# --- Interface PySide6 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Define ícone do aplicativo
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.server_ip = get_server_ip()
        self.setWindowTitle(f"Tollgate Dashboard — {self.server_ip}:8080")
        self.resize(900, 600)
        # Estado de dispositivos conectados
        self.connected_ips = set()
        self.current_msg_box = None
        self._build_ui()
        self._start_flask()

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet("background-color: #000000;")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Cabeçalho
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(
            "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #003610, stop:1 #003611);"
            "margin: 0; padding: 0;"
            # "border-bottom: 1px solid #004d00;"
            # border-style: solid;
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(15, 0, 15, 0)
        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        logo.setPixmap(QPixmap(logo_path).scaledToHeight(40, Qt.SmoothTransformation))
        hl.addWidget(logo)
        title = QLabel("Intelbras LPR PUSH Notification")
        subtitle = QLabel("*Este app está em desenvolvimento e não deve ser usado em produção.*\n"
                        "-->Use com cautela! Qualquer bug contatar: Gustavo Prim Back ou Samuel Vasconcelos.")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(subtitle)
        main_layout.addWidget(header)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Painel esquerdo
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: transparent;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # Exibe IP do servidor
        self.ip_label = QLabel(f"Servidor: http://{self.server_ip}:8080")
        self.ip_label.setStyleSheet("color: white; font-size: 14px; margin-bottom: 10px;")
        left_layout.addWidget(self.ip_label)

        # Indicador de conexão
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 10)
        status_label = QLabel("Dispositivos:")
        status_label.setStyleSheet("color: white; font-size: 14px;")
        status_layout.addWidget(status_label)
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(15, 15)
        self.status_indicator.setStyleSheet("background-color: red; border-radius: 7px;")
        status_layout.addWidget(self.status_indicator)
        self.device_label = QLabel("Nenhum")
        self.device_label.setStyleSheet("color: white; font-size: 14px; margin-left: 10px;")
        status_layout.addWidget(self.device_label)
        status_layout.addStretch()
        left_layout.addLayout(status_layout)

        test_btn = QPushButton("Testar Notificação")
        test_btn.setFixedHeight(40)
        test_btn.setStyleSheet(
            "background-color: #00a651; color: white; border-radius: 5px; font-size: 14px;"
        )
        test_btn.clicked.connect(self.fake_notification)
        left_layout.addWidget(test_btn)
        left_layout.addStretch()
        splitter.addWidget(left_panel)

        # Painel direito
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: transparent;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)

        # Preview de imagem
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(300, 200)
        self.image_preview.setStyleSheet("background-color: #222222; border: 1px solid #444444;")
        self.image_preview.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.image_preview)

        # Tabela de notificações
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Data/Hora", "Placa", "Arquivo"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "alternate-background-color: #121212; background-color: #000000; color: white;"
        )
        right_layout.addWidget(self.table)
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)

        notif_signal.new_notification.connect(self.on_new_notification)

    def _start_flask(self):
        self.flask_thread = FlaskThread()
        self.flask_thread.start()

    def on_new_notification(self, info):
        # Atualiza status de dispositivos
        ip = info.get('client_ip')
        if ip:
            self.connected_ips.add(ip)
            self.status_indicator.setStyleSheet("background-color: green; border-radius: 7px;")
            self.device_label.setText(ip)

        # Atualiza preview de imagem
        pix = QPixmap(info['file_path'])
        if not pix.isNull():
            self.image_preview.setPixmap(
                pix.scaled(self.image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        # Adiciona linha na tabela
        row = self.table.rowCount()
        self.table.insertRow(row)
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.table.setItem(row, 0, QTableWidgetItem(now))
        self.table.setItem(row, 1, QTableWidgetItem(info['plate_number']))
        self.table.setItem(row, 2, QTableWidgetItem(info['file_path']))

        # Fecha pop-up anterior, se existir
        if self.current_msg_box and self.current_msg_box.isVisible():
            self.current_msg_box.close()

        # Pop-up não modal
        box = QMessageBox(self)
        box.setWindowTitle("Nova Notificação")
        box.setText(f"Placa: {info['plate_number']}\nIP: {ip}\n{info['file_path']}")
        box.setStandardButtons(QMessageBox.Ok)
        box.setModal(False)
        box.show()
        self.current_msg_box = box

    def fake_notification(self):
        fake = {
            "Picture": {
                "NormalPic": {
                    "Content": base64.b64encode(b"fakeimage").decode(),
                    "PicName": "teste.jpg"
                },
                "Plate": {"PlateNumber": "ABC1234"}
            }
        }
        # Emula chamado com IP local
        notif_signal.new_notification.emit({
            'file_path': 'teste.jpg',
            'plate_number': 'ABC1234',
            'client_ip': self.server_ip
        })

    def closeEvent(self, ev):
        self.flask_thread.shutdown()
        super().closeEvent(ev)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

