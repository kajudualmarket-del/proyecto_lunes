# =============================
# Etapa 1: Compilar aplicación Angular
# =============================
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./

# ✅ CLI alineado con Angular 20
RUN npm install -g @angular/cli@20.3.6

# ✅ Manejo de conflictos de dependencias
RUN npm ci --legacy-peer-deps

# 🚫 Ya no se necesita (provocaba el error)
# RUN npm install --save-dev @angular-devkit/build-angular

COPY . .

RUN ng build --configuration production

# =============================
# Etapa 2: Servir aplicación con http-server
# =============================
FROM node:20-alpine

RUN npm install -g http-server && npm cache clean --force

WORKDIR /app

COPY --from=build /app/dist ./

EXPOSE 8080

CMD ["http-server", "/app", "-p", "8080", "--cors", "-c-1"]
