FROM node:21.7.1-alpine
WORKDIR /app
COPY package.json package-lock.json .npmrc ./
RUN npm ci
COPY . ./
RUN npm run build
CMD cp -r build result_build
