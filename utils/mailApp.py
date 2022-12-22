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
from itsdangerous import URLSafeSerializer

def sendEmail(url, diff, topic, recipients):
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
    print('recipients list: ')
    print(*recipients, sep=", ")
    if len(recipients) > 0:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                #open mail port
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(EMAIL_ADDRESS, PASSWORD)
                
                #start loop
                for email in recipients:
                    #get token
                    s = URLSafeSerializer(os.environ.get('SECRET_KEY'), salt='unsubscribe')
                    token = s.dumps(email)
                    
                    msg = EmailMessage()
                    #if url is a list, then [0] is the URL and [1] is the substituted rating
    
                    if type(url) == list:
                        print('closest article to ' + diff + ' sent')
                        url = url[0]
    
                    # Create the body of the message (a plain-text and an HTML version).
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = 'Your Daily ' + topic + ' Article!'
                    msg['From'] = EMAIL_ADDRESS
                    msg['TO'] = email
                    
                    with open('utils/plaintext_email_template.txt') as f:
                        text = f.read()
                        text = text.replace("{{url}}", url)
                        text = text.replace("{{token}}", token)

                    with open('utils/email_template.html') as f:
                        html = f.read()
                        html = html.replace("{{url}}", url)
                        html = html.replace("{{token}}", token)
    
                    # Record the MIME types of both parts - text/plain and text/html.
                    part1 = MIMEText(text, 'plain')
                    part2 = MIMEText(html, 'html')
                    
                    # Attach parts into message container.
                    # According to RFC 2046, the last part of a multipart message, in this case
                    # the HTML message, is best and preferred.
                    msg.attach(part1)
                    msg.attach(part2)
                    # Send the message via local SMTP server.
                    smtp.sendmail(EMAIL_ADDRESS, msg['TO'], msg.as_string())
    
                print('Topic: ' + topic + ', diff: ' + diff + ' - sent to ' + str(len(recipients)) + ' users')
                return 'Success'

        except:
           print('There was an error, email not sent to: ' + ", ".join(recipients))
           return 'error'

    else:
        print('No receipients for this topic/diff')
        return 'No recepient settings match'
    
    