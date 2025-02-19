# KolayCMS

KolayCMS, Python Flask ile geliştirilmiş, kullanımı kolay bir içerik yönetim sistemidir.

## Özellikler

- Tema desteği
- Dinamik menü yönetimi
- Sayfa yönetimi
- Blog yönetimi
- Slider yönetimi
- Tema renk ve stil özelleştirme
- Responsive tasarım
- SEO dostu URL yapısı

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/aligencturk/KolayCMS.git
cd KolayCMS
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac için
venv\Scripts\activate     # Windows için
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
python recreate_db.py
```

5. Uygulamayı çalıştırın:
```bash
python app.py
```

## Kullanım

1. Tarayıcınızda `http://localhost:5001` adresine gidin
2. Admin paneline erişmek için `http://localhost:5001/admin` adresini kullanın
3. Varsayılan admin girişi:
   - Kullanıcı adı: admin@admin.com
   - Şifre: admin123

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: Açıklama'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Bir Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.
