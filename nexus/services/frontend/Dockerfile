# Dockerfile para frontend React + Vite
# services/frontend/Dockerfile

FROM node:20-alpine

WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm install

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 5173

# Comando de desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]