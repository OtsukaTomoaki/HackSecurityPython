import socket
import pprint

target_host = 'localhost'
target_port = 80

#ソケットオブジェクトの作成
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#データの送信
client.sendto(b'AAABBBXCC', (target_host, target_port))

#データの受信
data, addr = client.recvfrom(4096)

pprint.pprint(data)
pprint.pprint(addr)