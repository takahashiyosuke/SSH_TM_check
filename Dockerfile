# 使用官方 Python 3.9 slim 版映像
FROM python:3.9-slim

# 安裝必要套件：SSH Client (Paramiko連線需要)
RUN apt-get update && apt-get install -y openssh-client && rm -rf /var/lib/apt/lists/*

# 宣告環境變數（在此只做佔位，實際值請在部署/執行時注入）
ENV MACOS_PASSWORD=""
ENV TELEGRAM_BOT_TOKEN=""
ENV TELEGRAM_CHAT_ID=""

# 設定工作目錄
WORKDIR /app

# 複製程式碼和 requirements.txt
COPY . .

# 安裝 Python 相依套件
RUN pip install --no-cache-dir -r requirements.txt

# 指定容器啟動時要執行的指令
CMD ["python", "monitor.py"]