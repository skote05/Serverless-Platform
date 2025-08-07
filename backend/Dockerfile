FROM node:18-alpine

# Install curl for health checks
RUN apk add --no-cache curl

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5001

CMD ["npm", "start"]
