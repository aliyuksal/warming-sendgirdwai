import csv
import logging

# Loglama ayarları
logging.basicConfig(filename='recipient_manager.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Recipient:
    """
    Alıcı sınıfı: Alıcı bilgilerini saklar ve işlem yapar.
    """
    def __init__(self, name, last_name, email, unique_code):
        self.name = name.strip()
        self.last_name = last_name.strip()
        self.email = email.strip().lower()  # E-posta adresini küçük harfe çevir
        self.unique_code = unique_code.strip()

    def full_name(self):
        """
        Alıcının tam adını döner.
        """
        return f"{self.name} {self.last_name}"

    def __str__(self):
        """
        Alıcı bilgilerini string olarak döner.
        """
        return f"Name: {self.full_name()}, Email: {self.email}, Unique Code: {self.unique_code}"

class RecipientManager:
    """
    RecipientManager sınıfı: Alıcıları yükler, doğrular ve yönetir.
    """
    def __init__(self, csv_file_path):
        """
        Alıcı bilgilerini CSV dosyasından yükler ve listeler.
        """
        self.recipients = []
        self.csv_file_path = csv_file_path
        self.load_recipients_from_csv(csv_file_path)

    def load_recipients_from_csv(self, csv_file_path):
        """
        CSV dosyasından alıcı bilgilerini okur ve Recipient nesneleri oluşturur.
        """
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if self.is_valid_recipient(row):
                        recipient = Recipient(
                            name=row['name'],
                            last_name=row['lastname'],
                            email=row['email'],
                            unique_code=row['unique_code']
                        )
                        self.recipients.append(recipient)
                        logging.info(f"Added recipient: {recipient}")
                    else:
                        logging.warning(f"Invalid recipient data skipped: {row}")
        except FileNotFoundError:
            logging.error(f"CSV file not found: {csv_file_path}")
            print(f"Error: CSV file '{csv_file_path}' not found.")
        except Exception as e:
            logging.error(f"Error loading recipients from CSV: {str(e)}")
            print(f"Error loading recipients from CSV: {str(e)}")

    def is_valid_recipient(self, recipient_data):
        """
        Alıcı verilerini doğrular. E-posta adresinin varlığı ve diğer bilgilerin geçerliliğini kontrol eder.
        """
        return all([
            'name' in recipient_data and recipient_data['name'].strip(),
            'lastname' in recipient_data and recipient_data['lastname'].strip(),
            'email' in recipient_data and self.is_valid_email(recipient_data['email']),
            'unique_code' in recipient_data and recipient_data['unique_code'].strip()
        ])

    def is_valid_email(self, email):
        """
        E-posta adresini temel doğrulama ile kontrol eder. (Basit bir kontrol, regex ile daha güçlü doğrulama eklenebilir.)
        """
        return '@' in email and '.' in email

    def get_all_recipients(self):
        """
        Tüm alıcıları döner.
        """
        return self.recipients

    def find_recipient_by_email(self, email):
        """
        E-posta adresine göre alıcıyı bulur.
        """
        email = email.strip().lower()  # E-posta adresini normalize et
        for recipient in self.recipients:
            if recipient.email == email:
                return recipient
        logging.info(f"Recipient not found for email: {email}")
        return None

    def total_recipients(self):
        """
        Toplam alıcı sayısını döner.
        """
        return len(self.recipients)

    def log_summary(self):
        """
        Alıcılar hakkında özet bir raporu loglar.
        """
        logging.info(f"Total recipients loaded: {self.total_recipients()}")
        for recipient in self.recipients:
            logging.info(str(recipient))


# Test kodu (opsiyonel):
if __name__ == "__main__":
    csv_file = 'recipients.csv'  # Alıcı bilgilerini içeren CSV dosyasının yolu
    manager = RecipientManager(csv_file)
    
    # Tüm alıcıları listele
    for recipient in manager.get_all_recipients():
        print(recipient)

    # Belirli bir e-posta adresine göre alıcıyı bul
    email = 'beyhanogul1@gmail.com'
    found_recipient = manager.find_recipient_by_email(email)
    if found_recipient:
        print(f"Recipient found: {found_recipient}")
    else:
        print(f"No recipient found for email: {email}")
    
    # Toplam alıcı sayısı
    print(f"Total recipients: {manager.total_recipients()}")
    
    # Logları yazdır
    manager.log_summary()
