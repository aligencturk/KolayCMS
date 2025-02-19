import sqlite3

def update_table():
    conn = sqlite3.connect('kolaycms.db')
    cursor = conn.cursor()
    
    # Yeni sütunları ekle
    alter_commands = [
        "ALTER TABLE site_settings ADD COLUMN theme_version VARCHAR(10) DEFAULT '1.0'",
        "ALTER TABLE site_settings ADD COLUMN theme_name VARCHAR(50) DEFAULT 'default'",
        "ALTER TABLE site_settings ADD COLUMN is_customized BOOLEAN DEFAULT 0",
        "ALTER TABLE site_settings ADD COLUMN success_color VARCHAR(10) DEFAULT '#28a745'",
        "ALTER TABLE site_settings ADD COLUMN info_color VARCHAR(10) DEFAULT '#17a2b8'",
        "ALTER TABLE site_settings ADD COLUMN warning_color VARCHAR(10) DEFAULT '#ffc107'",
        "ALTER TABLE site_settings ADD COLUMN danger_color VARCHAR(10) DEFAULT '#dc3545'",
        
        # Navbar Ayarları
        "ALTER TABLE site_settings ADD COLUMN navbar_bg_color VARCHAR(10) DEFAULT '#ffffff'",
        "ALTER TABLE site_settings ADD COLUMN navbar_text_color VARCHAR(10) DEFAULT '#000000'",
        "ALTER TABLE site_settings ADD COLUMN navbar_active_color VARCHAR(10) DEFAULT '#007bff'",
        "ALTER TABLE site_settings ADD COLUMN navbar_hover_color VARCHAR(10) DEFAULT '#0056b3'",
        "ALTER TABLE site_settings ADD COLUMN navbar_is_fixed BOOLEAN DEFAULT 1",
        "ALTER TABLE site_settings ADD COLUMN navbar_is_transparent BOOLEAN DEFAULT 0",
        "ALTER TABLE site_settings ADD COLUMN navbar_font_family VARCHAR(50) DEFAULT 'inherit'",
        "ALTER TABLE site_settings ADD COLUMN navbar_font_size VARCHAR(10) DEFAULT '1rem'",
        
        # Body Ayarları
        "ALTER TABLE site_settings ADD COLUMN body_bg_color VARCHAR(10) DEFAULT '#ffffff'",
        "ALTER TABLE site_settings ADD COLUMN body_text_color VARCHAR(10) DEFAULT '#212529'",
        "ALTER TABLE site_settings ADD COLUMN body_link_color VARCHAR(10) DEFAULT '#007bff'",
        "ALTER TABLE site_settings ADD COLUMN body_font_family VARCHAR(50) DEFAULT 'Poppins'",
        "ALTER TABLE site_settings ADD COLUMN body_font_size VARCHAR(10) DEFAULT '14px'",
        "ALTER TABLE site_settings ADD COLUMN body_line_height VARCHAR(10) DEFAULT '1.5'",
        
        # Footer Ayarları
        "ALTER TABLE site_settings ADD COLUMN footer_bg_color VARCHAR(10) DEFAULT '#343a40'",
        "ALTER TABLE site_settings ADD COLUMN footer_text_color VARCHAR(10) DEFAULT '#ffffff'",
        "ALTER TABLE site_settings ADD COLUMN footer_link_color VARCHAR(10) DEFAULT '#ffffff'",
        "ALTER TABLE site_settings ADD COLUMN footer_font_family VARCHAR(50) DEFAULT 'inherit'",
        "ALTER TABLE site_settings ADD COLUMN footer_font_size VARCHAR(10) DEFAULT '1rem'",
        
        # Diğer Ayarlar
        "ALTER TABLE site_settings ADD COLUMN custom_header_code TEXT",
        "ALTER TABLE site_settings ADD COLUMN custom_footer_code TEXT",
        "ALTER TABLE site_settings ADD COLUMN custom_meta_tags TEXT",
        "ALTER TABLE site_settings ADD COLUMN maintenance_mode BOOLEAN DEFAULT 0",
        "ALTER TABLE site_settings ADD COLUMN maintenance_message TEXT DEFAULT 'Site bakım modunda.'",
        "ALTER TABLE site_settings ADD COLUMN google_analytics_id VARCHAR(50)",
        "ALTER TABLE site_settings ADD COLUMN recaptcha_site_key VARCHAR(100)",
        "ALTER TABLE site_settings ADD COLUMN recaptcha_secret_key VARCHAR(100)"
    ]
    
    for command in alter_commands:
        try:
            cursor.execute(command)
            print(f"Başarılı: {command}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Sütun zaten var: {command}")
            else:
                print(f"Hata: {str(e)} - {command}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_table() 