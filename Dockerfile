# Use an official Python runtime as a parent image (change 'buster' to 'slim', if needed)
FROM python:3.11-buster  

LABEL maintainer="your_name@example.com"  

WORKDIR /usr/src/app  

COPY requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt  

COPY . .  

EXPOSE 8501  
EXPOSE 5000

# 使用多进程管理器启动两个服务
RUN apt-get update && apt-get install -y supervisor
COPY docker-supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]  

