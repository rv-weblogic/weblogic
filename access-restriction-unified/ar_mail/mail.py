
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

import os, sys
from pprint import pformat

import ar_log.log as ar_log
console = ar_log.get_logger("console")

def send(email_from,
         email_to,
         email_subject,
         email_body,
         server_host,
         server_port,
         attachments=[],):

    assert isinstance(email_to, list)
    assert isinstance(attachments, list)

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = COMMASPACE.join(email_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = email_subject

    console.debug(pformat(vars()))

    msg.attach( MIMEText(email_body) )

    for f in attachments:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' %
                        os.path.basename(f))
        msg.attach(part)
    #/for f

    err = ""
    try:
        smtp = smtplib.SMTP(host=server_host,
                            port=server_port,
                            timeout=3)
        #smtp.set_debuglevel(True)
        try:
            smtp.sendmail(email_from, email_to, msg.as_string())
        finally:
            smtp.close()
    except Exception:
        _type, e, _trace = sys.exc_info()
        err = str(e)
    return err
#/def send_mail