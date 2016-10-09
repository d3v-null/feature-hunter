# Import smtplib for the actual sending function
import smtplib
from tabulate import tabulate

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Alerter(object):
    @classmethod
    def tabulate_changes(cls, changes, tablefmt):
        return tabulate(changes.items(), headers=["target", "changes"], tablefmt=tablefmt)

    @classmethod
    def create_alert(cls, changes, smtp_params, recipients=None):
        if not (changes or smtp_params):
            return
        for key in ['sender', 'pass', 'host', 'port']:
            assert smtp_params[key], "must have key %s" % key
        sender = smtp_params['sender']
        if not recipients:
            recipients = [sender]
        msg = MIMEMultipart('alternative')
        msg['subject'] = "[Feature Hunter] Changes detected on " + ", ".join(changes.keys())
        msg['to'] = str(recipients)
        msg['from'] = sender

        content = "Here is the table of changes"
        content_text = content + "\n" + cls.tabulate_changes(changes, tablefmt='simple')
        content_html = """\
<html>
  <head></head>
  <body>
    <p>{content}</p>
    {table}
  </body>
</html>
""".format(
    content=content,
    table=cls.tabulate_changes(changes, tablefmt="html")
)
        msg.attach(MIMEText(content_text, 'plain'))
        msg.attach(MIMEText(content_html, 'html'))

        s = smtplib.SMTP_SSL(smtp_params['host'], str(smtp_params['port']), 'ich.ddns.me')
        # s = smtplib.SMTP(smtp_params['host'], str(smtp_params['port']))
        s.set_debuglevel(1)
        s.ehlo()
        # s.starttls()
        # s.ehlo()
        print "logging in with %s : %s" % (sender, smtp_params['pass'])
        s.login(sender, smtp_params['pass'])
        print "Sending message from %s to %s: %s" % (
            sender, str(recipients), msg.as_string()
        )
        s.sendmail(sender, recipients, msg.as_string())
        s.quit()

        # s = smtplib.SMTP('localhost')
        # s.sendmail(msg['from'], recipients, msg.as_string())
        # s.quit()
