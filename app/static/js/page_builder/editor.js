/**
 * KolayCMS Sürükle Bırak Sayfa Düzenleyici
 * 
 * Bu dosya, sayfa yapılandırma düzenleyicisinin temel işlevselliğini sağlar.
 * Gridstack.js kütüphanesini kullanarak sayfa elemanlarının sürüklenip bırakılmasını destekler.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Sayfa ID'sini al
  const pageId = document.getElementById('page-editor').dataset.pageId;
  
  // Gridstack yapılandırması
  const grid = GridStack.init({
    column: 12,
    cellHeight: 60,
    animate: true,
    float: true,
    resizable: {
      handles: 'e, se, s, sw, w'
    },
    draggable: {
      handle: '.element-drag-handle'
    }
  });
  
  // Elemanlar yer değiştirdiğinde güncelle
  grid.on('change', function(event, items) {
    // Pozisyon değişikliklerini topla
    const updates = items.map(item => {
      return {
        id: item.id,
        position: {
          x: item.x,
          y: item.y,
          width: item.w,
          height: item.h
        }
      };
    });
    
    // Düzen değişikliğini kaydet
    saveLayout(updates);
  });
  
  // Elem şablonları için sürükle-bırak işlevselliği
  document.querySelectorAll('.element-template').forEach(template => {
    template.addEventListener('dragstart', function(e) {
      e.dataTransfer.setData('element-type', this.dataset.elementType);
    });
  });
  
  // Düzenleyici alanına eleman bırakılınca
  document.getElementById('grid-container').addEventListener('drop', function(e) {
    e.preventDefault();
    const elementType = e.dataTransfer.getData('element-type');
    if (elementType) {
      createNewElement(elementType, e.clientX, e.clientY);
    }
  });
  
  document.getElementById('grid-container').addEventListener('dragover', function(e) {
    e.preventDefault(); // Drop olayının gerçekleşmesi için
  });
  
  // Şablon değiştirme modalı
  const templateModal = document.getElementById('template-modal');
  const selectTemplateBtn = document.getElementById('select-template-btn');
  
  if (selectTemplateBtn) {
    selectTemplateBtn.addEventListener('click', function() {
      templateModal.classList.remove('hidden');
    });
  }
  
  // Şablon seçimini uygula
  document.querySelectorAll('.select-template').forEach(btn => {
    btn.addEventListener('click', function() {
      const templateId = this.dataset.templateId;
      setPageTemplate(templateId);
      templateModal.classList.add('hidden');
    });
  });
  
  // Eleman düzenleme modalı
  const elementModal = document.getElementById('element-modal');
  const elementForm = document.getElementById('element-form');
  let currentElementId = null;
  
  // Sayfa yüklendiğinde elemanları getir
  fetchElements();
  
  // Eleman düzenle butonları için olay dinleyicisi (delegasyon)
  document.addEventListener('click', function(e) {
    if (e.target && e.target.classList.contains('edit-element-btn')) {
      const elementId = e.target.closest('.grid-stack-item').getAttribute('gs-id');
      openElementEditor(elementId);
    }
    
    if (e.target && e.target.classList.contains('delete-element-btn')) {
      const elementId = e.target.closest('.grid-stack-item').getAttribute('gs-id');
      deleteElement(elementId);
    }
  });
  
  // Modal kapatma düğmeleri
  document.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', function() {
      this.closest('.modal').classList.add('hidden');
    });
  });
  
  // Eleman form gönderimi
  if (elementForm) {
    elementForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const data = {
        title: formData.get('element-title'),
        content: {
          text: formData.get('element-content'),
          // Diğer içerik alanları element tipine göre eklenebilir
        },
        style: {
          backgroundColor: formData.get('element-bg-color'),
          textColor: formData.get('element-text-color'),
          padding: formData.get('element-padding'),
          borderRadius: formData.get('element-border-radius')
        }
      };
      
      if (currentElementId) {
        // Mevcut elemanı güncelle
        updateElement(currentElementId, data);
      }
      
      elementModal.classList.add('hidden');
    });
  }
  
  // ---- API İşlevleri ----
  
  // Elemanları getir
  function fetchElements() {
    fetch(`/page-builder/api/elements?page_id=${pageId}`)
      .then(response => response.json())
      .then(elements => {
        renderElements(elements);
      })
      .catch(error => {
        console.error('Elemanlar getirilirken hata oluştu:', error);
        showNotification('Elemanlar yüklenirken bir hata oluştu.', 'error');
      });
  }
  
  // Elemanları render et
  function renderElements(elements) {
    // Önce grid'i temizle
    grid.removeAll();
    
    // Her bir elemanı ekle
    elements.forEach(element => {
      const pos = element.position || { x: 0, y: 0, width: 6, height: 2 };
      
      // HTML içeriği oluştur
      const content = `
        <div class="element-content" style="${getStyleString(element.style)}">
          <div class="element-header">
            <div class="element-drag-handle">
              <i class="ri-drag-move-line"></i>
            </div>
            <div class="element-title">${element.title}</div>
            <div class="element-actions">
              <button class="edit-element-btn" title="Düzenle">
                <i class="ri-edit-line"></i>
              </button>
              <button class="delete-element-btn" title="Sil">
                <i class="ri-delete-bin-line"></i>
              </button>
            </div>
          </div>
          <div class="element-body">
            ${renderElementContent(element)}
          </div>
        </div>
      `;
      
      // Grid'e ekle
      grid.addWidget({
        id: element.id,
        x: pos.x,
        y: pos.y,
        w: pos.width,
        h: pos.height,
        content: content
      });
    });
  }
  
  // Element türüne göre içeriği render et
  function renderElementContent(element) {
    switch(element.element_type) {
      case 'text':
        return `<div class="text-element">${element.content.text || ''}</div>`;
      
      case 'image':
        return `
          <div class="image-element">
            <img src="${element.content.imageUrl || ''}" alt="${element.title}">
          </div>
        `;
      
      case 'button':
        return `
          <div class="button-element">
            <a href="${element.content.url || '#'}" class="btn" target="${element.content.newTab ? '_blank' : '_self'}">
              ${element.content.text || 'Buton'}
            </a>
          </div>
        `;
      
      case 'video':
        return `
          <div class="video-element">
            <iframe src="${element.content.videoUrl || ''}" frameborder="0" allowfullscreen></iframe>
          </div>
        `;
      
      default:
        return `<div class="unknown-element">Bilinmeyen element türü</div>`;
    }
  }
  
  // Style nesnesini CSS string'ine dönüştür
  function getStyleString(style) {
    if (!style) return '';
    
    return Object.entries(style)
      .map(([key, value]) => {
        // camelCase'i kebab-case'e dönüştür
        const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
        return `${cssKey}: ${value};`;
      })
      .join(' ');
  }
  
  // Yeni element oluştur
  function createNewElement(elementType, x, y) {
    // Grid üzerindeki konumu hesapla
    const gridPos = calculateGridPosition(x, y);
    
    // Element tipi için varsayılan başlık ve içerik
    let title, content;
    
    switch(elementType) {
      case 'text':
        title = 'Metin Bloğu';
        content = { text: 'Buraya metin ekleyin...' };
        break;
      
      case 'image':
        title = 'Görsel';
        content = { imageUrl: '/static/img/placeholder.jpg' };
        break;
      
      case 'button':
        title = 'Buton';
        content = { text: 'Tıkla', url: '#', newTab: false };
        break;
      
      case 'video':
        title = 'Video';
        content = { videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ' };
        break;
      
      default:
        title = 'Yeni Element';
        content = {};
    }
    
    // API'ye gönderilecek veri
    const data = {
      element_type: elementType,
      title: title,
      content: content,
      position: {
        x: gridPos.x,
        y: gridPos.y,
        width: 6,
        height: 2
      },
      page_id: pageId
    };
    
    // API isteği
    fetch('/page-builder/api/elements', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(newElement => {
      // Ekrana ekle
      fetchElements(); // Tüm elementleri tekrar yükle
      showNotification('Element başarıyla eklendi.', 'success');
    })
    .catch(error => {
      console.error('Element eklenirken hata oluştu:', error);
      showNotification('Element eklenirken bir hata oluştu.', 'error');
    });
  }
  
  // Element düzenleme modalını aç
  function openElementEditor(elementId) {
    // Element verilerini getir
    const item = document.querySelector(`.grid-stack-item[gs-id="${elementId}"]`);
    if (!item) return;
    
    currentElementId = elementId;
    
    // API'den element detaylarını getir
    fetch(`/page-builder/api/elements/${elementId}`)
      .then(response => response.json())
      .then(element => {
        // Form alanlarını doldur
        const form = document.getElementById('element-form');
        
        form.querySelector('[name="element-title"]').value = element.title;
        
        if (element.content.text) {
          form.querySelector('[name="element-content"]').value = element.content.text;
        }
        
        if (element.style) {
          if (element.style.backgroundColor) {
            form.querySelector('[name="element-bg-color"]').value = element.style.backgroundColor;
          }
          
          if (element.style.textColor) {
            form.querySelector('[name="element-text-color"]').value = element.style.textColor;
          }
          
          if (element.style.padding) {
            form.querySelector('[name="element-padding"]').value = element.style.padding;
          }
          
          if (element.style.borderRadius) {
            form.querySelector('[name="element-border-radius"]').value = element.style.borderRadius;
          }
        }
        
        // Modalı göster
        elementModal.classList.remove('hidden');
      })
      .catch(error => {
        console.error('Element detayları getirilirken hata oluştu:', error);
        showNotification('Element detayları yüklenirken bir hata oluştu.', 'error');
      });
  }
  
  // Element güncelle
  function updateElement(elementId, data) {
    fetch(`/page-builder/api/elements/${elementId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        fetchElements(); // Tüm elementleri tekrar yükle
        showNotification('Element başarıyla güncellendi.', 'success');
      } else {
        showNotification('Element güncellenirken bir hata oluştu.', 'error');
      }
    })
    .catch(error => {
      console.error('Element güncellenirken hata oluştu:', error);
      showNotification('Element güncellenirken bir hata oluştu.', 'error');
    });
  }
  
  // Element sil
  function deleteElement(elementId) {
    if (!confirm('Bu elementi silmek istediğinizden emin misiniz?')) return;
    
    fetch(`/page-builder/api/elements/${elementId}`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCsrfToken()
      }
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        // Grid'den kaldır
        grid.removeWidget(document.querySelector(`.grid-stack-item[gs-id="${elementId}"]`));
        showNotification('Element başarıyla silindi.', 'success');
      } else {
        showNotification('Element silinirken bir hata oluştu.', 'error');
      }
    })
    .catch(error => {
      console.error('Element silinirken hata oluştu:', error);
      showNotification('Element silinirken bir hata oluştu.', 'error');
    });
  }
  
  // Sayfa şablonunu değiştir
  function setPageTemplate(templateId) {
    fetch(`/page-builder/api/pages/${pageId}/template`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ template_id: templateId })
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        showNotification('Sayfa şablonu başarıyla değiştirildi.', 'success');
        // Sayfayı yenileyerek yeni şablonu uygula
        window.location.reload();
      } else {
        showNotification('Şablon değiştirilirken bir hata oluştu.', 'error');
      }
    })
    .catch(error => {
      console.error('Şablon değiştirilirken hata oluştu:', error);
      showNotification('Şablon değiştirilirken bir hata oluştu.', 'error');
    });
  }
  
  // Düzen değişikliklerini kaydet
  function saveLayout(elements) {
    fetch(`/page-builder/api/pages/${pageId}/save-layout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ elements: elements })
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        // Sessiz bir şekilde kaydet
      } else {
        showNotification('Düzen kaydedilirken bir hata oluştu.', 'error');
      }
    })
    .catch(error => {
      console.error('Düzen kaydedilirken hata oluştu:', error);
      showNotification('Düzen kaydedilirken bir hata oluştu.', 'error');
    });
  }
  
  // Fare pozisyonundan grid pozisyonunu hesapla
  function calculateGridPosition(mouseX, mouseY) {
    const container = document.getElementById('grid-container');
    const rect = container.getBoundingClientRect();
    
    // Mouse pozisyonunu container içine göreceli hale getir
    const relativeX = mouseX - rect.left;
    const relativeY = mouseY - rect.top;
    
    // Container genişliği ve yüksekliği
    const containerWidth = rect.width;
    const containerHeight = rect.height;
    
    // Grid sutun ve satır sayısı
    const columns = 12;
    const rowHeight = grid.cellHeight();
    
    // X ve Y koordinatlarını hesapla
    const x = Math.floor(relativeX / (containerWidth / columns));
    const y = Math.floor(relativeY / rowHeight);
    
    return { x: Math.max(0, x), y: Math.max(0, y) };
  }
  
  // CSRF token al
  function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  }
  
  // Bildirim göster
  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 3 saniye sonra kaybolsun
    setTimeout(() => {
      notification.classList.add('hide');
      setTimeout(() => notification.remove(), 500);
    }, 3000);
  }

  // Kaydet butonu
  const saveButton = document.getElementById('save-page-btn');
  if (saveButton) {
    saveButton.addEventListener('click', function() {
      showNotification('Sayfa düzeni kaydedildi.', 'success');
    });
  }
}); 