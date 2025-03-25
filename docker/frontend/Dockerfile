# Stage 1: Base image for development
FROM node:18-alpine AS dev

# Set working directory
WORKDIR /app

# Install Angular CLI globally
RUN npm install -g @angular/cli@16.2.12

# Copy package.json and package-lock.json (if exists) for dependency installation
COPY frontend/package*.json frontend/angular.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the Angular project files
COPY frontend/ .

# Expose port 3000 (custom port for ng serve)
EXPOSE 3000

# Start the Angular development server on port 3000
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "3000"]