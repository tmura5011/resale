import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

def log(file, str):
    file.write(str + "\n")
    print(str)

#送信元メールアドレス
MAIL_FROM = "autoservice0111@gmail.com"
#送信元メールアドレスパスワード
MAIL_FROM_PWD = "94t5092a"

# メール作成
def gmail_create_message(to_addr, subject, body, attach):
    msg = MIMEMultipart(body)
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_addr
    msg["Bcc"] = MAIL_FROM
    msg["Date"] = formatdate()

    file = open(attach, "r")
    mime = MIMEText(file.read(), _subtype="csv")
    file.close()

    fname = os.path.basename(attach)
    mime.add_header("Content-Disposition","attachment", filename=fname)
    msg.attach(mime)

    return msg

# メール送信
def gmail_send_message(mailto, subject, body, attach):
    msg = gmail_create_message(mailto, subject, body, attach)
    smtpobj = smtplib.SMTP("smtp.gmail.com", 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(MAIL_FROM, MAIL_FROM_PWD)
    smtpobj.sendmail(MAIL_FROM, mailto, msg.as_string())
    smtpobj.close()

