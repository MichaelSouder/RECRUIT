# Multi-stage build for smaller production image

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Vite env vars must be available at build time
# VITE_BASE_PATH: "/" for site root, "/recruit/" for https://host/recruit/
ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}
ARG VITE_API_URL=
ENV VITE_API_URL=${VITE_API_URL}

# Build the application
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

ARG NGINX_CONFIG=default
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx/${NGINX_CONFIG}.conf /etc/nginx/conf.d/default.conf

ARG HEALTH_URI=/health

# Expose port
EXPOSE 80

# Health check (path must match nginx config)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider "http://127.0.0.1${HEALTH_URI}" || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
