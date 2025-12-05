FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Команда по умолчанию - сборка статики (будет переопределена в docker-compose)
CMD ["sh", "-c", "npm run build && cp -r build/* /app/build/"]
