import os
import logging
from dotenv import load_dotenv
import sendgrid
from sendgrid.helpers.mail import Mail
import ssl  # SSL doğrulamasını devre dışı bırakmak için
from time import sleep
from recipient import RecipientManager  # Alıcıları yönetmek için RecipientManager'ı içe aktar

# Sertifika doğrulamasını devre dışı bırak
ssl._create_default_https_context = ssl._create_unverified_context

# .env dosyasını yükle
load_dotenv()

# Loglama için ayarlar
logging.basicConfig(filename='smtp_service.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class SMTPService:
    def __init__(self):
        # .env dosyasından SendGrid API anahtarını al
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.sg = sendgrid.SendGridAPIClient(self.api_key)

    def send_email(self, recipient_email, subject, content, html_format=True, retries=3):
        """
        E-posta gönderme işlemi. HTML formatında veya düz metin formatında gönderim yapabilir.
        Gönderim başarısız olursa belirli bir sayıda yeniden deneme yapılır.
        """
        message = Mail(
            from_email='luiz@offerlytic.com',  # Onaylanmış SendGrid e-posta adresi
            to_emails=recipient_email,
            subject=subject,
            html_content=content if html_format else None,
            plain_text_content=content if not html_format else None
        )

        for attempt in range(retries):
            try:
                response = self.sg.send(message)
                logging.info(f"Email sent to {recipient_email}: Status Code {response.status_code}")
                print(f"Email sent to {recipient_email}: Status Code {response.status_code}")
                break
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                # Belirli bir süre bekleyip yeniden deneme yapar
                if attempt < retries - 1:
                    sleep(2)  # 2 saniye bekle
                else:
                    print(f"Failed to send email to {recipient_email} after {retries} attempts.")
                    logging.error(f"Failed to send email to {recipient_email} after {retries} attempts.")

    def send_bulk_emails(self, csv_file, subject_template, content_template, delay=10):
        """
        CSV dosyasından alıcı bilgilerini çekerek toplu e-posta gönderimi.
        """
        manager = RecipientManager(csv_file)  # Alıcı bilgilerini CSV'den yükle
        for recipient in manager.get_all_recipients():
            subject = subject_template.format(name=recipient.full_name())
            content = content_template.format(name=recipient.full_name(), unique_code=recipient.unique_code)
            
            # E-posta gönderimi
            self.send_email(recipient.email, subject, content)
            print(f"{delay} saniye bekleniyor...")
            sleep(delay)  # Gönderimler arasında bekleme süresi

    def check_responses(self):
        print("Checking email responses...")
        logging.info("Checking email responses...")

# Test kodu
if __name__ == "__main__":
    smtp_service = SMTPService()
    csv_file = 'recipients.csv'  # Alıcı bilgilerini içeren CSV dosyasının yolu
    subject_template = "Merhaba {name}, sizin için özel bir teklifimiz var!"
    content_template = "Merhaba {name}, işte size özel indirim kodunuz: {unique_code}. Fırsatları kaçırmayın!"
    
    smtp_service.send_bulk_emails(csv_file, subject_template, content_template, delay=5)
