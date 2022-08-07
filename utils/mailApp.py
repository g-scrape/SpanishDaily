import os
import smtplib
from email.message import EmailMessage
# =============================================================================
# EMAIL_ADDRESS = os.environ.get('GMAIL')
# PASSWORD = os.environ.get('GMAIL_KEY')
# =============================================================================

# EMAIL_ADDRESS = 'daily-article@readspanishdaily.com'

def sendEmail(url, diff, topic, bcc):
    exec(open('/home/gharold/utils/env_vars.py').read())
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
            	if type(url) == list:
            	    print('closest article to ' + diff + ' sent')
            	    realDiff = url[1]
            	    url = url[0]
            	    body = 'No `' + diff + '` articles found for: ' + topic + '. The closest we could find was this `' + realDiff + '` article here: ' + url
            	else:
            	    body = 'Enjoy this `' + diff + '` ' + topic + ' article: ' + url

                #set body
            	msg.set_content(body)
            	msg['Subject'] = 'Your Daily ' + topic + ' Article!'
            	msg['From'] = EMAIL_ADDRESS
            	msg['BCC'] = bcc


            	#subject = 'Test subject'
            	#body = 'Test body'

            	#msg = f'Subject: {subject}\n\n{body}'

            	#smtp.sendmail(SENDER, RECEIVER, msg)
            	smtp.send_message(msg)
            	print('Topic: ' + topic + ', diff: ' + diff + ' - sent to ' + str(len(bcc)) + ' users')
            	return 'Success'
        except:
            print('There was an error, email not sent to: ' + ", ".join(bcc))
            return 'error'
    else:
        print('No receipients for this topic/diff')
        return 'No recepient settings match'