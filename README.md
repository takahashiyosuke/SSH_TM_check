```markdown
# Time Machine Backup Monitor (Dockerized)

這是一個使用 Python 撰寫、透過 Docker 進行部署的簡易「macOS 時光機備份監控」專案。  
主要功能包括：
- 定時檢查 macOS 「時光機」備份時間，並發送通知到指定的 Telegram Chat。
- 支援透過 `/status` 指令來手動查詢當前備份狀態。
- 使用環境變數輸入 SSH 密碼、Telegram Bot Token 與 Chat ID，確保程式碼中不留任何機敏資訊。

## 目錄
- [專案結構](#專案結構)
- [需求與安裝](#需求與安裝)
- [環境變數](#環境變數)
- [使用方式](#使用方式)
- [Docker 部署](#docker-部署)
- [License](#license)
- [常見問題 (FAQ)](#常見問題-faq)

---

## 專案結構

```plaintext
.
├── Dockerfile           # Docker 建置檔
├── monitor.py           # Python 主程式 (含定時檢查 & 手動查詢功能)
├── requirements.txt     # Python 相依套件列表
└── README.md            # 專案說明文件 (本文)
```

- **monitor.py**  
  透過 `schedule` 模組定時執行 SSH 連線至 macOS，呼叫 `tmutil` 指令以查詢最新備份狀態。  
  同時也會每幾秒檢查 Telegram 是否有 `/status` 指令，若有則立即查詢並回傳結果。

- **Dockerfile**  
  - 以 `python:3.9-slim` 為基底  
  - 安裝 `openssh-client` 以支援 `paramiko` SSH 連線  
  - 安裝 `requirements.txt` 中所需的套件  
  - 最終執行 `monitor.py` 以啟動服務

---

## 需求與安裝

1. **Python 3.8+**  
   - 如果您不打算使用 Docker，可直接在本地執行程式
2. **pip**  
   - 若您想安裝套件
3. **Docker**  
   - 若您想容器化部署

### 安裝 Python 依賴套件

若在本地執行：
```bash
pip install --no-cache-dir -r requirements.txt
```

---

## 環境變數

專案使用下列 **環境變數**，請確保在本地或 Docker 容器中設定：

| 變數名稱             | 用途                           | 範例                               |
|----------------------|--------------------------------|------------------------------------|
| `MACOS_HOST`         | macOS 內網 IP（或主機名稱）    | `192.168.0.1/24`                    |
| `MACOS_USER`         | macOS 登入使用者名稱          | `Username`                              |
| `MACOS_PASSWORD`     | macOS SSH 密碼                | *透過環境變數設置，程式碼中不留*   |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token            | `123456:ABC-DEF_ghi123`            |
| `TELEGRAM_CHAT_ID`   | 要接收通知的 Chat ID          | `123456789`                        |
| `CHECK_INTERVAL_MINUTES` | (選擇性) 定時檢查間隔 (分鐘) | 預設 `720` 分鐘                   |

> **注意：**  
> 若未明確在程式碼中指定 `CHECK_INTERVAL_MINUTES` 這個環境變數，將以預設值（720 分鐘）作為自動檢查間隔。

---

## 使用方式

### 1. 本機執行

1. **安裝相依套件**
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```
2. **設定環境變數**
   ```bash
   export MACOS_HOST="192.168.0.xxx"
   export MACOS_USER="your_user"
   export MACOS_PASSWORD="your_password"
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```
3. **執行程式**
   ```bash
   python monitor.py
   ```
4. **測試**  
   - 程式會在背景自動執行定時備份檢查。  
   - 可到 Telegram 與您的 Bot 對話，輸入 `/status` 即可手動查詢備份狀態。

### 2. Docker 執行

若您想在容器中執行，請參考下方 [Docker 部署](#docker-部署) 章節。

---

## Docker 部署

### 建置映像檔

假設您已將此專案內容放在同一個資料夾中（含 `Dockerfile`、`monitor.py`、`requirements.txt`）。在該資料夾下執行：

```bash
docker build -t your_image_name:latest .
```

- `-t your_image_name:latest` 用來指定映像檔名稱與標籤。  
- 您可視需求命名，如 `my_tm_monitor:latest` 等。

### 執行容器

將映像執行為容器並設定環境變數：

```bash
docker run -d \
  -e MACOS_HOST="192.168.0.xxx" \
  -e MACOS_USER="your_user" \
  -e MACOS_PASSWORD="your_password" \
  -e TELEGRAM_BOT_TOKEN="your_telegram_bot_token" \
  -e TELEGRAM_CHAT_ID="your_chat_id" \
  --name tm_monitor \
  your_image_name:latest
```

- `-d`：在背景執行容器  
- `--name tm_monitor`：指定容器名稱，方便管理  

完成後，程式會自動在容器中運行並定時檢查。  
同樣地，您可以透過 Telegram Bot 發送 `/status` 指令，即時查詢備份狀況。

---

## License

本專案採用 [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.zh-tw.html) 授權，您可以在遵守該授權條款的前提下自由使用、修改及散佈本程式。如需更詳細資訊。

---

## 常見問題 (FAQ)

1. **為什麼 `Operation not permitted`？**  
   - 確認專案不在 iCloud/Dropbox 等同步資料夾。  
   - 檢查檔案與 `.git` 權限設定。

2. **macOS IP 與使用者名稱是否能留空？**  
   - 若您要透過 SSH 連線，就必須知道 macOS 主機 IP 與有效的使用者名稱。

3. **Telegram Bot 怎麼取得 Token？**  
   - 在 Telegram 與 [BotFather](https://t.me/botfather) 對話，建立新 Bot 即可取得 Token。

4. **如何設定長輪詢 / Webhook？**  
   - 範例程式中使用 `getUpdates`（輪詢）方式；如需改用 Webhook，可參考 Telegram 官方文件或 `python-telegram-bot` 相關說明。
```

---
