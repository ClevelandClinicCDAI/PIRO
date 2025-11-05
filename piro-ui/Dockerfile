FROM node:20 AS build
WORKDIR /app
COPY piro-ui/package*.json ./
RUN npm ci
COPY piro-ui/ .
RUN npm run build:prod
FROM nginx:1.27-alpine
COPY docker/ui/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/piro /usr/share/nginx/html
EXPOSE 80
