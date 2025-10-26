# ==============================
# Etapa 1: Compilar Angular 16
# ==============================
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install -g @angular/cli@16.2.16
RUN npm install --frozen-lockfile

COPY . .
RUN npm run build --prod

# ==============================
# Etapa 2: Servir aplicación con http-server
# ==============================
FROM node:20-alpine AS production

# Instalar http-server globalmente
RUN npm install -g http-server

# Establecemos la raíz de la aplicación para copiar los archivos.
WORKDIR /usr/src/app

# Copiamos SOLO la carpeta dist a /usr/src/app/dist
COPY --from=build /app/dist /usr/src/app/dist

# *** CAMBIO CLAVE: Usar la ruta completa de la subcarpeta como base para http-server ***
# Ahora, el CMD apunta directamente a la subcarpeta que contiene index.html
# -p 4200: Puerto interno
# -c-1: Sin caché
# --proxy: Necesario para que Angular SPA funcione
CMD ["http-server", "dist/trabajo_lunes/browser", "-a", "0.0.0.0", "-p", "4200", "-c-1", "--proxy", "http://0.0.0.0:4200"]