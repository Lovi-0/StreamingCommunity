# Usa un'immagine di base con Node.js
FROM node:14-alpine

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file necessari
COPY . .

# Installa le dipendenze e builda il frontend React
RUN npm install && npm run build && npm install -g serve

# Espone la porta su cui il server React ascolterà
EXPOSE 3000

# Comando per avviare il server React
CMD ["serve", "-s", "build", "-l", "3000"]

