FROM node:20 AS build
ARG TARGETARCH
WORKDIR /app
COPY piro-ui/package*.json ./
RUN npm ci
RUN case "$TARGETARCH" in \
    "amd64") npm install --no-save @rollup/rollup-linux-x64-gnu ;; \
    "arm64") npm install --no-save @rollup/rollup-linux-arm64-gnu ;; \
    *) echo "Unsupported TARGETARCH $TARGETARCH for rollup; attempting default install" && npm install --no-save rollup ;; \
  esac
COPY piro-ui/ .
RUN npm run build:prod
FROM nginx:1.27-alpine
COPY piro-ui/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/piro /usr/share/nginx/html
EXPOSE 80
