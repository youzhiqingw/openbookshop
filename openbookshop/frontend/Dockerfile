# 前端 Dockerfile（Vue3 + Nginx）
# ========== 构建阶段 ==========
FROM node:18-alpine AS builder

WORKDIR /app

# 使用国内 npm 镜像加速
RUN npm config set registry https://registry.npmmirror.com

# 先复制 package.json 利用 Docker 层缓存
COPY package.json package-lock.json* ./
RUN npm install

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
