# -*- coding:utf-8 -*-
import imaplib
import email
import email.header
import time
import io as cStringIO

class imap4mail(object):

    def __init__(self, data):
        """
        コンストラクタで与えられたメールデータの解析を実行する
        """
        self.files = {}

        #文字コード取得用
        buf = email.message_from_string(data.decode("utf-8"))
        msg_encoding = email.header.decode_header(buf.get("Subject"))[0][1] or "iso-2022-jp"
        #メッセージをパース
        msg = email.message_from_string(data.decode(msg_encoding))
        #タイトル取得
        self.title = self.decode(msg.get("Subject"))
        #送信者取得
        self.sender = self.decode(msg.get("From"))
        #送信日付取得
        self.date = self.get_format_date(msg.get("Date"))

        #添付ファイルを抽出
        for part in msg.walk():

            if part.get_content_maintype() == "multipart":
                continue

            #ファイル名を取得
            filename = part.get_filename()

            #ファイル名が取得できなければ本文
            if not filename:
                print("ファイル以外")
#                self.body = self.decode_body(part)
                self.body = ""

            #ファイル名が存在すれば添付ファイル
            else:
                filename = self.decode(filename)
                print("ファイル：" + filename)
                tmpfile = cStringIO.BytesIO()
                tmpfile.write(part.get_payload(decode=1))
                self.files[filename] = tmpfile

    def decode(self, dec_target):
        """
        メールタイトル、送信者のデコード
        """
        decodefrag = email.header.decode_header(dec_target)
        title = ""

        for frag, enc in decodefrag:
            if enc:
                title += str(frag, enc)
            else:
                title += str(frag)

        return title

    def decode_body(self, part):
        """
        メール本文のデコード
        """
        body = ""
        charset = str(part.get_content_charset())

        print(charset)

        if charset:
            body = str(part.get_payload(), charset)

        else:
            body = part.get_payload()

        return body

    def get_format_date(self, date_string):
        """
        メールの日付をtimeに変換
        http://www.faqs.org/rfcs/rfc2822.html
        "Jan" / "Feb" / "Mar" / "Apr" /"May" / "Jun" / "Jul" / "Aug" /"Sep" / "Oct" / "Nov" / "Dec"
        Wed, 12 Dec 2007 19:18:10 +0900
        """

        format_pattern = "%a, %d %b %Y %H:%M:%S"

        #3 Jan 2012 17:58:09という形式でくるパターンもあるので、
        #先頭が数値だったらパターンを変更
        if date_string[0].isdigit():
            format_pattern = "%d %b %Y %H:%M:%S"

        return time.strptime(date_string[0:-6], format_pattern)

def analize_mail(mail):

    #取得したメールの内容を表示
    print( mail.sender )
    print( mail.date )
    print( mail.title )
    print( mail.body)

    for key, value in mail.files.items():
        with open(key, "wb") as f:
            f.write(value.getvalue())

if __name__ == "__main__":

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
                mail = imap4mail(data[0][1])
                analize_mail(mail)
            finally:
                #未読に戻す
                M.store(num, "-FLAGS", "\\Seen")
    finally:
        M.close()
        M.logout()