import imaplib
import email
import re
import datetime
from utils.config import Config
from datetime import datetime, timedelta
from email.header import decode_header

class EmailHelper:
    def decode_content(content, charset=None):
        if charset is None:
            # Try common encodings
            encodings = ['utf-8', 'ascii', 'iso-8859-1', 'windows-1252', 'latin1']
            for encoding in encodings:
                try:
                    return content.decode(encoding)
                except (UnicodeDecodeError, AttributeError):
                    continue
            # If all attempts fail, try to decode ignoring errors
            return content.decode('utf-8', errors='ignore')
        try:
            return content.decode(charset)
        except (UnicodeDecodeError, AttributeError):
            return content.decode('utf-8', errors='ignore')
        
    def get_otp_from_email():
        # Connect to the IMAP server
        imap_port = 993
        imap_server = imaplib.IMAP4_SSL(Config.EMAIL_IMAP_SERVER, imap_port)
        imap_server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
        
        # Select the inbox
        imap_server.select("INBOX")
        
        # Search for recent emails (within last 5 minutes)
        date_format = (datetime.now() - timedelta(minutes=4)).strftime("%d-%b-%Y")
        _, message_numbers = imap_server.search(None, f'(SINCE "{date_format}" SUBJECT "Booking.com")')
        
        # Pattern to match OTP in Booking.com subject format
        subject_pattern = r'Booking\.com – ([A-Z0-9]{6}) is your verification code'
        
        num = message_numbers[0].split()[-1]  # Get the most recent email number
        # Fetch the email message by ID
        _, msg_data = imap_server.fetch(num, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        
        # Get the email subject
        subject_header = decode_header(email_message["subject"])[0]
        subject = subject_header[0]
        if isinstance(subject, bytes):
            subject = EmailHelper.decode_content(subject)
        
        # Check for OTP in subject
        subject_match = re.search(subject_pattern, subject)
        if subject_match:
            imap_server.close()
            imap_server.logout()
            return subject_match.group(1)  # Return the captured OTP group
            
        # If not found in subject, check email body as backup
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset()
                    content = part.get_payload(decode=True)
                    body = EmailHelper.decode_content(content, charset)
                    # Search for OTP in the email body
                    body_match = re.search(r'\b([A-Z0-9]{6})\b', body)
                    if body_match:
                        imap_server.close()
                        imap_server.logout()
                        return body_match.group(1)
        else:
            charset = email_message.get_content_charset()
            content = email_message.get_payload(decode=True)
            body = EmailHelper.decode_content(content, charset)
            body_match = re.search(r'\b([A-Z0-9]{6})\b', body)
            if body_match:
                imap_server.close()
                imap_server.logout()
                return body_match.group(1)
        
        imap_server.close()
        imap_server.logout()
        return None