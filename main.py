from smtp_service import SMTPService
from ai_content_generator import AIContentGenerator
from recipient import RecipientManager
from email_manager import EmailManager
import logging

def main():
    # Loglama ayarları
    logging.basicConfig(filename='main.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Alıcıları CSV dosyasından yükle
    csv_file_path = 'recipients.csv'  # Alıcıların bulunduğu CSV dosyasının yolu
    logging.info(f"Loading recipients from {csv_file_path}...")
    recipient_manager = RecipientManager(csv_file_path)
    recipients = recipient_manager.get_all_recipients()

    if not recipients:
        logging.error("No recipients found in CSV file.")
        print("No recipients found.")
        return

    # SMTP servisini ve AI içerik oluşturucuyu başlat
    smtp_service = SMTPService()
    ai_content_generator = AIContentGenerator(
        ai_model_url="http://localhost:5000/run_model",  # Flask API URL'si
        prompt_file_path="C:/Users/Administrator/Desktop/4warm/prompt.txt"  # prompt.txt dosyasının tam yolu
    )

    # EmailManager oluştur
    email_manager = EmailManager(smtp_service, ai_content_generator)

    # E-posta başlık ve içerik şablonları
    subject_template = "Merhaba {name}, size özel bir teklifimiz var!"
    content_template = "Merhaba {name}, işte sizin özel indirim kodunuz: {unique_code}. Fırsatları kaçırmayın!"

    # Toplu e-posta gönderimi başlat
    logging.info("Starting bulk email sending...")
    email_manager.send_bulk_emails(recipients)

    # Başarısız olan gönderimler için tekrar deneme
    logging.info("Retrying failed emails, if any...")
    email_manager.retry_failed_emails(recipients)

if __name__ == "__main__":
    main()
