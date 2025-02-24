import csv
import requests
import random

class AIContentGenerator:
    def __init__(self, ai_model_url, prompt_file_path):
        """
        AI model URL'sini ve prompt dosyasının yolunu alarak başlatır.
        """
        self.ai_model_url = ai_model_url  # AI model URL'si burada ayarlanır
        self.prompt_file_path = prompt_file_path  # prompt.txt dosyasının yolu
        self.prompts = self.load_prompts()  # Prompları dosyadan yükle

    def load_prompts(self):
        """
        Prompt'ları .txt dosyasından yükler ve bir liste olarak döner.
        
        Returns:
        - List[str]: Prompt metinlerinin listesi.
        """
        with open(self.prompt_file_path, 'r', encoding='utf-8') as file:
            prompts = file.readlines()  # prompt.txt dosyasını satır satır oku
        # Satır sonlarını temizleyelim
        prompts = [prompt.strip() for prompt in prompts]  # Gereksiz boşlukları kaldır
        return prompts

    def select_random_prompt(self):
        """
        Rastgele bir prompt seçer.
        
        Returns:
        - str: Seçilen prompt.
        """
        return random.choice(self.prompts)  # Promplar arasından rastgele birini seç

    def generate_email_content(self, recipient_name, unique_code):
        """
        Flask API'ye istek göndererek dinamik içerik oluşturur.
        
        Args:
        - recipient_name (str): Alıcının adı
        - unique_code (str): Alıcıya özel benzersiz kod
        
        Returns:
        - content (str): Oluşturulan e-posta içeriği
        """
        # Rastgele bir prompt seç ve name ile unique_code'u yerine koy
        prompt = self.select_random_prompt().format(name=recipient_name, unique_code=unique_code)

        # Flask API'ye gönderilecek JSON verisi
        payload = {
            'input': prompt,
            'model': 'llama3.2'  # Model adı burada belirtiliyor
        }

        try:
            # Flask API'ye POST isteği gönder
            response = requests.post(self.ai_model_url, json=payload)  # Belirtilen URL'ye istek gönder

            if response.status_code == 200:
                # AI modelinden gelen yanıtı döndür
                return response.json().get('output', 'No output returned from AI model.')
            else:
                return f"Failed to generate content: {response.status_code}"

        except Exception as e:
            return f"Error connecting to AI model: {str(e)}"

    def generate_from_csv(self, csv_file_path):
        """
        CSV dosyasını okuyarak her alıcı için AI modelinden içerik oluşturur.
        
        Args:
        - csv_file_path (str): CSV dosyasının yolu
        
        Returns:
        - None: Her alıcı için içerik oluşturulup gösterilir.
        """
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    name = row['name']
                    lastname = row['lastname']
                    email = row['email']
                    unique_code = row['unique_code']
                    
                    # Alıcı bilgilerini kullanarak e-posta içeriği oluştur
                    email_content = self.generate_email_content(f"{name} {lastname}", unique_code)

                    # İçeriği göster
                    print(f"Generated content for {name} {lastname} ({email}):\n{email_content}\n")

        except FileNotFoundError:
            print(f"CSV file not found: {csv_file_path}")

# AI model URL'sini ve prompt.txt dosyasının yolunu ayarlayın
ai_model_url = "http://138.201.246.152:5000/run_model"  # AI modeli için URL burada ayarlandı
prompt_file_path = r'C:\Users\Administrator\Desktop\4warm\prompt.txt'  # prompt.txt dosyasının tam yolu
ai_content_generator = AIContentGenerator(ai_model_url, prompt_file_path)

# CSV dosyasını kullanarak içerik oluştur
csv_file_path = r'C:\Users\Administrator\Desktop\4warm\recipients.csv'  # CSV dosyasının tam yolu
ai_content_generator.generate_from_csv(csv_file_path)
