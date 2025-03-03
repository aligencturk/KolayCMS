# Kolay CMS Panel Ürün Gereksinim Belgesi

## 📌 Temel Özellikler
- [ ] **Firebase Entegrasyonu**: Firestore + Authentication + Storage
- [ ] **Dinamik İçerik Yönetimi**: Gerçek zamanlı veri senkronizasyonu
- [ ] **Modüler Yapı**: 8 farklı içerik modülü
- [ ] **2025 WordPress Standartları**: WP REST API uyumluluğu

## 🎨 Tasarım Spesifikasyonları
```html
<!-- Tasarım Önizleme (partial) -->
<div class="w-64 bg-gray-800 text-white">
  <div class="p-4 text-2xl font-bold">
    <span class="text-primary">Art</span>Web
  </div>
  <nav class="mt-4">
    <!-- Modül Listesi -->
    <div class="sidebar-item p-4 flex items-center space-x-3">
      <i class="ri-slideshow-line"></i>
      <span>Slider Modülü</span>
    </div>
  </nav>
</div>
```

**Renk Paleti:**
| Renk         | Hex Kodu   | Kullanım Alanı       |
|--------------|------------|----------------------|
| Primary      | `#00BCD4`  | Butonlar, Başlıklar  |
| Secondary    | `#f44336`  | Hata Mesajları       |
| Dark BG      | `#1a202c`  | Sidebar Arkaplan     |

## 🔧 Teknik Mimari
```javascript
// Firebase Config Örneği
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "kolay-cms.firebaseapp.com",
  projectId: "kolay-cms",
  storageBucket: "kolay-cms.appspot.com"
};
```

**Modüller:**
1. Rapor Modülü - `reports`
2. Slider Yönetimi - `sliders`
3. Kurumsal İçerik - `corporate`
4. Ekip Üyeleri - `team`
5. İK Yönetimi - `hr`
6. Hizmetler - `services`
7. Projeler - `projects`
8. Kullanıcılar - `users`

## 📊 Veri Modeli
**Kullanıcı Modeli:**
```typescript
interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'editor' | 'user';
  createdAt: firebase.firestore.Timestamp;
}
```

## 🛠️ Geliştirme Stack'i
| Teknoloji    | Versiyon  | Amaç                |
|--------------|-----------|---------------------|
| React        | 18.2+     | UI Framework        |
| Tailwind CSS | 3.3+      | Styling             |
| Firebase     | 9.23+     | Backend Servisleri  |
| Remix Icon   | 4.5+      | İkon Seti           |

## ✅ Kabul Kriterleri
- [x] Tüm modüller sidebar'da listelenmeli
- [x] Kullanıcılar tablosu CRUD operasyonları desteklemeli
- [x] Tasarım Tailwind CSS ile responsive olmalı
- [x] Veriler Firebase'de kalıcı olarak saklanmalı

## 📅 Roadmap
1. Phase 1: Temel CMS Yapısı (Q4 2024)
2. Phase 2: WordPress Entegrasyonu (Q1 2025)
3. Phase 3: AI Destekli İçerik Üretimi (Q2 2025)

## ⏳ YAPILACAK
- [ ] **3. SEO ve Performans Optimizasyonu**
  - [ ] SEO Dostu URL'ler - Özel URL yapıları oluşturma
  - [ ] Meta Etiket Yönetimi - Sayfa başlığı, açıklama, anahtar kelimeleri düzenleme
  - [ ] Hızlı Önbellekleme - Daha hızlı yükleme süreleri için önbellek desteği
  - [ ] Mobil Uyumlu (Responsive Design) - Tüm cihazlarda sorunsuz çalışabilme

- [x] **4. Tema ve Özelleştirme Seçenekleri** ✅ (Tamamlandı)
  - [x] Tema Desteği - Farklı görünümler ekleyip değiştirebilme ✅ (Tamamlandı)
  - [x] Özelleştirilebilir Şablonlar - Sayfa düzenlerini değiştirebilme ✅ (Tamamlandı)
  - [x] Sürükle-Bırak Sayfa Düzenleyici - Teknik bilgi olmadan sayfa tasarımı yapabilme ✅ (Tamamlandı)

[Firebase Resmi Dokümantasyonu](https://firebase.google.com/docs) | [Tailwind Admin Şablonları](https://tailwindtemplates.co/admin)

## Görev Listesi

### Firebase Entegrasyonu Görevleri
- [x] Firebase projesi oluştur. ✅ (Tamamlandı)
  1. https://console.firebase.google.com/ adresine gidin
  2. "Yeni Proje Oluştur" butonuna tıklayın
  3. Proje adı olarak "KolayCMS" girin
  4. Google Analytics'i devre dışı bırakın
  5. "Proje Oluştur" butonuna tıklayın

- [x] Firestore'u yapılandır. ✅ (Tamamlandı)
  1. Sol menüden "Firestore Database" seçin
  2. "Veritabanı Oluştur" butonuna tıklayın
  3. Test modunda başlat seçeneğini seçin
  4. Bölge olarak "europe-west3" (Almanya) seçin

- [x] Authentication'ı etkinleştir. ✅ (Tamamlandı)
  1. Sol menüden "Authentication" seçin
  2. "Başlayın" butonuna tıklayın
  3. Email/Şifre yöntemini etkinleştirin

- [-] Storage'ı ayarla. ❌ (İptal - Ücretli servis)

- [x] Firebase konfigürasyonunu projeye ekle. ✅ (Tamamlandı)
  1. Proje ayarlarına gidin (⚙️ simgesi)
  2. "Hizmet hesapları" sekmesine gidin
  3. "Yeni özel anahtar oluştur" butonuna tıklayın
  4. İndirilen JSON dosyasını `serviceAccountKey.json` olarak projenin kök dizinine kaydedin
  5. .env dosyasını güncelleyin

### Dinamik İçerik Yönetimi Görevleri
- [x] Veri modellerini tanımla. ✅ (Tamamlandı)
  - BaseModel sınıfı oluşturuldu
  - Tüm modüller için model sınıfları tanımlandı
  - Veri doğrulama kuralları eklendi

- [x] Firestore'dan veri okuma işlevini geliştir. ✅ (Tamamlandı)
  - FirestoreManager sınıfı oluşturuldu
  - Döküman getirme metotları eklendi
  - Filtreleme ve sıralama özellikleri eklendi

- [x] Firestore'a veri yazma işlevini geliştir. ✅ (Tamamlandı)
  - Döküman ekleme metotları eklendi
  - Güncelleme ve silme işlevleri eklendi
  - Hata yönetimi eklendi

- [x] Gerçek zamanlı veri senkronizasyonunu sağla. ✅ (Tamamlandı)
  - Gerçek zamanlı dinleme metotları eklendi
  - Değişiklik callback'leri tanımlandı
  - Otomatik güncelleme sistemi kuruldu

### Modüler Yapı Görevleri
- [x] Her bir modül için ayrı klasörler oluştur. ✅ (Tamamlandı)
  - Rapor Modülü (reports)
  - Slider Yönetimi (sliders)
  - Kurumsal İçerik (corporate)
  - Ekip Üyeleri (team)
  - İK Yönetimi (hr)
  - Hizmetler (services)
  - Projeler (projects)
  - Kullanıcılar (users)

- [x] Modüller arası iletişimi sağla. ✅ (Tamamlandı)
  - BaseModule sınıfı oluşturuldu
  - Ortak CRUD işlemleri tanımlandı
  - Firestore entegrasyonu yapıldı

- [x] Modülleri sidebar'a entegre et. ✅ (Tamamlandı)
  - Blueprint'ler oluşturuldu
  - Routing yapısı kuruldu
  - Dinamik modül yükleme sistemi eklendi

### 2025 WordPress Standartları Görevleri
- [x] WP REST API uyumluluğunu araştır.
- [x] Gerekli API endpoint'lerini oluştur.
- [x] Veri formatlarını WP standartlarına uygun hale getir.

### Tasarım Görevleri
- [x] Tailwind CSS ile temel tasarımı oluştur. ✅ (Tamamlandı)
  - Modern admin panel arayüzü
  - Sidebar tasarımı
  - Tablo tasarımı
  - Responsive header
  - Pagination tasarımı

- [x] Responsive tasarımı sağla. ✅ (Tamamlandı)
  - Mobil uyumlu sidebar
  - Responsive tablo yapısı
  - Esnek grid sistem
  - Dinamik boyutlandırma

- [x] Renk paletini uygula. ✅ (Tamamlandı)
  - Primary: #00BCD4
  - Secondary: #f44336
  - Dark BG: #1a202c
  - Gri tonları
  - Hover efektleri

- [x] Remix Icon'ları entegre et. ✅ (Tamamlandı)
  - Sidebar modül ikonları
  - İşlem butonları ikonları
  - Header ikonları
  - Pagination ikonları

### Veri Modeli Görevleri
- [x] Kullanıcı modelini oluştur. ✅ (Tamamlandı)
  - Temel kullanıcı özellikleri
  - Rol yönetimi
  - Aktif/pasif durumu
  - Zaman damgaları

- [x] Diğer veri modellerini (slider, rapor, vb.) oluştur. ✅ (Tamamlandı)
  - Rapor modeli
  - Slider modeli
  - Kurumsal içerik modeli
  - Ekip üyeleri modeli
  - İK ilanları modeli
  - Hizmetler modeli
  - Projeler modeli

- [x] Veri validasyonunu sağla. ✅ (Tamamlandı)
  - Zorunlu alan kontrolleri
  - Format doğrulamaları
  - Özel validasyon kuralları
  - Hata yönetimi

### Geliştirme Ortamı Görevleri
- [x] PYTHON flask projesi oluştur. ✅ (Tamamlandı)
  - Proje yapısı oluşturuldu
  - Flask uygulaması başlatıldı
  - Konfigürasyon dosyası hazırlandı
  - Blueprint'ler tanımlandı

- [x] Tailwind CSS'i yapılandır. ✅ (Tamamlandı)
  - CDN entegrasyonu yapıldı
  - Özel renk paleti tanımlandı
  - Responsive tasarım ayarları yapıldı

- [x] Firebase SDK'sını entegre et. ✅ (Tamamlandı)
  - Firebase Admin SDK kuruldu
  - Firestore bağlantısı yapılandırıldı
  - Authentication entegrasyonu tamamlandı

- [x] Gerekli kütüphaneleri yükle. ✅ (Tamamlandı)
  - Flask ve eklentileri
  - Firebase Admin SDK
  - Diğer yardımcı kütüphaneler

# Proje Gereksinimleri

- [x] Proje için temel gereksinimler belirlendi. ✅ (Tamamlandı)
  - Modern bir CMS sistemi
  - Kullanıcı dostu arayüz
  - Hızlı ve güvenli performans
  - SEO dostu yapı
  - Çoklu dil desteği
  - Responsive tasarım

- [x] Geliştirme stack'i tanımlandı. ✅ (Tamamlandı)
  - Backend: Python Flask
    - Flask-Admin (Admin panel)
    - Flask-Login (Oturum yönetimi)
    - Flask-WTF (Form işlemleri)
    - Flask-Babel (Çoklu dil desteği)
  - Veritabanı: Firebase
    - Firestore (NoSQL veritabanı)
    - Authentication (Kullanıcı yönetimi)
    - Storage (Dosya depolama)
  - Frontend:
    - Jinja2 Templates
    - Tailwind CSS
    - Alpine.js (Minimal JavaScript)
    - Remix Icons
  - Deployment:
    - Firebase Hosting
    - Cloud Functions
    - Cloud Storage

- [x] Veri modeli oluşturuldu. ✅ (Tamamlandı)
  ```python
  # models.py
  from datetime import datetime
  from firebase_admin import firestore

  class User:
      def __init__(self, uid, username, email, role, created_at=None, updated_at=None):
          self.uid = uid
          self.username = username
          self.email = email
          self.role = role  # 'admin' | 'editor' | 'user'
          self.created_at = created_at or datetime.now()
          self.updated_at = updated_at or datetime.now()

      @staticmethod
      def from_dict(source):
          return User(
              uid=source['uid'],
              username=source['username'],
              email=source['email'],
              role=source['role'],
              created_at=source['created_at'],
              updated_at=source['updated_at']
          )

      def to_dict(self):
          return {
              'uid': self.uid,
              'username': self.username,
              'email': self.email,
              'role': self.role,
              'created_at': self.created_at,
              'updated_at': self.updated_at
          }

  class Page:
      def __init__(self, id, title, slug, content, status, author_id, created_at=None, updated_at=None):
          self.id = id
          self.title = title
          self.slug = slug
          self.content = content
          self.status = status  # 'draft' | 'published'
          self.author_id = author_id
          self.created_at = created_at or datetime.now()
          self.updated_at = updated_at or datetime.now()

  class Setting:
      def __init__(self, id, key, value, created_at=None, updated_at=None):
          self.id = id
          self.key = key
          self.value = value
          self.created_at = created_at or datetime.now()
          self.updated_at = updated_at or datetime.now()
  ```

## Firebase Konfigürasyonu

```python
# config.py
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-project-id.appspot.com'
})

db = firestore.client()
```

## Flask Uygulama Yapısı

```
project/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   └── main.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── admin/
│   │   └── auth/
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── config.py
├── requirements.txt
└── run.py
```

## Güvenlik Kuralları (Firestore)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId || hasRole('admin');
    }
    match /pages/{pageId} {
      allow read: if true;
      allow write: if hasRole('admin') || hasRole('editor');
    }
    match /settings/{settingId} {
      allow read: if true;
      allow write: if hasRole('admin');
    }
  }
}

function hasRole(role) {
  return request.auth != null && request.auth.token[role] == true;
}
```
