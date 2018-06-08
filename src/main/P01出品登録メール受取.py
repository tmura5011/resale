import shutil
from datetime import datetime
import imaplib
import sys

sys.path.append("/..")
from bl import 出品登録 as read_list
from util import gmail受信 as read_gmail
from util import gmail送信 as send_gmail

host = "imap.gmail.com"
user = "autoservice0111"
password = "94t5092a"
mailbox = "INBOX"

#メールサーバ指定
M = imaplib.IMAP4_SSL(host=host)

#ログイン
M.login(user, password)

try:
    #メールボックス選択
    M.select(mailbox)

    #未読メッセージ取得
    typ, data = M.search(None, "UNSEEN")

    for num in data[0].split():
        try:
            typ, data = M.fetch(num, "(RFC822)")
            mail = read_gmail.imap4mail(data[0][1])
            read_gmail.analize_mail(mail)
        finally:
            #未読に戻す
            M.store(num, "-FLAGS", "\\Seen")

        #拡張子チェック
        if "出品登録" not in mail.title:
            continue

        #ファイルを処理
        for key, value in mail.files.items():

            #ファイルを移動
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            infile = "../../file/" + key.replace(".csv", now + ".csv")
            outfile = "../../file/" + key.replace(".csv", now + "結果.csv")
            shutil.move(key, infile)

            #ファイルを取込
            read_list.read_file(infile, outfile, mail.sender)

            #ファイルを送信
            mailto = mail.sender
            subject = "Re:" + mail.title
            body = mail.body
            attach = outfile
            send_gmail.gmail_send_message(mailto, subject, body, attach)

        #既読にする
#        M.store(num, "+FLAGS", "\\Seen")

finally:
    M.close()
    M.logout()
