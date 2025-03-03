import os

def create_module_directories():
    # Ana modül dizini
    modules_dir = 'app/modules'
    
    # Modül listesi
    modules = [
        'reports',
        'sliders', 
        'corporate',
        'team',
        'hr',
        'services',
        'projects',
        'users'
    ]
    
    # Ana dizini oluştur
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    
    # Her bir modül için klasör oluştur
    for module in modules:
        module_path = os.path.join(modules_dir, module)
        if not os.path.exists(module_path):
            os.makedirs(module_path)
            # __init__.py dosyasını oluştur
            with open(os.path.join(module_path, '__init__.py'), 'w') as f:
                pass
            # models.py dosyasını oluştur
            with open(os.path.join(module_path, 'models.py'), 'w') as f:
                pass
            # views.py dosyasını oluştur
            with open(os.path.join(module_path, 'views.py'), 'w') as f:
                pass

if __name__ == '__main__':
    create_module_directories()
    print("Modül klasörleri başarıyla oluşturuldu.") 