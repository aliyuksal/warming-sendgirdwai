import logging
from smtp_service import SMTPService
from ai_content_generator import AIContentGenerator
from recipient import RecipientManager  # Alıcı yönetimi için içe aktarma

class EmailManager:
    def __init__(self, smtp_service, ai_content_generator):
        self.smtp_service = smtp_service  # SMTP servisi entegrasyonu
        self.ai_content_generator = ai_content_generator  # AI içerik oluşturma entegrasyonu
        self.sent_emails = []  # Gönderilen e-postaları izlemek için liste
        logging.basicConfig(filename='email_manager.log', level=logging.INFO)

    def send_email_to_recipient(self, recipient):
        """
        Bir alıcıya e-posta gönderir ve durumu loglar.
        """
        # AI ile e-posta içeriği oluştur
        content = self.ai_content_generator.generate_email_content(recipient.full_name(), recipient.unique_code)
        
        # E-posta gönderimini yap
        try:
            self.smtp_service.send_email(recipient.email, "Özel Fırsat!", content)
            self.sent_emails.append(recipient.email)
            logging.info(f"Email successfully sent to {recipient.email}")
        except Exception as e:
            logging.error(f"Failed to send email to {recipient.email}: {str(e)}")

    def send_bulk_emails(self, recipients):
        """
        Birden fazla alıcıya toplu e-posta gönderimi yapar.
        """
        for recipient in recipients:
            self.send_email_to_recipient(recipient)

    def retry_failed_emails(self, recipients):
        """
        Başarısız olan e-posta gönderimleri için tekrar deneme yapar.
        """
        failed_recipients = [recipient for recipient in recipients if recipient.email not in self.sent_emails]
        if failed_recipients:
            logging.info("Retrying failed email sends...")
            self.send_bulk_emails(failed_recipients)


# Test fonksiyonu
if __name__ == "__main__":
    # RecipientManager ile CSV dosyasından alıcıları yükle
    csv_file = 'recipients.csv'
    recipient_manager = RecipientManager(csv_file)
    recipients = recipient_manager.get_all_recipients()

    # SMTPService ve AIContentGenerator örneklerini oluştur
    smtp_service = SMTPService()
    ai_content_generator = AIContentGenerator('http://localhost:5000/run_model', 'C:/Users/Administrator/Desktop/4warm/prompt.txt')

    # EmailManager örneğini oluştur ve toplu e-posta gönderimi yap
    email_manager = EmailManager(smtp_service, ai_content_generator)
    email_manager.send_bulk_emails(recipients)

    # Başarısız olan gönderimler için tekrar deneme
    email_manager.retry_failed_emails(recipients)
