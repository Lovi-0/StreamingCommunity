#!/bin/bash

# Installa i pacchetti Python
echo "Installazione dei pacchetti Python..."
pip install -r requirements.txt

# Installa i pacchetti npm
echo "Installazione dei pacchetti npm..."
cd frontend
npm install
cd ..

# Avvia il backend Django
echo "Avvio del backend Django..."
python3.11 api/manage.py runserver &

# Avvia il frontend Vue.js con Vite
echo "Avvio del frontend Vue.js con Vite..."
cd frontend
npm run dev &

# Attendi l'esecuzione dei processi
wait