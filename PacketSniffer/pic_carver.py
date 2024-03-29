import re
import zlib
import cv2

from scapy.all import *

pictures_directory = 'pictures'
faces_directory = 'faces'
pcap_file = 'bhp.pcap'

def get_http_headers(http_payload):
    try:
        #HTTPのヘッダー抽出
        headers_raw = http_payload[:http_payload.index("\\r\\n\\r\\n")+2]
        #ヘッダーの各要素を辞書化
        headers = dict(re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n)', headers_raw))
    except Exception as ex:
        print(ex)
        return None

    if 'Content-Type' not in headers:
        return None
    return headers

def extract_image(headers, http_payload):
    image = None
    image_type = None

    try:
        if 'image' in headers['Content-Type']:
            #画像種別と画像本体の取得
            image_type = headers['Content-Type'].split('/')[1]
            image = http_payload[http_payload.index('\r\n')+4:]

            #画像が圧縮されている場合は解凍
            try:
                if 'Content-Encoding' in headers.keys():
                    if headers['Content-Encoding'] == 'gzip':
                        image = zlib.decompress(image, 16+zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == 'deflate':
                        image = zlib.decompress(image)
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)
        return None, None
    return image, image_type

def face_detect(path, file_name):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifer('haarcascade_frontalface_alt.xml')
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))

    if len(rects) == 0:
        return False

    rects[:, 2:] += rects[:, :2]

    #画像中の全ての顔をハイライト
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
    cv2.imwrite(f'{faces_directory}/{pcap_file}-{file_name}', img)
    return True


def http_assembler(pcap_file):
    carved_images = 0
    faces_detected = 0

    a = rdpcap(pcap_file)

    sessions = a.sessions()

    for session in sessions:
        http_payload = ''
        for packet in sessions[session]:
            try:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    #ストリームの再構築
                    http_payload += str(packet[TCP].payload)
            except Exception as ex:
                print(ex)
        headers = get_http_headers(http_payload)

        if headers is None:
            continue

        image, image_type = extract_image(headers, http_payload)

        if image is not None and image_type is not None:
            #画像の保存
            file_name = f'{pcap_file}-pic_carver_{carved_images}.{image_type}'

            with open(f'{pictures_directory}/{file_name}', 'wb') as fd:
                fd.write(image)

            carved_images += 1

            #顔検出
            try:
                result = face_detect(f'{pictures_directory}/{file_name}', file_name)
                if result is True:
                    faces_detected += 1
            except Exception as ex:
                print(ex)
    return carved_images, faces_detected

def main():
    carved_images, faces_detected = http_assembler(pcap_file)
    print(f'Extracted: {carved_images} images.')
    print(f'Detected: {faces_detected} faces_detected.')

main()
