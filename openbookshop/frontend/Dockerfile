# 前端 Dockerfile（Vue3 + Nginx）
# ========== 构建阶段 ==========
FROM node:18-alpine AS builder

WORKDIR /app

# 先复制 package.json 利用 Docker 层缓存
COPY package.json package-lock.json* ./

# 使用 npm install 并添加重试机制，同时设置合理的超时和资源限制
RUN npm install --legacy-peer-deps --foreground --fetch-timeout=60000 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || npm install --legacy-peer-deps

# 复制源码并构建
COPY . .
RUN npm run build

# ========== 生产阶段 ==========
FROM nginx:alpine

# 删除默认 Nginx 欢迎页
RUN rm -rf /usr/share/nginx/html/*

# 将构建产物复制到 Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置（与 Dockerfile 同目录）
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
