import win32process
import winreg
import threading
import socket
from datetime import datetime
import win32pipe, win32file


PIPE_NAME = r'\\.\pipe\test_pipe'
HOST = 'localhost'
PORT = 12346


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


def check_sqm_data_collection():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\SQMClient")
        value, _ = winreg.QueryValueEx(key, "CEIPEnable")
        if value == 1:
            return "Сбор данных для SQM разрешен"
        else:
            return "Сбор данных для SQM запрещен"
    except FileNotFoundError:
        return "Ключ реестра не найден"


def get_process_priority():
    h_process = win32process.GetCurrentProcess()
    priority_class = win32process.GetPriorityClass(h_process)
    return f"Приоритет процесса сервера: {priority_class}"


def handle_request(client_socket, address):
    while True:
        reply = 'Нет такой команды'
        data = client_socket.recv(1024)
        if not data:
            break
        command = data.decode()

        if 'priority' in command:
            reply = get_process_priority()

        if 'sqm' in command:
            reply = check_sqm_data_collection()
        if 'help' in command:
            reply = 'Команды сервера:\n\nsqm: проверить сбор информации Service Quality Manager на сервере;\n' \
                    'priority: узнать приоритет процесса сервера;\n' \
                    'help: помощь.\n\n'
        now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        reply = now + '\n' + reply

        log_msg = f'SERVER 2\nCLIENT: {address}\nREQUEST: {command}\nRESPONSE: {reply}\n\n'
        send_log(log_msg)
        client_socket.sendall(reply.encode())

    client_socket.close()
    log_msg = 'SERVER 2\nCLIENT: {address}\nОтключился\n\n'
    send_log(log_msg)


def start_server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        log_msg = 'SERVER 2\nСервер запущен и ожидает подключений...\n\n'
        send_log(log_msg)
        print(log_msg)
    except Exception as ex:
        log_msg = f'SERVER 2\nНе удалось запустить сервер: {ex}\n\n'
        send_log(log_msg)
        print(log_msg)
        exit(0)

    while True:
        client_sock, address = server_socket.accept()
        log_msg = f"SERVER 2\nПринято соединение от {address[0]}:{address[1]}\n\n"
        send_log(log_msg)
        print(log_msg)

        request_handler = threading.Thread(target=handle_request, args=(client_sock, address))
        request_handler.start()


if __name__ == '__main__':
    start_server()
