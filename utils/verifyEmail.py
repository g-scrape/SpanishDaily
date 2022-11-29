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

def sendVerificationEmail(recipient):
#grab envVars locally or in prod
    path = ''
    if os.name == 'nt':
        path = 'C:/Users/glens/.spyder-py3/Practice Projects/SpanishDaily/SpanishDaily/home/gharold/utils/env_vars.py'
    elif os.name == 'posix':
        path = '/home/gharold/utils/env_vars.py'

    exec(open(path).read()) 
    EMAIL_ADDRESS = os.environ.get('GMAIL')
    PASSWORD = os.environ.get('GMAIL_KEY')

    print('recipient: ')
    print(recipient)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            #open mail port
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, PASSWORD)

            #get token
            s = URLSafeSerializer(os.environ.get('SECRET_KEY'), salt='verify')
            token = s.dumps(recipient)
            
            msg = EmailMessage()

            # Create the body of the message (a plain-text and an HTML version).
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Please verify your email'
            msg['From'] = EMAIL_ADDRESS
            msg['TO'] = recipient
            
            text = "Sorry! I haven't created a plaintext template yet :/"
            with open('utils/verify_template.html') as f:
                html = f.read()
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

        print("Verification email sent to: " + str(recipient))
        return 'Success'

    except:
       print('There was an error, email not sent to: ' + str(recipient))
       return 'error'

    
    