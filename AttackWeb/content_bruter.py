import queue
import threading
import os
import requests

threads = 3

target_url = 'http://testphp.vulnweb.com'
wordlist_file = './tmp/all.txt' #SVNDiggerから
resume = None
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:19.0)'

def build_wordlist(wordlist_file):
    #単語の辞書を読み取る
    with open(wordlist_file, 'rt') as reader:
        raw_words = reader.readlines()

    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        word = word.rstrip()

        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print(f'Resuming wordlist from: {resume}')
        else:
            words.put(word)
    return words

def dir_bruter(word_queue, extentions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []

        #ファイル拡張子があるかチェックする。
        #なければディレクトリのパスとして総当たり攻撃の対象とする
        if '.' not in attempt:
            attempt_list.append(f'/{attempt}/')
        else:
            attempt_list.append(f'/{attempt}')

        #拡張子の総当たりをしたい場合
        if extentions:
            for extention in extentions:
                attempt_list.append(f'/{attempt}')

        #作成したリストの最後まで繰り返す
        for brute in attempt_list:
            url = f'{target_url}{requests.utils.quote(brute)}'
            try:
                headers = {}
                headers['User-Agent'] = user_agent
                res = requests.get(url, headers = headers)
                res.raise_for_status()
                print(f'{res.status_code}, {url}')
            except Exception as ex:
                print(f'!!! {ex}')

word_queue = build_wordlist(wordlist_file)
extentions = ['.php', '.bak', 'orig', 'inc']

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue, extentions,))
    t.start()