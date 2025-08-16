# Build stage
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Install dependencies for node-gyp and security updates
RUN apk add --no-cache python3 make g++ && \
    apk upgrade

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy project files
COPY . .

# Set production environment variables for build
ENV NODE_ENV=production
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8000}
ENV VITE_CHAT_API_BASE_URL=${VITE_CHAT_API_BASE_URL:-http://localhost:8001}
ENV VITE_FINANCIAL_API_BASE_URL=${VITE_FINANCIAL_API_BASE_URL:-http://localhost:8002}

# Build the app for production
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for health checks and security updates
RUN apk add --no-cache curl && \
    apk upgrade

# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf.bak

# Create nginx user and set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    chmod -R 755 /usr/share/nginx/html

# Create directories for nginx to write to
RUN mkdir -p /var/cache/nginx/client_temp && \
    mkdir -p /var/cache/nginx/proxy_temp && \
    mkdir -p /var/cache/nginx/fastcgi_temp && \
    mkdir -p /var/cache/nginx/uwsgi_temp && \
    mkdir -p /var/cache/nginx/scgi_temp && \
    chown -R nginx:nginx /var/cache/nginx

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 80

# Health check with better error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Start nginx with proper signal handling
CMD ["nginx", "-g", "daemon off;"]