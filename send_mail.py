#! /usr/bin/python3

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import smtplib
import argparse
import os
import configparser
import inquirer

class Configuration():
    def __init__(self,user,password,port,SMTP_servername):
        self.user = user
        self.password = password
        self.port = port
        self.SMTP_servername = SMTP_servername
    
    def load_config(self,config_path):
        full_path_name = os.path.join(os.path.dirname(__file__),config_path)
        conf = configparser.ConfigParser()
        with open(full_path_name,'r') as f:
            conf.read_file(f)
        try:
            self.password = conf["DEFAULT"]['password']
            self.user = conf["DEFAULT"]['user']
            self.port = conf["DEFAULT"]['port']
            self.SMTP_servername = conf["DEFAULT"]['SMTP_servername']
        except:
            print("Something went wrong loading configuration")
    
    def write_config(self,config_path):
        full_path_name = os.path.join(os.path.dirname(__file__),config_path)
        conf = configparser.ConfigParser()
        with open(full_path_name,'r') as f:
            conf.read_file(f)
        questions = [
            inquirer.Text('user', message="What's your email"),
            inquirer.Text('password', message="What's your email password (app password)"),
            inquirer.Text('SMTP_servername', message="SMTP server"),
            inquirer.Text("port",message="The SMTP server port")
        ]

        results = inquirer.prompt(questions)

        results['port'] = int(results.get('port'))
        conf.read_dict({"DEFAULT":results})
        print("Configuration saved sucessfully")
        with open(full_path_name,"w") as f:
            conf.write(f)

        #tomllib.load()
        

__author__ = "Henrique Domiciano <henriquedomiciano@yahoo.com>"
__program__ = "send_mail"


usage = """
Used to send email messages, to be able to send email just change the parameters.py change the user and password, or the smtp server
you can also send attachments, messages etc. 

If running first time run with -config as the only option to configure. 
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
args.add_argument('-c','--config',action='store_true')
argum = args.parse_args()

if argum.config:
    c = Configuration(None,None,None,None)
    c.write_config("parameters.config")
    c.load_config("parameters.config")
    exit()


send_to = argum.to
c = Configuration(None,None,None,None)
c.load_config('parameters.config')
log(argum.verbose,"Configuration loaded")

msg = MIMEMultipart()
msg["From"] = c.user
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
    with smtplib.SMTP(c.SMTP_servername, c.port) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user=c.user, password=c.password)
            mail = smtp.sendmail(c.user, send_to, msg.as_string())
            if mail == {} and argum.verbose:
                print(f"[INFO] mail sent to {(' '.join(send_to))}")
        except Exception as e:
            print(f"[ERROR] {e} happened")
