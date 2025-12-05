FROM nginx:alpine

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Создаем директорию для статических файлов (будет смонтирована через volume)
RUN mkdir -p /usr/share/nginx/html

# Expose порты
EXPOSE 80 443

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]

