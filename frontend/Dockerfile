FROM nginx:alpine
# Copies your updated index.html into the Nginx server
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
