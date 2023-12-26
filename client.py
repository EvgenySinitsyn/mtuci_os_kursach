import socket

from PyQt5 import QtCore, QtGui, QtWidgets


class UiClient:
    def __init__(self):

        self.HOST = 'localhost'
        self.PORTS = {1: 12347, 2: 12346}

        self.centralwidget = QtWidgets.QWidget(client)
        self.btn_choose_server1 = QtWidgets.QPushButton(self.centralwidget)
        self.btn_choose_server2 = QtWidgets.QPushButton(self.centralwidget)
        self.btn_get_info = QtWidgets.QPushButton(self.centralwidget)
        self.btn_move = QtWidgets.QPushButton(self.centralwidget)
        self.btn_proc_priority = QtWidgets.QPushButton(self.centralwidget)
        self.btn_check_sqm = QtWidgets.QPushButton(self.centralwidget)
        self.lbl_output = QtWidgets.QLabel(self.centralwidget)
        self.x_label = QtWidgets.QLabel(self.centralwidget)
        self.y_label = QtWidgets.QLabel(self.centralwidget)
        self.x_input = QtWidgets.QLineEdit(self.centralwidget)
        self.y_input = QtWidgets.QLineEdit(self.centralwidget)

    def setup_widget(self, object_name, rect, font, label=None, style_sheet=None):
        widget = getattr(self, object_name)
        widget.setGeometry(QtCore.QRect(*rect))
        widget.setFont(font)
        if label:
            widget.setText(label)
        widget.setObjectName(object_name)
        if style_sheet:
            widget.setStyleSheet(style_sheet)

    def setup_ui(self, client):
        client.setObjectName("Client")
        client.resize(1300, 500)
        client.setUnifiedTitleAndToolBarOnMac(False)

        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setFixedSize(1300, 575)

        font = QtGui.QFont()
        font.setPointSize(25)

        font_commands = QtGui.QFont()
        font_commands.setPointSize(14)

        font_label = QtGui.QFont()
        font_label.setPointSize(16)

        self.setup_widget("btn_choose_server1", (20, 70, 500, 100), font, "Подключиться к серверу 1",
                          "background-color: white")

        self.setup_widget("btn_choose_server2", (20, 200, 500, 100), font, "Подключиться к серверу 2",
                          "background-color: white")

        self.setup_widget("btn_get_info", (600, 70, 300, 100), font_commands, "Инфо", "background-color: white")

        self.setup_widget("btn_move", (920, 70, 200, 100), font_commands, "Передвинуть", "background-color: white")

        self.setup_widget('x_label', (1130, 70, 30, 40), font_commands, 'x:')
        self.setup_widget('y_label', (1130, 130, 30, 40), font_commands, 'y:')

        self.setup_widget('x_input', (1160, 70, 60, 40), font_commands)
        self.setup_widget('y_input', (1160, 130, 60, 40), font_commands)

        self.setup_widget("btn_proc_priority", (600, 200, 300, 100), font_commands, "Приоритет процесса",
                          "background-color: white")

        self.setup_widget("btn_check_sqm", (920, 200, 300, 100), font_commands, "Проверить сбор данных SQM",
                          "background-color: white")

        self.setup_widget("lbl_output", (20, 350, 1200, 100), font_label)

        self.add_functions()

    def add_functions(self):
        self.btn_choose_server1.clicked.connect(lambda: self.connect_server(1))
        self.btn_choose_server2.clicked.connect(lambda: self.connect_server(2))
        self.btn_get_info.clicked.connect(lambda: self.send_command('info'))
        self.btn_move.clicked.connect(lambda: self.send_command('move'))
        self.btn_proc_priority.clicked.connect(lambda: self.send_command('priority'))
        self.btn_check_sqm.clicked.connect(lambda: self.send_command('sqm'))

    def connect_server(self, server):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.HOST, self.PORTS[server]))
            self.lbl_output.setText(
                f'Успешно подключились к серверу {server}... Для получения справки введите help. Для выхода введите exit.')
            getattr(self, f'btn_choose_server{server}').setStyleSheet('background-color: green')
            getattr(self, f'btn_choose_server{1 if server == 2 else 2}').setStyleSheet('background-color: white')
        except Exception as ex:
            self.lbl_output.setText(f'Не удалось подключиться к серверу {server}')

    def send_command(self, command):
        if command == 'exit':
            exit(0)

        if command == 'move':
            command += ' ' + self.x_input.text() + ' ' + self.y_input.text()
        self.client_socket.sendall(command.encode())
        data = self.client_socket.recv(1024)
        self.lbl_output.setText(data.decode())


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    client = QtWidgets.QMainWindow()
    client.setWindowTitle('Курсовая работа по Операционным системам: Клиент')
    icon = QtGui.QIcon('icon.png')
    client.setWindowIcon(icon)
    ui = UiClient()
    ui.setup_ui(client)
    client.show()
    sys.exit(app.exec_())
