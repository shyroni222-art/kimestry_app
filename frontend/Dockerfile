# Multi-stage build for React app
# Build stage
FROM node:18-alpine AS builder

# Set environment variables
ENV NODE_ENV=production

# Set work directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy project files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Copy the build output to replace the default nginx page
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Run the application
CMD ["nginx", "-g", "daemon off;"]