FROM node:20-alpine
WORKDIR /web/
RUN corepack enable && corepack prepare yarn@1.22.22 --activate
COPY web/. .
RUN yarn install
RUN yarn build

FROM nginx:alpine
COPY ./docker_env/nginx/my.conf /etc/nginx/conf.d/my.conf
COPY --from=0 /web/dist /usr/share/nginx/html