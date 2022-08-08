import os
import smtplib
from email.message import EmailMessage
# =============================================================================
# EMAIL_ADDRESS = os.environ.get('GMAIL')
# PASSWORD = os.environ.get('GMAIL_KEY')
# =============================================================================

# EMAIL_ADDRESS = 'daily-article@readspanishdaily.com'

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendEmail(url, diff, topic, bcc):
#grab envVars locally or in prod
    path = ''
    if os.name == 'nt':
        path = 'C:/Users/glens/.spyder-py3/Practice Projects/SpanishDaily/SpanishDaily/home/gharold/utils/env_vars.py'
    elif os.name == 'posix':
        path = '/home/gharold/utils/env_vars.py'

    exec(open(path).read()) 
    EMAIL_ADDRESS = os.environ.get('GMAIL')
    PASSWORD = os.environ.get('GMAIL_KEY')
    print('url: ')
    print(url)
    print('topic: ' + topic)
    print('diff: ' + diff)
    print('bcc list: ')
    print(*bcc, sep=", ")
    if len(bcc) > 0:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(EMAIL_ADDRESS, PASSWORD)
                msg = EmailMessage()
                #if url is a list, then [0] is the URL and [1] is the substituted rating
# =============================================================================
#                 if type(url) == list:
#                     print('closest article to ' + diff + ' sent')
#                     realDiff = url[1]
#                     url = url[0]
#                     body = 'No `' + diff + '` articles found for: ' + topic + '. The closest we could find was this `' + realDiff + '` article here: ' + url
#                 else:
#                     body = 'Enjoy this `' + diff + '` ' + topic + ' article: ' + url
# =============================================================================

                # Create the body of the message (a plain-text and an HTML version).
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'Your Daily ' + topic + ' Article!'
                msg['From'] = EMAIL_ADDRESS
                msg['BCC'] = "glensilas95@gmail.com"
                
                text = "this is the standard text string"
                with open('utils/email_template.html') as f:
                    html = f.read()
                    html = html.replace("{{url}}", url)

                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(text, 'plain')
                part2 = MIMEText(html, 'html')
                
                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
                msg.attach(part1)
                msg.attach(part2)
                # Send the message via local SMTP server.
                smtp.sendmail(EMAIL_ADDRESS, "glensilas95@gmail.com", msg.as_string())

                print('Topic: ' + topic + ', diff: ' + diff + ' - sent to ' + str(len(bcc)) + ' users')
                return 'Success'

        except:
           print('There was an error, email not sent to: ' + ", ".join(bcc))
            return 'error'

    else:
        print('No receipients for this topic/diff')
        return 'No recepient settings match'
    
    