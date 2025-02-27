#!/usr/bin/env bash
# exit on error
set -o errexit

# Python sürümünü güncelle
python -m pip install --upgrade pip

# Gereksinimleri yükle
pip install -r requirements.txt

# Gunicorn'u direkt olarak yükle
pip install gunicorn

# Gerekli dizinleri oluştur
mkdir -p instance
mkdir -p /tmp

# SQLite veritabanının yazma izinlerini kontrol et
touch /tmp/cms.db
chmod 777 /tmp/cms.db

# Veritabanı tablolarını oluştur
python initialize_db.py 