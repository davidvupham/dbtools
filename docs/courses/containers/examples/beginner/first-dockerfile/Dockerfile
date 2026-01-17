# First Dockerfile Example
# This demonstrates basic Dockerfile instructions

# Use nginx alpine as base (small and efficient)
FROM nginx:alpine

# Document the author
LABEL maintainer="containers-course"
LABEL description="First Dockerfile example"

# Copy our custom HTML file to nginx's web root
COPY index.html /usr/share/nginx/html/index.html

# Document that the container listens on port 80
EXPOSE 80

# The CMD is inherited from the nginx base image
# nginx will start automatically when the container runs
