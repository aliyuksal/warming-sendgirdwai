from flask import Flask, request, jsonify
import subprocess
import logging
from werkzeug.exceptions import BadRequest
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Loglama ayarları
logging.basicConfig(filename='ollama_api.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def run_ollama_model(model: str, input_text: str) -> str:
    """
    Ollama modelini çalıştır ve verilen girdiye göre çıktı al.
    """
    try:
        # Ollama komutunu çalıştırma
        command = ['C:/Users/Administrator/AppData/Local/Programs/Ollama/ollama.exe', 'run', model, input_text]

        # stdout ve stderr'i PIPE kullanarak yönlendirme
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

        # stdout ve stderr'i loglayalım
        logging.info(f"STDOUT: {result.stdout}")
        logging.error(f"STDERR: {result.stderr}")

        # Hata kontrolü
        if result.returncode != 0:
            return f"Model çalıştırılırken hata oluştu: {result.stderr}"
        
        # Model çıktısını kontrol et ve None ise varsayılan bir değer döndür
        if result.stdout is None or result.stdout.strip() == "":
            logging.error("AI model returned no output.")
            return "AI model returned no output."

        # Model çıktısını logla
        logging.info(f"Model Output: {result.stdout.strip()}")
        return result.stdout.strip()

    except FileNotFoundError:
        logging.critical("Ollama executable not found. Check the installation path.")
        return "Ollama çalıştırılabilir dosyası bulunamadı. Lütfen yükleme yolunu kontrol edin."

    except Exception as e:
        logging.exception("Unexpected error occurred")
        return f"Beklenmeyen bir hata oluştu: {str(e)}"




def validate_request_data(data: dict):
    """
    İstek verilerini doğrula ve eksik alanları kontrol et.

    Args:
    - data (dict): API'ye gelen JSON verisi.

    Raises:
    - BadRequest: Gerekli veri eksikse veya hatalıysa.
    """
    if 'input' not in data:
        raise BadRequest('Lütfen geçerli bir input değeri sağlayın.')

    # Model bilgisi opsiyoneldir, sağlanmazsa varsayılan olarak 'llama3.2' kullanılır.
    if 'model' in data and not isinstance(data['model'], str):
        raise BadRequest('Model adı geçerli bir string olmalıdır.')


@app.route('/run_model', methods=['POST'])
def run_model():
    try:
        # JSON'dan model ve input verilerini alın
        data = request.get_json()

        # İstek verilerini doğrula
        validate_request_data(data)
        
        model = data.get('model', 'llama3.2')  # Varsayılan model 'llama3.2'
        input_text = data['input']

        # Modeli çalıştır ve çıktıyı al
        output = run_ollama_model(model, input_text)

        # Başarı durumunda JSON cevabı döndür
        return jsonify({
            'model': model,
            'input': input_text,
            'output': output
        }), 200  # 200: OK

    except BadRequest as e:
        logging.warning(f"Bad request: {str(e)}")
        return jsonify({'error': str(e)}), 400  # 400: Bad Request

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Bir hata oluştu.'}), 500  # 500: Internal Server Error


if __name__ == '__main__':
    # Flask sunucusunu tüm arayüzlerde başlat
    app.run(host='0.0.0.0', port=5000, debug=True)

