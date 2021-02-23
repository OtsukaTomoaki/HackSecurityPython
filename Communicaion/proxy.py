import sys
import socket
import threading
import traceback
import pickle
import binascii

def server_loop(local_host, local_port, remote_host, remote_port, recieve_first):
    print(local_host, local_port, remote_host, remote_port)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except:
        print(f'[!!]Failed to listen on {local_host}:{local_port}')
        print('[!!]Check for other listening sockets or correct permissions.')
        print(traceback.print_exc())
        sys.exit(0)

    print(f'[*]Listening on {local_host}:{local_port}')
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        #ローカル側からの接続情報を表示
        print(f'[==>]Received incoming connection from {addr[0]}, {addr[1]}')
        #リモートホストと通信をするためのスレッドを作成し、開始
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, recieve_first))
        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, recieve_first):
    #リモートホストへの接続
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    #必要ならリモートホストからデータを受信
    if recieve_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        #受信データ処理関数にデータを受け渡し
        remote_buffer = response_handler(remote_buffer)

        #もしローカル側に対して送るデータがあれば送信
        if len(remote_buffer):
            print(f'[<==]Sending {len(remote_buffer)} bytes to localhost.')
            client_socket.send(remote_buffer.encode())
    #ローカルからのデータの受信、リモートへの送信、ローカルへの送信の
    #繰り返しを行うループ処理
    while True:
        #ローカルホストからのデータ受信
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print(f'[==>]Received {len(local_buffer)} bytes from localhost.')
            hexdump(local_buffer)
            #送信データ処理関数にデータ受け渡し
            local_buffer = request_handler(local_buffer)

            #リモートホストへのデータ送信
            remote_socket.send(local_buffer)
            print('[==>]Sent to remote.')
        #応答の受信
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f'[<==]Received {len(remote_buffer)} bytes from remote.')
            hexdump(remote_buffer)

            #受信データ処理関数にデータ受け渡し
            remote_buffer = response_handler(remote_buffer)

            #ローカル側に応答データを送信
            client_socket.send(remote_buffer)

            print('[<==]Sent to localhost.')
        #ローカル側、リモート側双方からデータが来なければ接続を閉じる
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print('[*]No more data. Closing connections.')
            break

def hexdump(src, length=16):
    #print(pickle.dumps(src).decode())
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i : i+length]
        #print(s.decode())
        #16進数に変換
        #print('s', s)
        hexa = b' '.join(['%0*X'.encode() % (digits, ord(chr(x))) for x in s])
        #print('hexa', hexa)
        #print(binascii.a2b_hex(hexa))
        text = b''.join([chr(int(x)).encode() if 0x20 <= int(x) < 0x7F else b'.' for x in s])
        #print('text', text)

        result.append(b'%04X  %-*s  %s' % (i, length*(digits + 1), hexa, text))
    print((b'\r\n'.join(result)).decode())

def receive_from(connection):
    buffer = b''
    #タイムアウト値を5秒に設定（ターゲットに応じて要調整）
    connection.settimeout(5)
    try:
        #データを受け取らなくなるかタイムアウトになるまでデータを受信してbufferに格納
        while True:
            data = connection.recv(4096)

            if not data:
                break
            buffer += data
    except:
        pass
        print(traceback.print_exc())
    return buffer

#リモート側のホストに送る全リクエストのデータの改変
def request_handler(buffer):
    #パケットの改変を実施
    return buffer

def response_handler(buffer):
    #パケットの改変を実施
    return buffer

def main():
    #コマンドライン引数の解釈
    if len(sys.argv[1:]) != 5:
        print('Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [recieve_first]')
        print('Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True')
        sys.exit(0)
    #ローカル側で通信傍受を行うための設定
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    #リモート側の設定
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    #リモート側にデータを送る前にデータ受信を行うかどうかの指定
    recieve_first = sys.argv[5]

    if 'True' in recieve_first:
        recieve_first = True
    else:
        recieve_first = False

    #通信待機ソケットの起動
    server_loop(local_host, local_port, remote_host, remote_port, recieve_first)

main()