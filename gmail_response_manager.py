import csv
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from ai_content_generator import AIContentGenerator
from datetime import datetime

# Gmail API yetkilendirme dosyası
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]


def load_gmail_service():
    """Gmail API servisini yükler."""
    creds = Credentials.from_authorized_user_file('C:/Users/Administrator/Desktop/4warm/token.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    return service

def extract_message_content(msg):
    """E-postanın gövdesini çıkartır ve döner."""
    try:
        if 'data' in msg['payload']['body']:
            # E-posta gövdesi direk 'data' içinde varsa
            message_content = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        elif 'parts' in msg['payload']:
            # E-posta 'parts' içinde bölünmüşse, bölümleri birleştir
            message_content = ""
            for part in msg['payload']['parts']:
                if 'body' in part and 'data' in part['body']:
                    message_content += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            message_content = "Gönderi boş ya da desteklenmeyen formatta."
        return message_content
    except Exception as e:
        return f"Message decoding error: {str(e)}"

def check_email_responses(service, csv_file='responses.csv'):
    """Gmail'den gelen yanıtları kontrol eder ve responses.csv dosyasına kaydeder."""
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])

    if not messages:
        print('No new messages.')
        return

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            sender_email = next(header['value'] for header in email_data if header['name'] == 'From')
            message_content = extract_message_content(msg)

            # Yanıtı CSV'ye kaydet
            received_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([None, sender_email, message_content, '', False, received_at, '', ''])

            # E-posta'yı okundu olarak işaretle
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

    print(f"Yanıtlar {csv_file} dosyasına kaydedildi.")

def send_email_response(service, recipient_email, subject, content):
    """Gmail API üzerinden yanıt gönderir."""
    message = {
        'raw': base64.urlsafe_b64encode(f"From: me\nTo: {recipient_email}\nSubject: {subject}\n\n{content}".encode('utf-8')).decode('utf-8')
    }
    try:
        send_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"E-posta gönderildi: {recipient_email}")
        return send_message
    except Exception as e:
        print(f"E-posta gönderilemedi: {recipient_email}. Hata: {str(e)}")
        return None


def process_responses_and_generate_replies(service, ai_content_generator, csv_file='responses.csv'):
    """Responses.csv'deki yanıtlara göre AI ile yanıt oluşturur ve yanıtları gönderir."""
    updated_rows = []
    
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Başlık satırını atla

        for row in reader:
            email_id, sender_email, message_content, response_content, response_sent, received_at, responded_at, response_code = row
            
            if response_sent == 'False':  # Yanıt gönderilmemişse
                # AI ile yanıt oluştur
                ai_response = ai_content_generator.generate_email_content(sender_email, email_id)

                # Yanıtı gönder
                send_result = send_email_response(service, sender_email, "Yanıtınız için teşekkürler!", ai_response)
                
                if send_result:
                    response_sent = 'True'
                    responded_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    response_code = '200'
                    response_content = ai_response  # Gönderilen yanıtı CSV'ye kaydediyoruz
                else:
                    response_code = '500'

            updated_rows.append([email_id, sender_email, message_content, response_content, response_sent, received_at, responded_at, response_code])

    # CSV'yi güncelle
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['email_id', 'sender_email', 'message_content', 'response_content', 'response_sent', 'received_at', 'responded_at', 'response_code'])
        writer.writerows(updated_rows)


    # CSV'yi güncelle
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['email_id', 'sender_email', 'message_content', 'response_content', 'response_sent', 'received_at', 'responded_at', 'response_code'])
        writer.writerows(updated_rows)

if __name__ == "__main__":
    service = load_gmail_service()
    ai_content_generator = AIContentGenerator('http://localhost:5000/run_model', 'C:/Users/Administrator/Desktop/4warm/prompt.txt')

    # Gmail yanıtlarını kontrol et ve responses.csv dosyasına kaydet
    check_email_responses(service)

    # Yanıtları işle ve AI ile yanıt oluşturup gönder
    process_responses_and_generate_replies(service, ai_content_generator)
