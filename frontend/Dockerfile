# Use the official Nginx image as the base image
FROM nginx:alpine

# Copy the frontend HTML files to the nginx container
COPY . /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 to access the frontend
EXPOSE 80

# Run the nginx server to serve the files
CMD ["nginx", "-g", "daemon off;"]
