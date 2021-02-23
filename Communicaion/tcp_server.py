import socket
import threading
import pprint

bind_ip = '0.0.0.0'
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)

print(f'[*] Listening in {bind_ip}:{bind_port}')

#クライアントからの接続を処理するスレッド
def handle_client(client_socket):
    #クライアントが送信してきたデータを送信
    request = client_socket.recv(1024)

    print(f'[*] Received: {request}')

    #パケットの返送
    client_socket.send(b'ACK!')
    client_socket.close()

while True:
    client, addr = server.accept()
    print(f'[*] Accepted connection from: {addr[0]}:{addr[1]}')
    print(client)
    #データを処理するスレッドの起動
    client_handler = threading.Thread(target=handle_client, args=(client, ))
    client_handler.start()
