from scapy.all import *

#パケット処理用コールバック関数
def packet_callback(packet):
    if packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)
        if 'user' in mail_packet.lower() or 'pass' in mail_packet.lower():
            print(f'[*]Server: {packet[IP].dst}')
            print(f'[*]{packet[TCP].payload}')
    #print(packet.show())

#スニッファーを起動
sniff(prn=packet_callback, count=1)