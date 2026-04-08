# 🤖 Arena AI Bot Template (Python)

歡迎來到期末 AI 錦標賽！這份官方 Python 模板已經為你處理好所有繁瑣的伺服器通訊、Session 維護、Heartbeat 與 SSE 重連。你只需要專注於一件事：**寫出最強的演算法擊敗對手。**

## 📂 專案結構

本模板包含以下核心檔案：

* **`strategy.py`** ⭐️ **你要寫扣的地方**：包含 `BotStrategy` 類別，你所有的 AI 邏輯（如 Minimax、Alpha-Beta 剪枝或神經網路推論）都請實作在這裡。
* **`main.py`** (不建議修改)：遊戲主程式。負責登入、維護狀態機、解析 SSE 事件流，並在適當的時機呼叫你的策略。
* **`api.py`** (不建議修改)：底層的 HTTP/REST API 封裝，會處理 session、錯誤 envelope 與 heartbeat 相關呼叫。
* **`requirements.txt`**：Python 依賴套件清單。

---

## 🚀 快速啟動 (Quick Start)

### 1. 安裝環境與依賴
請確保你的電腦已安裝 Python 3.8+。
```bash
# 建議使用虛擬環境 (Virtual Environment)
python -m venv venv
source venv/bin/activate  # Windows 系統請用 venv\Scripts\activate

# 安裝必要套件
pip install -r requirements.txt
```

### 2. 設定環境變數
你的 Bot 需要 API Key 才能連上競技場。請將以下環境變數替換為你在平台上獲得的真實資訊：
```bash
export ARENA_URL="http://your-arena-url.com" # 競技場網址
export BOT_API_KEY="ga_bot_YOUR_API_KEY"     # 你的專屬 API Key
export ROOM_ID="human-1"                     # 你要加入的房間 ID
export BOT_SEAT="black"                      # 偏好的初始座位，可設 black 或 white
```
*(Windows 使用者請將 `export` 替換為 `set` 或使用 PowerShell 的 `$env:VAR="value"`)*

注意：模板會在登入成功後直接使用 server 回傳的 bot `username`，不需要你自己手動指定 `BOT_USERNAME`。

### 3. 啟動你的 Bot
```bash
python main.py
```
啟動後，Bot 會自動登入、連線至房間、自動上桌與 ready，並在輪到你時呼叫 `strategy.py` 裡的邏輯。你可以打開網頁版競技場，親眼觀看你的 Bot 下棋。

---

## 🧠 如何開發你的 AI？

請打開 `strategy.py`，你只需要實作以下兩個核心函式：

### 1. `choose_move` (落子策略)
當輪到你的回合時，系統會呼叫此函式。你需要回傳你想落子的座標，以及是否使用特殊棋子（Strong 棋子）。

**傳入參數：**
* `board`: 15x15 的二維陣列（`.`=空, `b`=黑一般, `w`=白一般, `B`=黑強子, `W`=白強子）。
* `my_color`: 整數，**1** 代表黑方，**2** 代表白方。
* `strong_available`: 整數，你目前手上持有的 Strong 棋子數量（0 或 1）。
* `time_left`: 浮點數，你這局**剩餘的總思考時間**（秒）。

**回傳值格式：**
`row (int)`, `col (int)`, `use_strong (bool)`

### 2. `choose_bid` (Armageddon 競標策略)
如果前兩局雙方打平（1:1），將進入 Armageddon。雙方會進行 **simultaneous sealed bid**，**出價較低者將獲得該局的選色權（黑/白）**，和局則由未得標方獲勝。

**傳入參數：**
* `my_max_bid`: 你最多可以出的秒數（通常等於預設初始時間）。
* `default_color`: 預設分配的顏色。

**回傳值格式：**
`bid_seconds (float)`, `chosen_color (str, "black" 或 "white")`

---

## 📜 遊戲核心規則摘要

* **獲勝條件**：在 15x15 的棋盤上，率先將 **6 顆**自己的棋子連成一線（橫、豎、斜皆可）。
* **Strong 棋子 (強子)**：
    * 一般子只能下在空格。
    * 強子可以覆蓋在**任何非強子**（包含對手或自己的普通子）之上，且覆蓋後**無法再被任何人覆蓋**。
* **強子補給機制**：
    * 在第 6、13、20、27... 手開始前，雙方會同時獲得 1 顆強子。
    * **注意：強子最多只能庫存 1 顆！** 如果在補給回合到來前你沒有把手上的強子打出去，它就會被浪費掉。

---

## ⚠️ 效能與競技規範 (必讀)

這是一場寫實的程式競技，系統資源是有限的。在提交你的程式碼前，請注意以下事項：

1.  **時間就是生命**：本次錦標賽採用包含 increment 的快棋時制。你的 `choose_move` 函式如果執行時間超過你的 `time_left`，系統將會強制判斷你**超時落敗 (Timeout)**。
2.  **硬體限制**：錦標賽伺服器將使用 Docker 進行嚴格的資源隔離。請預設你的 Bot 只能使用 **有限的 CPU 核心** 進行運算。過度複雜的神經網路如果推論過慢，將會被傳統的高效 C++ / Python 搜尋演算法擊敗。
3.  **網路隔離**：比賽用的沙箱是**斷網**的（僅能連線至 Arena API）。請勿嘗試使用 API 呼叫外部的運算資源（如遠端 GPU 伺服器），這會導致你的程式直接崩潰。

---

## 🔌 Template 與目前 Arena Contract 的對應

這份模板目前已對齊以下 server 行為：

1. `POST /api/auth/login` 會回傳 bot user 資訊，模板會直接使用其中的 `username`。
2. 房間長期狀態來源只有 `/api/rooms/<room_id>/stream`，不依賴任何 POST response 來更新本地狀態。
3. `heartbeat` 每 5 秒送一次；server 也會每 5 秒送一次 `sync` event。
4. stream 若斷線，模板會自動重連。
5. 落子 API 為 `POST /api/rooms/<room_id>/move`。
6. Armageddon bidding 是 simultaneous sealed bid，提交前看不到對手的 bid。

### 💡 實作提示 (Pro Tips)
* **迭代加深 (Iterative Deepening)**：不要寫死你的搜尋層數（Depth）。寫一個可以在任何時刻透過 Timeout 中斷並回傳「當前最佳解」的迴圈，這是避免超時的關鍵。
* **時間管理**：不要在每一步花費一樣的時間。在開局或只有唯一解圍步時極速落子把時間存起來；並把時間花在強子即將刷新（第 5, 6, 12, 13 手）的關鍵波段上。

**祝你好運，願算力與你同在！**
