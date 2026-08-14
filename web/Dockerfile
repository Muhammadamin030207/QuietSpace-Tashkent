FROM node:22-alpine

WORKDIR /app

COPY packages/api-client /packages/api-client
COPY web/package.json ./
RUN npm install

COPY web/ .

EXPOSE 5174
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]