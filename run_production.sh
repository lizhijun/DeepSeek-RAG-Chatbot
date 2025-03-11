#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export FLASK_APP=api.py
export FLASK_ENV=production

# 确保目录存在
mkdir -p logs
mkdir -p temp

# 使用Gunicorn作为WSGI服务器启动应用
# -w: 工作进程数，建议设置为CPU核心数的2-4倍
# -b: 绑定的地址和端口
# --timeout: 超时时间，默认30秒
# --access-logfile: 访问日志文件路径
# --error-logfile: 错误日志文件路径
gunicorn -w 4 -b 0.0.0.0:5005 --timeout 120 --access-logfile logs/access.log --error-logfile logs/error.log api:app 