#! /usr/bin/python3

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import smtplib
import parameters
import argparse
import os

__author__ = "Henrique Domiciano <henriquedomiciano@yahoo.com>"
__program__ = "send_mail"


usage = """
Used to send email messages, to be able to send email just change the parameters.py change the user and password, or the smtp server
you can also send attachments, messages etc. 
"""


def log(verb, message):
    if verb:
        print(f"[INFO] {message}")


args = argparse.ArgumentParser(prog=__program__, usage=usage)

args.add_argument("-t", "--to", nargs="+", default=[])
args.add_argument("-f", "--file")
args.add_argument("-s", "--subject")
args.add_argument("-m", "--message")
args.add_argument("-a", "--attachment", nargs="+", default=[])
args.add_argument("-v", "--verbose", action="store_true")

argum = args.parse_args()

send_to = argum.to

msg = MIMEMultipart()
msg["From"] = parameters.user
msg["To"] = COMMASPACE.join(send_to)
msg["Date"] = formatdate(localtime=True)
msg["Subject"] = argum.subject


log(verb=argum.verbose, message="Appending message")
msg.attach(MIMEText(argum.message))


log(
    verb=argum.verbose,
    message=f"Starting to Attach the files {' '.join(argum.attachment)}",
)
for f in argum.attachment:
    with open(f, "rb") as fil:
        part = MIMEApplication(fil.read(), Name=os.path.basename(f))
    log(verb=argum.verbose, message=f"Attached the file {f}")
    part["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(f)
    msg.attach(part)

if __name__ == "__main__":
    with smtplib.SMTP(parameters.SMTP_servername, parameters.port) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user=parameters.user, password=parameters.password)
            mail = smtp.sendmail(parameters.user, send_to, msg.as_string())
            if mail == {} and argum.verbose:
                print(f"[INFO] mail sent to {(' '.join(send_to))}")
        except Exception as e:
            print(f"[ERROR] {e} happened")
