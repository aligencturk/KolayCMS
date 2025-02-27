#!/usr/bin/env bash
# exit on error
set -o errexit

# Python sürümünü güncelle
python -m pip install --upgrade pip

# Gereksinimleri yükle
pip install -r requirements.txt

# Gunicorn'u direkt olarak yükle
pip install gunicorn

# Gerekli dizinlerin varlığını kontrol et
mkdir -p instance 