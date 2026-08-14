FROM node:22-alpine

WORKDIR /app

COPY packages/api-client /packages/api-client
COPY miniapp/package.json ./
RUN npm install

COPY miniapp/ .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
