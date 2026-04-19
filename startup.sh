#!/bin/bash
# Comando de inicio para Azure App Service
# Azure ejecuta este archivo automáticamente al iniciar la app

gunicorn --bind=0.0.0.0:8000 --timeout 120 --workers 2 app:app