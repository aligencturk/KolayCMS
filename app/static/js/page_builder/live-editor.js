/**
 * KolayCMS Canlı Sayfa Düzenleyici
 * 
 * Bu sayfa düzenleyici, web sayfalarının görünümünü iframe içinde çalışan
 * bir WYSIWYG editör ile canlı olarak değiştirmeye olanak tanır.
 * Gelişmiş sürükle-bırak işlevselliği ile komponentleri kolayca ekleyebilir
 * ve konumlandırabilirsiniz.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Sayfa düzenleyici sınıfını başlat
  const editor = new LivePageEditor();
  editor.init();
});

/**
 * Canlı Sayfa Düzenleyici Ana Sınıfı
 */
class LivePageEditor {
  constructor() {
    // DOM Elemanları
    this.iframe = document.getElementById('page-preview');
    this.editorEl = document.getElementById('element-editor');
    this.noElementMessage = document.getElementById('no-element-message');
    this.elementPathEl = document.getElementById('element-path');
    this.notification = document.getElementById('editor-notification');
    this.componentLibraryEl = document.getElementById('component-library');
    
    // Tab sistemi
    this.tabs = document.querySelectorAll('.panel-tab');
    this.tabContents = document.querySelectorAll('.panel-tab-content');
    
    // Butonlar
    this.saveDraftBtn = document.getElementById('save-draft-btn');
    this.publishBtn = document.getElementById('publish-btn');
    this.toggleEditorBtn = document.getElementById('toggle-editor-btn');
    
    // Form alanları - Element özellikleri
    this.widthInput = document.getElementById('element-width');
    this.widthUnitSelect = document.getElementById('element-width-unit');
    this.heightInput = document.getElementById('element-height');
    this.heightUnitSelect = document.getElementById('element-height-unit');
    this.bgColorInput = document.getElementById('element-bg-color');
    this.bgColorPreview = document.getElementById('bg-color-preview');
    this.textColorInput = document.getElementById('element-text-color');
    this.textColorPreview = document.getElementById('text-color-preview');
    this.paddingTopInput = document.getElementById('element-padding-top');
    this.paddingRightInput = document.getElementById('element-padding-right');
    this.paddingBottomInput = document.getElementById('element-padding-bottom');
    this.paddingLeftInput = document.getElementById('element-padding-left');
    this.borderWidthInput = document.getElementById('element-border-width');
    this.borderStyleSelect = document.getElementById('element-border-style');
    this.borderColorInput = document.getElementById('element-border-color');
    this.borderRadiusInput = document.getElementById('element-border-radius');
    
    // Form alanları - Sayfa özellikleri
    this.pageBgColorInput = document.getElementById('page-bg-color');
    this.pageBgPreview = document.getElementById('page-bg-preview');
    this.containerWidthInput = document.getElementById('container-width');
    this.containerWidthUnitSelect = document.getElementById('container-width-unit');
    this.pageFontSelect = document.getElementById('page-font');
    
    // Düzenleyici durumu
    this.selectedElement = null;
    this.isEditorActive = true;
    this.styleCache = {}; // Değişiklikleri önbelleğe alma
    this.editingHistory = []; // Değişiklik geçmişi
    this.historyIndex = -1; // Geçmiş indeksi
    this.draggedComponent = null; // Sürüklenen komponent
    this.dropTarget = null; // Bırakma hedefi
    this.isDragging = false; // Sürükleme durumu
    
    // Sayfa/URL bilgileri
    this.pageId = this.getPageIdFromUrl();
    
    // Resize tutamaçları
    this.resizeHandles = [];
    
    // Komponent kütüphanesi
    this.components = {
      navbar: {
        name: 'Navbar',
        icon: 'fa-bars',
        html: `<nav class="navbar navbar-expand-lg navbar-light bg-light">
          <div class="container">
            <a class="navbar-brand" href="#">Logo</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
              <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
              <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                  <a class="nav-link active" href="#">Ana Sayfa</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">Hakkımızda</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">Hizmetler</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">İletişim</a>
                </li>
              </ul>
            </div>
          </div>
        </nav>`
      },
      header: {
        name: 'Başlık Bölümü',
        icon: 'fa-heading',
        html: `<header class="py-5 bg-primary text-white text-center">
          <div class="container">
            <h1>Web Sitenize Hoşgeldiniz</h1>
            <p class="lead">Modern ve profesyonel bir web sitesi için doğru yerdesiniz</p>
            <button class="btn btn-light">Daha Fazla</button>
          </div>
        </header>`
      },
      blogCard: {
        name: 'Blog Kartı',
        icon: 'fa-newspaper',
        html: `<div class="card mb-4">
          <img src="https://via.placeholder.com/300x200" class="card-img-top" alt="Blog Görsel">
          <div class="card-body">
            <h5 class="card-title">Blog Başlığı</h5>
            <p class="card-text">Blog içeriği burada yer alacak. İçeriğinizi kendi ihtiyaçlarınıza göre düzenleyebilirsiniz.</p>
            <a href="#" class="btn btn-primary">Devamını Oku</a>
          </div>
          <div class="card-footer text-muted">
            2 gün önce paylaşıldı
          </div>
        </div>`
      },
      serviceCard: {
        name: 'Hizmet Kartı',
        icon: 'fa-cogs',
        html: `<div class="card text-center mb-4">
          <div class="card-body">
            <i class="fas fa-cogs fa-3x mb-3 text-primary"></i>
            <h4 class="card-title">Hizmet Adı</h4>
            <p class="card-text">Hizmet açıklaması burada yer alacak. Kendi hizmet açıklamanızı ekleyebilirsiniz.</p>
            <a href="#" class="btn btn-outline-primary">Detaylar</a>
          </div>
        </div>`
      },
      contactForm: {
        name: 'İletişim Formu',
        icon: 'fa-envelope',
        html: `<div class="card p-4 mb-4">
          <h4 class="mb-3">Bize Ulaşın</h4>
          <form>
            <div class="mb-3">
              <label for="name" class="form-label">Ad Soyad</label>
              <input type="text" class="form-control" id="name">
            </div>
            <div class="mb-3">
              <label for="email" class="form-label">E-posta</label>
              <input type="email" class="form-control" id="email">
            </div>
            <div class="mb-3">
              <label for="message" class="form-label">Mesaj</label>
              <textarea class="form-control" id="message" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Gönder</button>
          </form>
        </div>`
      }
    };
  }
  
  /**
   * URL'den sayfa ID'sini al
   */
  getPageIdFromUrl() {
    const urlPath = window.location.pathname;
    const parts = urlPath.split('/');
    return parts[parts.length - 1];
  }
  
  /**
   * Düzenleyiciyi başlat
   */
  init() {
    // iframe hazır olduğunda
    this.iframe.addEventListener('load', () => {
      this.setupIframeEditor();
    });
    
    // Tab değiştirme işlevselliği
    this.tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        this.changeTab(tab.dataset.tab);
      });
    });
    
    // Renk değiştiriciler
    this.setupColorPickers();
    
    // Komponent kütüphanesini yükle
    this.loadComponentLibrary();
    
    // Sürükle-bırak yönetimi
    this.setupDragAndDrop();
  }
  
  /**
   * Komponent kütüphanesini yükle
   */
  loadComponentLibrary() {
    if (!this.componentLibraryEl) return;
    
    // Kütüphaneyi temizle
    this.componentLibraryEl.innerHTML = '';
    
    // Her komponent için bir kart oluştur
    Object.keys(this.components).forEach(key => {
      const component = this.components[key];
      
      const componentEl = document.createElement('div');
      componentEl.className = 'component-item';
      componentEl.dataset.componentType = key;
      componentEl.draggable = true;
      
      componentEl.innerHTML = `
        <div class="component-icon">
          <i class="fas ${component.icon}"></i>
        </div>
        <div class="component-name">${component.name}</div>
      `;
      
      this.componentLibraryEl.appendChild(componentEl);
    });
  }
  
  /**
   * Sürükle-bırak işlevselliğini kur
   */
  setupDragAndDrop() {
    // Komponent kütüphanesi elemanlarını sürüklenebilir yap
    if (this.componentLibraryEl) {
      const componentItems = this.componentLibraryEl.querySelectorAll('.component-item');
      
      componentItems.forEach(item => {
        item.addEventListener('dragstart', e => {
          this.handleDragStart(e, item);
        });
        
        item.addEventListener('dragend', e => {
          this.handleDragEnd(e);
        });
      });
    }
  }
  
  /**
   * Iframe içindeki düzenleyiciyi ayarla
   */
  setupIframeEditor() {
    const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
    const iframeWin = this.iframe.contentWindow;
    
    // iframe sayfasına stil ekleyelim - düzenlenebilir öğeleri gösterme
    const editorStyle = iframeDoc.createElement('style');
    editorStyle.textContent = `
      .kolaycms-selectable {
        cursor: pointer;
        transition: outline 0.2s;
      }
      .kolaycms-selectable:hover {
        outline: 2px solid rgba(0, 188, 212, 0.5);
      }
      .kolaycms-selected {
        outline: 2px solid rgba(0, 188, 212, 0.8) !important;
        position: relative;
        z-index: 1;
      }
    `;
    iframeDoc.head.appendChild(editorStyle);
    
    // Düzenlenebilir öğeleri işaretle
    this.makeElementsSelectable(iframeDoc);
    
    // Element seçim olayları
    iframeDoc.addEventListener('click', (e) => {
      // Eğer düzenleme modu aktifse
      if (this.isEditorActive) {
        // Tıklanan öğeyi veya ebeveynini bul
        const element = this.findSelectableElement(e.target);
        
        if (element) {
          e.preventDefault();
          e.stopPropagation();
          this.selectElement(element);
        }
      }
    });
    
    // Sayfa içerisinde bırakma bölgelerini tanımla
    this.setupDropZones(iframeDoc);
    
    // Düzenlenebilir içerik ayarları
    this.setupEditableContent(iframeDoc);
  }
  
  /**
   * Düzenlenebilir içerik ayarları
   */
  setupEditableContent(doc) {
    const editableElements = doc.querySelectorAll('[data-editable="true"]');
    
    editableElements.forEach(el => {
      el.contentEditable = true;
      
      el.addEventListener('focus', () => {
        this.selectElement(el);
      });
      
      el.addEventListener('blur', () => {
        // İçerik değişikliklerini kaydet
        this.saveElementChanges();
      });
    });
  }
  
  /**
   * Bırakma bölgelerini ayarla
   */
  setupDropZones(doc) {
    // Potansiyel drop bölgelerini tanımla - container divler, section'lar vb.
    const dropZones = doc.querySelectorAll('.container, .container-fluid, section, .row, [data-drop-zone="true"]');
    
    dropZones.forEach(zone => {
      // Sürüklenen öğeler için olayları tanımla
      zone.addEventListener('dragover', e => {
        this.handleDragOver(e, zone);
      });
      
      zone.addEventListener('dragleave', e => {
        this.handleDragLeave(e, zone);
      });
      
      zone.addEventListener('drop', e => {
        this.handleDrop(e, zone);
      });
    });
  }
  
  /**
   * Sürükleme başladığında
   */
  handleDragStart(e, item) {
    this.isDragging = true;
    this.draggedComponent = item.dataset.componentType;
    
    // Sürükleme verilerini ayarla
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('text/plain', this.draggedComponent);
    
    // Sürükleme görsel geribildirimi
    setTimeout(() => {
      item.classList.add('dragging');
    }, 0);
  }
  
  /**
   * Sürükleme bittiğinde
   */
  handleDragEnd(e) {
    this.isDragging = false;
    
    // Sürükleme görseli temizle
    const items = document.querySelectorAll('.component-item');
    items.forEach(item => item.classList.remove('dragging'));
    
    // Drop hedefindeki vurgu efektini kaldır
    if (this.dropTarget) {
      this.dropTarget.classList.remove('drop-highlight');
      this.dropTarget = null;
    }
  }
  
  /**
   * Sürüklenen öğe potansiyel bırakma bölgesi üzerinde
   */
  handleDragOver(e, zone) {
    // Varsayılan olayı engelle - drop'a izin vermek için
    e.preventDefault();
    
    // Bırakma efekti belirle
    e.dataTransfer.dropEffect = 'copy';
    
    // Daha önce bir hedef varsa, vurguyu kaldır
    if (this.dropTarget && this.dropTarget !== zone) {
      this.dropTarget.classList.remove('drop-highlight');
    }
    
    // Mevcut hedefi vurgula
    zone.classList.add('drop-highlight');
    this.dropTarget = zone;
  }
  
  /**
   * Sürüklenen öğe bırakma bölgesinden ayrıldığında
   */
  handleDragLeave(e, zone) {
    // Fare gerçekten bölgeden çıktığında vurguyu kaldır
    // İç elemanlar arası geçişte gereksiz tetiklenme olabilir
    const relatedTarget = e.relatedTarget;
    if (!zone.contains(relatedTarget)) {
      zone.classList.remove('drop-highlight');
      if (this.dropTarget === zone) {
        this.dropTarget = null;
      }
    }
  }
  
  /**
   * Öğe bırakıldığında
   */
  handleDrop(e, zone) {
    // Varsayılan olayı engelle
    e.preventDefault();
    e.stopPropagation();
    
    // Bırakma hedefindeki vurgu efektini kaldır
    zone.classList.remove('drop-highlight');
    
    // Bırakılan komponenti al
    const componentType = e.dataTransfer.getData('text/plain');
    
    // Komponent var mı kontrol et
    if (this.components[componentType]) {
      this.addComponentToPage(componentType, zone);
    }
    
    // Temizlik
    this.dropTarget = null;
    this.draggedComponent = null;
  }
  
  /**
   * Sayfaya komponent ekle
   */
  addComponentToPage(componentType, targetElement) {
    const component = this.components[componentType];
    const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
    
    // Komponent için konteyner oluştur
    const container = iframeDoc.createElement('div');
    container.className = 'cms-component';
    container.dataset.componentType = componentType;
    container.innerHTML = component.html;
    
    // Komponenti hedef elemana ekle
    targetElement.appendChild(container);
    
    // Yeni eklenen komponenti aktif et
    this.makeElementsSelectable(iframeDoc);
    this.selectElement(container);
    
    // Komponenti seçili yap
    this.showNotification(`${component.name} başarıyla eklendi.`, 'success');
    
    // Sayfada değişiklik yapıldı
    this.savePageChanges();
  }
  
  /**
   * Sayfa değişikliklerini kaydet
   */
  savePageChanges() {
    // Sayfa durumunu kaydet
    this.editingHistory.push({
      html: this.iframe.contentDocument.body.innerHTML,
      timestamp: new Date()
    });
    
    // Geçmiş indeksini güncelle
    this.historyIndex = this.editingHistory.length - 1;
    
    // Kaydetme butonunu aktive et
    if (this.saveDraftBtn) {
      this.saveDraftBtn.disabled = false;
    }
  }
  
  /**
   * iframe içindeki öğelere düzenlenebilir class'ı ekle
   */
  makeElementsSelectable(doc) {
    // Düzenlenebilir öğeler listesi - bunu tercihlerinize göre değiştirin
    const selectableSelector = 'div, section, nav, header, footer, main, aside, article, p, h1, h2, h3, h4, h5, h6, button, a';
    
    // Gövde içindeki seçilebilir öğeleri işaretle
    const selectables = doc.querySelectorAll(selectableSelector);
    
    selectables.forEach(el => {
      // Bazı öğeleri hariç tutabiliriz (örn: vücut, baş, komut dosyası, meta)
      if (el.tagName !== 'BODY' && el.tagName !== 'HTML' && el.tagName !== 'HEAD' && el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE') {
        el.classList.add('kolaycms-selectable');
        
        // Her öğeye benzersiz bir id ekle (yoksa)
        if (!el.id) {
          el.id = 'kolaycms-element-' + Math.random().toString(36).substr(2, 9);
        }
      }
    });
  }
  
  /**
   * Tıklanan veya parent'ında düzenlenebilir bir element bul
   */
  findSelectableElement(element) {
    let currentElement = element;
    
    // Selectable bir eleman bulana veya body'ye ulaşana kadar yukarı çık
    while (currentElement && currentElement !== document.body) {
      if (currentElement.classList && currentElement.classList.contains('kolaycms-selectable')) {
        return currentElement;
      }
      currentElement = currentElement.parentElement;
    }
    
    return null;
  }
  
  /**
   * Element seç ve düzenleme panelini aç
   */
  selectElement(element) {
    const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
    
    // Önceki seçili elementi temizle
    if (this.selectedElement) {
      this.selectedElement.classList.remove('kolaycms-selected');
      this.removeResizeHandles();
    }
    
    // Yeni elementi seç
    element.classList.add('kolaycms-selected');
    this.selectedElement = element;
    
    // Element path bilgisini göster
    this.updateElementPath(element);
    
    // Element özelliklerini panele yükle
    this.loadElementProperties(element);
    
    // Gösterge panelini göster
    this.noElementMessage.style.display = 'none';
    this.editorEl.style.display = 'block';
    
    // Yeniden boyutlandırma tutamaçlarını ekle
    this.addResizeHandles(element);
  }
  
  /**
   * Element seçim yolunu göster
   */
  updateElementPath(element) {
    let path = '';
    let currentElement = element;
    
    // Selectable bir eleman bulana veya body'ye ulaşana kadar yukarı çık
    while (currentElement && currentElement !== document.body) {
      const tagName = currentElement.tagName.toLowerCase();
      const id = currentElement.id ? `#${currentElement.id}` : '';
      const classes = currentElement.classList ? 
        Array.from(currentElement.classList)
          .filter(cls => cls !== 'kolaycms-selectable' && cls !== 'kolaycms-selected')
          .map(cls => `.${cls}`)
          .join('') : '';
      
      path = `<span class="text-primary">${tagName}</span>${id}${classes} > ${path}`;
      
      currentElement = currentElement.parentElement;
    }
    
    this.elementPathEl.innerHTML = path ? path.slice(0, -3) : ''; // Son '> ' karakterini kaldır
  }
  
  /**
   * Element özelliklerini panele yükle
   */
  loadElementProperties(element) {
    const styles = getComputedStyle(element);
    
    // Boyut özellikleri
    const width = styles.width;
    const height = styles.height;
    
    this.widthInput.value = this.parseSize(width).value;
    this.widthUnitSelect.value = this.parseSize(width).unit;
    
    this.heightInput.value = this.parseSize(height).value;
    this.heightUnitSelect.value = this.parseSize(height).unit;
    
    // Renk özellikleri
    const bgColor = styles.backgroundColor;
    const textColor = styles.color;
    
    this.bgColorInput.value = this.rgbToHex(bgColor);
    this.bgColorPreview.style.backgroundColor = bgColor;
    
    this.textColorInput.value = this.rgbToHex(textColor);
    this.textColorPreview.style.backgroundColor = textColor;
    
    // Padding (kenar boşluğu)
    this.paddingTopInput.value = parseInt(styles.paddingTop);
    this.paddingRightInput.value = parseInt(styles.paddingRight);
    this.paddingBottomInput.value = parseInt(styles.paddingBottom);
    this.paddingLeftInput.value = parseInt(styles.paddingLeft);
    
    // Border (kenarlık)
    this.borderWidthInput.value = parseInt(styles.borderWidth);
    this.borderStyleSelect.value = styles.borderStyle;
    this.borderColorInput.value = this.rgbToHex(styles.borderColor);
    
    // Border radius (köşe yuvarlaklığı)
    this.borderRadiusInput.value = parseInt(styles.borderRadius);
  }
  
  /**
   * Element üzerine yeniden boyutlandırma tutamaçları ekle
   */
  addResizeHandles(element) {
    const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
    const rect = element.getBoundingClientRect();
    
    // Tutamaç pozisyonları
    const positions = [
      { class: 'top-left', x: 0, y: 0 },
      { class: 'top-right', x: rect.width, y: 0 },
      { class: 'bottom-left', x: 0, y: rect.height },
      { class: 'bottom-right', x: rect.width, y: rect.height },
      { class: 'top', x: rect.width / 2, y: 0 },
      { class: 'bottom', x: rect.width / 2, y: rect.height },
      { class: 'left', x: 0, y: rect.height / 2 },
      { class: 'right', x: rect.width, y: rect.height / 2 }
    ];
    
    positions.forEach(pos => {
      const handle = iframeDoc.createElement('div');
      handle.classList.add('resize-handle', pos.class);
      handle.style.position = 'absolute';
      handle.style.width = '10px';
      handle.style.height = '10px';
      handle.style.background = '#00BCD4';
      handle.style.borderRadius = '50%';
      handle.style.zIndex = '9999';
      handle.style.left = `${pos.x - 5}px`;
      handle.style.top = `${pos.y - 5}px`;
      
      // Tutamaçları isteğe göre konumlandır
      switch(pos.class) {
        case 'top-left':
          handle.style.cursor = 'nwse-resize';
          break;
        case 'top-right':
          handle.style.cursor = 'nesw-resize';
          break;
        case 'bottom-left':
          handle.style.cursor = 'nesw-resize';
          break;
        case 'bottom-right':
          handle.style.cursor = 'nwse-resize';
          break;
        case 'top':
        case 'bottom':
          handle.style.cursor = 'ns-resize';
          break;
        case 'left':
        case 'right':
          handle.style.cursor = 'ew-resize';
          break;
      }
      
      // Tutamaç sürükleme olaylarını ekle
      this.addResizeEvents(handle, pos.class);
      
      // Seçili elementin üzerine ekle
      element.appendChild(handle);
      this.resizeHandles.push(handle);
    });
  }
  
  /**
   * Tutamaçlara sürükleme olayları ekle
   */
  addResizeEvents(handle, position) {
    let startX, startY, startWidth, startHeight;
    const element = this.selectedElement;
    
    const onMouseDown = (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      startX = e.clientX;
      startY = e.clientY;
      
      const styles = getComputedStyle(element);
      startWidth = parseInt(styles.width);
      startHeight = parseInt(styles.height);
      
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
      
      iframeDoc.addEventListener('mousemove', onMouseMove);
      iframeDoc.addEventListener('mouseup', onMouseUp);
    };
    
    const onMouseMove = (e) => {
      e.preventDefault();
      
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      
      let newWidth = startWidth;
      let newHeight = startHeight;
      
      // Tutamaç pozisyonuna göre boyutlandırma
      switch(position) {
        case 'right':
        case 'top-right':
        case 'bottom-right':
          newWidth = startWidth + deltaX;
          break;
        case 'left':
        case 'top-left':
        case 'bottom-left':
          newWidth = startWidth - deltaX;
          break;
      }
      
      switch(position) {
        case 'bottom':
        case 'bottom-left':
        case 'bottom-right':
          newHeight = startHeight + deltaY;
          break;
        case 'top':
        case 'top-left':
        case 'top-right':
          newHeight = startHeight - deltaY;
          break;
      }
      
      // Minimum boyut kontrolü
      if (newWidth < 20) newWidth = 20;
      if (newHeight < 20) newHeight = 20;
      
      // Elementin boyutunu güncelle
      element.style.width = `${newWidth}px`;
      element.style.height = `${newHeight}px`;
      
      // Tutamaç pozisyonlarını güncelle
      this.removeResizeHandles();
      this.addResizeHandles(element);
      
      // Form değerlerini güncelle
      this.widthInput.value = newWidth;
      this.heightInput.value = newHeight;
    };
    
    const onMouseUp = () => {
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
      
      iframeDoc.removeEventListener('mousemove', onMouseMove);
      iframeDoc.removeEventListener('mouseup', onMouseUp);
      
      // Değişikliği kaydet
      this.saveElementChanges();
    };
    
    handle.addEventListener('mousedown', onMouseDown);
  }
  
  /**
   * Resize tutamaçlarını kaldır
   */
  removeResizeHandles() {
    this.resizeHandles.forEach(handle => {
      if (handle.parentNode) {
        handle.parentNode.removeChild(handle);
      }
    });
    
    this.resizeHandles = [];
  }
  
  /**
   * Renk seçicileri hazırla
   */
  setupColorPickers() {
    // Arka plan rengi değiştiğinde
    this.bgColorInput.addEventListener('input', () => {
      const color = this.bgColorInput.value;
      this.bgColorPreview.style.backgroundColor = color;
      
      if (this.selectedElement) {
        this.selectedElement.style.backgroundColor = color;
        this.saveElementChanges();
      }
    });
    
    // Yazı rengi değiştiğinde
    this.textColorInput.addEventListener('input', () => {
      const color = this.textColorInput.value;
      this.textColorPreview.style.backgroundColor = color;
      
      if (this.selectedElement) {
        this.selectedElement.style.color = color;
        this.saveElementChanges();
      }
    });
    
    // Sayfa arka plan rengi değiştiğinde
    this.pageBgColorInput.addEventListener('input', () => {
      const color = this.pageBgColorInput.value;
      this.pageBgPreview.style.backgroundColor = color;
      
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
      iframeDoc.body.style.backgroundColor = color;
      
      this.savePageStyles();
    });
  }
  
  /**
   * Form alanları için olay dinleyicileri
   */
  setupFormEventListeners() {
    // Genişlik değişimi
    this.widthInput.addEventListener('change', () => {
      if (this.selectedElement) {
        const value = this.widthInput.value;
        const unit = this.widthUnitSelect.value;
        this.selectedElement.style.width = `${value}${unit}`;
        this.saveElementChanges();
      }
    });
    
    this.widthUnitSelect.addEventListener('change', () => {
      if (this.selectedElement) {
        const value = this.widthInput.value;
        const unit = this.widthUnitSelect.value;
        this.selectedElement.style.width = `${value}${unit}`;
        this.saveElementChanges();
      }
    });
    
    // Yükseklik değişimi
    this.heightInput.addEventListener('change', () => {
      if (this.selectedElement) {
        const value = this.heightInput.value;
        const unit = this.heightUnitSelect.value;
        this.selectedElement.style.height = `${value}${unit}`;
        this.saveElementChanges();
      }
    });
    
    this.heightUnitSelect.addEventListener('change', () => {
      if (this.selectedElement) {
        const value = this.heightInput.value;
        const unit = this.heightUnitSelect.value;
        this.selectedElement.style.height = `${value}${unit}`;
        this.saveElementChanges();
      }
    });
    
    // Padding değişimi
    this.paddingTopInput.addEventListener('change', () => {
      if (this.selectedElement) {
        this.selectedElement.style.paddingTop = `${this.paddingTopInput.value}px`;
        this.saveElementChanges();
      }
    });
    
    this.paddingRightInput.addEventListener('change', () => {
      if (this.selectedElement) {
        this.selectedElement.style.paddingRight = `${this.paddingRightInput.value}px`;
        this.saveElementChanges();
      }
    });
    
    this.paddingBottomInput.addEventListener('change', () => {
      if (this.selectedElement) {
        this.selectedElement.style.paddingBottom = `${this.paddingBottomInput.value}px`;
        this.saveElementChanges();
      }
    });
    
    this.paddingLeftInput.addEventListener('change', () => {
      if (this.selectedElement) {
        this.selectedElement.style.paddingLeft = `${this.paddingLeftInput.value}px`;
        this.saveElementChanges();
      }
    });
    
    // Border değişimi
    this.borderWidthInput.addEventListener('change', () => {
      if (this.selectedElement) {
        this.updateBorder();
      }
    });
    
    this.borderStyleSelect.addEventListener('change', () => {
      if (this.selectedElement) {
        this.updateBorder();
      }
    });
    
    this.borderColorInput.addEventListener('input', () => {
      if (this.selectedElement) {
        this.updateBorder();
      }
    });
    
    // Border radius değişimi
    this.borderRadiusInput.addEventListener('change', () => {
      if (this.selectedElement) {
        this.selectedElement.style.borderRadius = `${this.borderRadiusInput.value}px`;
        this.saveElementChanges();
      }
    });
    
    // Sayfa stili değişimi
    this.containerWidthInput.addEventListener('change', () => {
      const value = this.containerWidthInput.value;
      const unit = this.containerWidthUnitSelect.value;
      
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
      const containers = iframeDoc.querySelectorAll('.container'); // sayfadaki container sınıflı öğeler
      
      containers.forEach(container => {
        container.style.maxWidth = `${value}${unit}`;
      });
      
      this.savePageStyles();
    });
    
    this.containerWidthUnitSelect.addEventListener('change', () => {
      const value = this.containerWidthInput.value;
      const unit = this.containerWidthUnitSelect.value;
      
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
      const containers = iframeDoc.querySelectorAll('.container');
      
      containers.forEach(container => {
        container.style.maxWidth = `${value}${unit}`;
      });
      
      this.savePageStyles();
    });
    
    this.pageFontSelect.addEventListener('change', () => {
      const fontFamily = this.pageFontSelect.value;
      
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
      iframeDoc.body.style.fontFamily = fontFamily;
      
      this.savePageStyles();
    });
  }
  
  /**
   * Border stilini güncelle
   */
  updateBorder() {
    const width = this.borderWidthInput.value;
    const style = this.borderStyleSelect.value;
    const color = this.borderColorInput.value;
    
    this.selectedElement.style.borderWidth = `${width}px`;
    this.selectedElement.style.borderStyle = style;
    this.selectedElement.style.borderColor = color;
    
    this.saveElementChanges();
  }
  
  /**
   * Buton olaylarını ayarla
   */
  setupButtonListeners() {
    // Taslak kaydet butonu
    this.saveDraftBtn.addEventListener('click', () => {
      this.savePage(false);
    });
    
    // Yayınla butonu
    this.publishBtn.addEventListener('click', () => {
      this.savePage(true);
    });
    
    // Editör geçiş butonu
    this.toggleEditorBtn.addEventListener('click', () => {
      this.toggleEditorMode();
    });
  }
  
  /**
   * Tab değiştir
   */
  changeTab(tabId) {
    // Tüm tabları ve içeriklerini kontrol et
    this.tabs.forEach(tab => {
      if (tab.dataset.tab === tabId) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    
    this.tabContents.forEach(content => {
      if (content.id === `${tabId}-panel`) {
        content.style.display = 'block';
      } else {
        content.style.display = 'none';
      }
    });
  }
  
  /**
   * Editör modunu değiştir (önizleme/düzenleme)
   */
  toggleEditorMode() {
    this.isEditorActive = !this.isEditorActive;
    
    // iframe içindeki stilleri güncelle
    const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
    const selectables = iframeDoc.querySelectorAll('.kolaycms-selectable');
    
    if (this.isEditorActive) {
      // Düzenleme moduna geri dön
      selectables.forEach(el => {
        el.classList.remove('kolaycms-hidden');
      });
      
      this.toggleEditorBtn.innerHTML = '<i class="ri-eye-line mr-1"></i> Önizleme';
    } else {
      // Önizleme moduna geç
      selectables.forEach(el => {
        el.classList.add('kolaycms-hidden');
      });
      
      // Seçimi ve tutamaçları temizle
      if (this.selectedElement) {
        this.selectedElement.classList.remove('kolaycms-selected');
        this.removeResizeHandles();
        this.selectedElement = null;
      }
      
      this.noElementMessage.style.display = 'block';
      this.editorEl.style.display = 'none';
      
      this.toggleEditorBtn.innerHTML = '<i class="ri-edit-line mr-1"></i> Düzenle';
    }
  }
  
  /**
   * Element değişikliklerini kaydet
   */
  saveElementChanges() {
    if (!this.selectedElement) return;
    
    // Seçili elementi yeniden oluştur
    this.removeResizeHandles();
    this.addResizeHandles(this.selectedElement);
    
    // Değişiklikleri sakla
    const elementId = this.selectedElement.id;
    const styles = {
      width: this.selectedElement.style.width,
      height: this.selectedElement.style.height,
      backgroundColor: this.selectedElement.style.backgroundColor,
      color: this.selectedElement.style.color,
      paddingTop: this.selectedElement.style.paddingTop,
      paddingRight: this.selectedElement.style.paddingRight,
      paddingBottom: this.selectedElement.style.paddingBottom,
      paddingLeft: this.selectedElement.style.paddingLeft,
      borderWidth: this.selectedElement.style.borderWidth,
      borderStyle: this.selectedElement.style.borderStyle,
      borderColor: this.selectedElement.style.borderColor,
      borderRadius: this.selectedElement.style.borderRadius
    };
    
    // Cache'e ekle
    this.styleCache[elementId] = styles;
  }
  
  /**
   * Sayfa stillerini kaydet
   */
  savePageStyles() {
    const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;
    
    const pageStyles = {
      bodyBgColor: iframeDoc.body.style.backgroundColor,
      bodyFontFamily: iframeDoc.body.style.fontFamily
    };
    
    // Container stillerini ekle
    const containers = iframeDoc.querySelectorAll('.container');
    if (containers.length > 0) {
      pageStyles.containerMaxWidth = containers[0].style.maxWidth;
    }
    
    // Özel stil sayfası olarak ekle/güncelle
    let styleElement = iframeDoc.getElementById('kolaycms-custom-styles');
    
    if (!styleElement) {
      styleElement = iframeDoc.createElement('style');
      styleElement.id = 'kolaycms-custom-styles';
      iframeDoc.head.appendChild(styleElement);
    }
    
    styleElement.textContent = `
      body {
        background-color: ${pageStyles.bodyBgColor || ''};
        font-family: ${pageStyles.bodyFontFamily || ''};
      }
      
      .container {
        max-width: ${pageStyles.containerMaxWidth || ''};
      }
    `;
    
    // Cache'e ekle
    this.styleCache['page'] = pageStyles;
  }
  
  /**
   * Tüm değişiklikleri kaydet
   */
  savePage(isPublished) {
    // Sayfa stillerini güncelle (sayfa elementleri değişmiş olabilir)
    this.savePageStyles();
    
    // Bildirim göster
    this.showNotification('Değişiklikler kaydediliyor...', 'info');
    
    // API'ye gönderilecek veri
    const data = {
      page_id: this.pageId,
      element_styles: this.styleCache,
      is_published: isPublished
    };
    
    // API çağrısı
    fetch('/page-builder/api/save-styles', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCsrfToken()
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        this.showNotification(
          isPublished ? 'Sayfa başarıyla yayınlandı!' : 'Taslak başarıyla kaydedildi!',
          'success'
        );
      } else {
        this.showNotification('Hata: ' + (result.error || 'Bilinmeyen hata'), 'error');
      }
    })
    .catch(error => {
      this.showNotification('İstek hatası: ' + error.message, 'error');
    });
  }
  
  /**
   * Mesaj göster
   */
  showNotification(message, type = 'info') {
    this.notification.textContent = message;
    this.notification.className = 'editor-notification';
    this.notification.classList.add(type);
    this.notification.classList.add('show');
    
    setTimeout(() => {
      this.notification.classList.remove('show');
    }, 3000);
  }
  
  /**
   * RGB rengi Hex'e dönüştür
   */
  rgbToHex(rgb) {
    // rgb(r, g, b) veya rgba(r, g, b, a) formatından dönüştür
    if (!rgb || rgb === 'transparent' || rgb === 'rgba(0, 0, 0, 0)') {
      return '#ffffff';
    }
    
    const rgbRegex = /rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)/;
    const match = rgb.match(rgbRegex);
    
    if (!match) {
      return rgb; // Halihazırda hex veya tanınmayan format ise aynı geri döndür
    }
    
    const r = parseInt(match[1]);
    const g = parseInt(match[2]);
    const b = parseInt(match[3]);
    
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  }
  
  /**
   * Boyut değerini parse et (örn. "100px" -> {value: 100, unit: "px"})
   */
  parseSize(sizeStr) {
    const defaultResult = { value: 0, unit: 'px' };
    
    if (!sizeStr) return defaultResult;
    
    // Sayı ve birimi ayır
    const match = sizeStr.match(/^(\d+(?:\.\d+)?)([a-z%]+)$/);
    
    if (match) {
      return {
        value: parseFloat(match[1]),
        unit: match[2]
      };
    }
    
    // Eğer sadece sayı ise piksel olarak kabul et
    if (!isNaN(parseFloat(sizeStr))) {
      return {
        value: parseFloat(sizeStr),
        unit: 'px'
      };
    }
    
    return defaultResult;
  }
  
  /**
   * CSRF token al
   */
  getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  }
} 