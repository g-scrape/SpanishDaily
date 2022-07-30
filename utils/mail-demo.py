import os
import smtplib

# =============================================================================
# EMAIL_ADDRESS = os.environ.get('GMAIL')
# PASSWORD = os.environ.get('GMAIL_KEY')
# =============================================================================
exec(open('/home/gharold/SpanishDaily/env_vars.py').read())
# EMAIL_ADDRESS = 'daily-article@readspanishdaily.com'
EMAIL_ADDRESS = os.environ.get('GMAIL')
PASSWORD = os.environ.get('GMAIL_KEY')

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
	smtp.ehlo()
	smtp.starttls()
	smtp.ehlo()

	smtp.login(EMAIL_ADDRESS, PASSWORD)

	subject = 'Test subject'
	body = 'Test body'

	msg = f'Subject: {subject}\n\n{body}'

	#smtp.sendmail(SENDER, RECEIVER, msg)
	smtp.sendmail(EMAIL_ADDRESS, 'glensilas95@gmail.com', msg)