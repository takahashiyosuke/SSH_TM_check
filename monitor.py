import os
import time
import requests
import paramiko
import schedule

# --------------------
# 環境參數讀取
# --------------------
MACOS_HOST = ""     # 請依需求修改
MACOS_USER = ""               # 請依需求修改
MACOS_PASSWORD = os.getenv("MACOS_PASSWORD")  # 無預設值，請於環境變數設定

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # 無預設值
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")      # 無預設值

# 依照需求修改檢查間隔(分鐘)，例如 720 分鐘即為 12 小時
CHECK_INTERVAL_MINUTES = 720

# 定義 Telegram API 基本路徑；若沒有設定 Token，則會是 None
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# 記錄上一次處理到的 Update ID，用於長輪詢
LAST_UPDATE_ID = 0

# --------------------
# 核心功能
# --------------------
def check_time_machine_status(chat_id=TELEGRAM_CHAT_ID):
    """
    檢查 macOS 時光機備份狀態並回傳結果至指定 chat_id。
    預設使用 TELEGRAM_CHAT_ID，如有需要可自行傳入其他值。
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 若未設定 MACOS_PASSWORD，此處會是 None，需要自行處理或提前檢查
        ssh.connect(MACOS_HOST, username=MACOS_USER, password=MACOS_PASSWORD, timeout=10)

        # 執行 tmutil 指令
        stdin, stdout, stderr = ssh.exec_command("tmutil latestbackup")
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        # 分析結果
        if error:
            send_telegram_message(f"❌ 時光機備份錯誤(°ཀ°)：{error or '未知錯誤'}", chat_id)
        else:
            send_telegram_message(f"✅ 最新時光機備份٩(｡・ω・｡)﻿و：{output}", chat_id)

    except Exception as e:
        send_telegram_message(f"❌ SSH 連線失敗(|||ﾟдﾟ)：{e}", chat_id)


def send_telegram_message(message, chat_id=TELEGRAM_CHAT_ID):
    """
    發送 Telegram 通知至指定 chat_id。
    預設使用 TELEGRAM_CHAT_ID，如有需要可自行傳入其他值。
    """
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print("Telegram Token 或 Chat ID 未設定，無法發送訊息。")
        return

    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 若狀態碼非 200，則觸發例外
    except requests.exceptions.RequestException as e:
        print(f"Telegram 通知錯誤：{e}")


# --------------------
# 輪詢 Telegram /status 指令
# --------------------
def poll_telegram_commands():
    """
    定期呼叫 Telegram getUpdates 進行輪詢，若偵測到 /status 則立即執行備份檢查。
    """
    global LAST_UPDATE_ID

    if not TELEGRAM_BOT_TOKEN:
        return  # 若未設定 Token，不執行

    url = f"{TELEGRAM_API_BASE}/getUpdates?offset={LAST_UPDATE_ID+1}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # 如果拿到的回應不正常，就不繼續
        if not data.get("ok"):
            return

        for result in data.get("result", []):
            update_id = result["update_id"]
            message = result.get("message", {})

            # 使用者傳的文字訊息
            text = message.get("text", "")
            # 使用者對話的 chat_id
            user_chat_id = message.get("chat", {}).get("id")

            # 碰到 /status 就執行狀態檢查並將結果回傳給該使用者
            if text.strip() == "/status":
                check_time_machine_status(chat_id=user_chat_id)

            # 更新 LAST_UPDATE_ID，避免重複讀取同一筆訊息
            LAST_UPDATE_ID = update_id

    except Exception as e:
        print(f"Telegram 輪詢錯誤：{e}")


# --------------------
# 排程設定
# --------------------
# 每 720 分鐘自動檢查一次時光機備份，可自行調整間隔
schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_time_machine_status)

# 每 10 秒檢查一次 Telegram 是否收到 /status 指令
schedule.every(10).seconds.do(poll_telegram_commands)


# --------------------
# 主程式入口
# --------------------
if __name__ == "__main__":
    print("時光機備份監控服務啟動中...")
    while True:
        schedule.run_pending()
        time.sleep(1)
