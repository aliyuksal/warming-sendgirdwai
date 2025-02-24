import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from email_manager import EmailManager
from smtp_service import SMTPService
from ai_content_generator import AIContentGenerator

# SMTP servisi ve AI içerik oluşturucu nesnelerini oluştur
smtp_service = SMTPService()
ai_content_generator = AIContentGenerator('http://138.201.246.152:5000/run_model', 'prompt.txt')

# EmailManager nesnesi oluştur
email_manager = EmailManager(smtp_service, ai_content_generator)

# Örnek alıcı listesi
recipients = [
    {"name": "Ali", "unique_code": "ABC123", "email": "aliyuuksel13@gmail.com"},
    {"name": "Beyhan", "unique_code": "XYZ456", "email": "beyhanogul1@gmail.com"}
]

# Toplu e-posta gönderimini test et
email_manager.send_bulk_emails(recipients)
