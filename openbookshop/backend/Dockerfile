# 后端 Dockerfile（Django + Gunicorn）
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，防止 Python 缓存字节码和 stdout/stderr 缓冲
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 使用国内镜像加速 pip 安装（先复制 requirements.txt 利用 Docker 层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# 复制项目代码
COPY . .

# 修复 Windows CRLF 换行符并赋予执行权限
RUN sed -i 's/\r//' entrypoint.sh && chmod +x entrypoint.sh

# 暴露端口
EXPOSE 8000

# 使用 entrypoint 脚本（处理 collectstatic、migrate 和 gunicorn 启动）
ENTRYPOINT ["./entrypoint.sh"]
