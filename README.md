OOP yapısıyla bu proje şu şekilde çalışabilir:

SMTPService sınıfı, SendGrid ile SMTP üzerinden e-posta gönderme ve yanıtları alma görevini üstlenir.
AIContentGenerator sınıfı, Llama modeli ile her alıcıya özel e-posta içeriği oluşturur.
EmailManager sınıfı, alıcılara toplu e-posta gönderme işlemlerini yönetir ve yanıtları işler.
Recipient sınıfı ise her bir alıcıyı, onların adını, e-postasını ve benzersiz kodunu içeren bir nesne olarak temsil eder.

smtp_warming_project/

│
├── smtp_service.py        # SMTPService sınıfı

├── ai_content_generator.py # AIContentGenerator sınıfı

├── email_manager.py       # EmailManager sınıfı

├── recipient.py           # Recipient sınıfı

└── main.py                # Ana çalışma dosyası (main.py)



**Çalıştırmadan önce api.py çalıştır, llama modelini API ile çalıştırmak için kullanılır.
