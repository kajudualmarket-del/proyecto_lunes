# =============================
# Etapa 1: Compilar aplicación Angular
# =============================
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm install -g @angular/cli@16.2.16
RUN npm ci --legacy-peer-deps
RUN npm install --save-dev @angular-devkit/build-angular

COPY . .

RUN ng build --configuration production

# =============================
# Etapa 2: Servir aplicación con http-server
# =============================
FROM node:20-alpine

RUN npm install -g http-server && npm cache clean --force

WORKDIR /app

# Copiamos SOLO lo que Angular genera
COPY --from=build /app/dist ./ 

EXPOSE 8080

CMD ["http-server", "/app", "-p", "8080", "--cors", "-c-1"]

