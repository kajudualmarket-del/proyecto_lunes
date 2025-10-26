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
# Etapa 2: Servir aplicación
# ==============================
FROM node:20-alpine AS production

WORKDIR /usr/src/app

# Servir SPA correctamente
RUN npm install -g serve

# Copiar archivos compilados
COPY --from=build /app/dist/trabajo_lunes/browser/. /usr/src/app/


# Servir la app en puerto 4200 con fallback para Angular
CMD ["serve", "-s", ".", "-l", "4200"]
