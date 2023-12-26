import win32gui
import threading
import os
import socket
from datetime import datetime
import win32pipe, win32file


PIPE_NAME = r'\\.\pipe\test_pipe'
HOST = 'localhost'
PORT = 12347


def send_log(log_msg):
    try:
        file_handle = win32file.CreateFile(PIPE_NAME,
                                       win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                       win32file.FILE_SHARE_WRITE, None,
                                       win32file.OPEN_EXISTING, 0, None)
        win32file.WriteFile(file_handle, log_msg.encode())
        win32file.CloseHandle(file_handle)
    except Exception as ex:
        print(ex)


def get_window_id():
    windows = []

    def callback(hwnd, _):
        if "server1" in win32gui.GetWindowText(hwnd):
            windows.append(hwnd)

    win32gui.EnumWindows(callback, None)
    return windows


def move_window(x, y):
    window_id = get_window_id()[0]
    win32gui.MoveWindow(window_id, x, y, 1000, 700, True)


def server1_info():
    computer_name = os.environ['COMPUTERNAME']
    user_name = os.environ['USERNAME']
    return f"Сервер 1 - Имя компьютера: {computer_name}, Имя пользователя: {user_name}"


def handle_request(client_socket, address):
    while True:
        reply = 'Нет такой команды'
        data = client_socket.recv(1024)
        if not data:
            break
        command = data.decode()

        if 'move' in command:
            try:
                command_list = command.split()
                x = int(command_list[1])
                y = int(command_list[2])
                move_window(x, y)
                reply = f'Окно перемещено по координатам x: {x}, y: {y}.'
            except Exception as ex:
                reply = 'Допущена ошибка в команде.'

        if 'info' in command:
            reply = server1_info()

        if 'help' in command:
            reply = 'Команды сервера:\n\nmove x y: переместить окно сервера по координатам x y;\n' \
                    'info: получить информацию о компьютере и пользователе;\n' \
                    'help: помощь.\n\n'
        now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        reply = now + '\n' + reply

        log_msg = f'SERVER 1\nCLIENT: {address}\nREQUEST: {command}\nRESPONSE: {reply}\n\n'
        send_log(log_msg)
        client_socket.sendall(reply.encode())

    client_socket.close()
    log_msg = 'SERVER 1\nCLIENT: {address}\nОтключился\n\n'
    send_log(log_msg)


def start_server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        log_msg = 'SERVER 1\nСервер запущен и ожидает подключений...\n\n'
        send_log(log_msg)
        print(log_msg)
    except Exception as ex:
        log_msg = f'SERVER 1\nНе удалось запустить сервер: {ex}\n\n'
        send_log(log_msg)
        print(log_msg)
        exit(0)

    while True:
        client_sock, address = server_socket.accept()
        log_msg = f"SERVER 1\nПринято соединение от {address[0]}:{address[1]}\n\n"
        send_log(log_msg)
        print(log_msg)

        request_handler = threading.Thread(target=handle_request, args=(client_sock, address))
        request_handler.start()


if __name__ == '__main__':
    start_server()
