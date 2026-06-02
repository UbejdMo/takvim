# Frontend image: build the Vite/React app, then serve the static bundle with nginx on :80.
# VITE_API_BASE_URL must be provided at BUILD time — Vite inlines import.meta.env.VITE_* into
# the bundle (docker-compose passes it as a build arg).

# ---- Build stage ----
FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# ---- Serve stage ----
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
