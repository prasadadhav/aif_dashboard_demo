FROM node:16

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Use serve package to serve the built app
RUN npm install -g serve

EXPOSE 3001

CMD ["serve", "-s", "build", "-l", "3001"]