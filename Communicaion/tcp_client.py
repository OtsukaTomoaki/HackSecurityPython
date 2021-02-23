import socket
import pprint

target_host = '0.0.0.0'
target_port = 9999

#ソケットオブジェクトの作成
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#サーバーへ接続
client.connect((target_host, target_port))

#データの送信
client.send(b'''GET / HTTP/1.1
Host: google.com

''')

#データの受信
response = client.recv(4096)
pprint.pprint(response)
