import random

class BotStrategy:
    def __init__(self, username):
        self.username = username

    def choose_move(self, board, my_color, strong_available, time_left):
        """
        在這裡實作你的 AI 演算法 (Minimax, Alpha-Beta 等)
        board: 2D list, "."=空, "b"=黑一般, "w"=白一般, "B"=黑Strong, "W"=白Strong
        my_color: int, 1=黑, 2=白
        strong_available: int, 手上擁有的 strong 數量
        time_left: float, 剩餘時間 (秒)
        """
        # --- 範例：隨機下棋 (請替換為你的演算法) ---
        empty_spots = []
        for r in range(len(board)):
            for c in range(len(board[r])):
                if board[r][c] == ".":
                    empty_spots.append((r, c))
        
        if empty_spots:
            r, c = random.choice(empty_spots)
            use_strong = (strong_available > 0) # 範例：有就用
            return r, c, use_strong
        
        return 0, 0, False # Fallback

    def choose_bid(self, my_max_bid, default_color):
        """
        在這裡實作你的 Armageddon 競標策略
        目前為 simultaneous sealed bid，對手的 bid 在揭標前不可見
        my_max_bid: float, 你最多可以出的時間 (通常是預設基本時間)
        default_color: str, "black" 或 "white"
        """
        # --- 範例：出 80% 的時間，並選擇黑色 ---
        my_bid = my_max_bid * 0.8
        chosen_color = "black"
        return my_bid, chosen_color
