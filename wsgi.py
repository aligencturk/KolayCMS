from app import create_app
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    app = create_app('development')
    
    if __name__ == '__main__':
        app.run(
            debug=True,
            use_reloader=True,
            host='127.0.0.1',
            port=5000,
            threaded=True
        )
except Exception as e:
    logger.error(f"WSGI uygulaması başlatılırken hata oluştu: {str(e)}", exc_info=True)
    raise 