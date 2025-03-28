"""
介面處理模組 - 負責處理Tkinter用戶界面相關功能

包含功能:
- 創建和管理GUI界面
- 日誌輸出和狀態顯示
- 用戶交互和按鈕功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("介面處理")

class 介面控制:
    """介面控制類，提供Tkinter界面的基本功能"""
    
    def __init__(self, root, main_app=None):
        """初始化界面控制物件"""
        self.root = root
        self.main_app = main_app
        
        # 初始化變數
        self.buttons = []
        self.log_area = None
        self.main_frame = None
        self.url_entry = None
    
    def create_frame(self):
        """創建主框架"""
        # 建立主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 創建URL輸入區域
        url_frame = ttk.Frame(self.main_frame)
        url_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(url_frame, text="蝦皮網址 (選填):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        url_frame.columnconfigure(1, weight=1)
        
        # 創建按鈕框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        self.main_frame.columnconfigure(0, weight=1)
    
    def create_log_area(self):
        """創建日誌顯示區域"""
        # 創建日誌框架
        log_frame = ttk.Frame(self.main_frame)
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.rowconfigure(2, weight=1)
        
        # 創建日誌文本區域
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=25)
        self.log_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 初始歡迎訊息
        self.log_message("歡迎使用蝦皮商品規格調價自動化程式")
        self.log_message("請點擊「啟動Chrome瀏覽器」開始操作")
    
    def get_url(self):
        """獲取URL輸入框的值"""
        if self.url_entry:
            return self.url_entry.get().strip()
        return ""
    
    def add_button(self, text, command, row=None, column=None, width=20):
        """添加按鈕到按鈕框架"""
        if not self.button_frame:
            logger.error("未創建按鈕框架")
            return None
            
        button = ttk.Button(self.button_frame, text=text, command=command, width=width)
        
        if row is None or column is None:
            # 自動排列按鈕
            col_count = len(self.buttons) % 3
            row_count = len(self.buttons) // 3
            button.grid(row=row_count, column=col_count, padx=5, pady=5)
        else:
            button.grid(row=row, column=column, padx=5, pady=5)
            
        self.buttons.append(button)
        return button
    
    def add_label(self, text, row=None, column=None):
        """添加標籤到按鈕框架"""
        if not self.button_frame:
            logger.error("未創建按鈕框架")
            return None
            
        label = ttk.Label(self.button_frame, text=text)
        
        if row is None or column is None:
            # 自動排列標籤
            col_count = len(self.buttons) % 3
            row_count = len(self.buttons) // 3
            label.grid(row=row_count, column=col_count, padx=5, pady=5)
        else:
            label.grid(row=row, column=column, padx=5, pady=5)
            
        return label
    
    def add_entry(self, default_value="", width=5, row=None, column=None):
        """添加輸入框到按鈕框架"""
        if not self.button_frame:
            logger.error("未創建按鈕框架")
            return None
            
        var = tk.StringVar(value=default_value)
        entry = ttk.Entry(self.button_frame, textvariable=var, width=width)
        
        if row is None or column is None:
            # 自動排列輸入框
            col_count = len(self.buttons) % 3
            row_count = len(self.buttons) // 3
            entry.grid(row=row_count, column=col_count, padx=5, pady=5)
        else:
            entry.grid(row=row, column=column, padx=5, pady=5)
            
        return entry
    
    def log_message(self, message):
        """顯示日誌訊息到日誌區域"""
        if self.log_area:
            self.log_area.insert(tk.END, f"{message}\n")
            self.log_area.see(tk.END)
            self.root.update_idletasks()
        else:
            logger.info(message)
    
    def clear_log(self):
        """清空日誌區域"""
        if self.log_area:
            self.log_area.delete(1.0, tk.END)
    
    def show_error_dialog(self, title, message):
        """顯示錯誤對話框"""
        messagebox.showerror(title, message)
    
    def show_warning_dialog(self, title, message):
        """顯示警告對話框"""
        messagebox.showwarning(title, message)
    
    def show_info_dialog(self, title, message):
        """顯示資訊對話框"""
        messagebox.showinfo(title, message)
    
    def show_confirm_dialog(self, title, message):
        """顯示確認對話框"""
        return messagebox.askyesno(title, message)
    
    def show_question_dialog(self, title, message):
        """顯示問題對話框，讓用戶選擇是/否"""
        return messagebox.askyesno(title, message)
    
    # 兼容舊方法名
    def 添加按鈕(self, 文字, 命令, row=0, column=0, padx=10):
        """添加按鈕到按鈕框架 (兼容舊方法名)"""
        return self.add_button(文字, 命令, row, column)
    
    def 日誌訊息(self, message):
        """顯示日誌訊息 (兼容舊方法名)"""
        self.log_message(message)
    
    def 清空日誌(self):
        """清空日誌 (兼容舊方法名)"""
        self.clear_log()
    
    def 顯示錯誤(self, 標題, 訊息):
        """顯示錯誤對話框 (兼容舊方法名)"""
        self.show_error_dialog(標題, 訊息)
    
    def 顯示警告(self, 標題, 訊息):
        """顯示警告對話框 (兼容舊方法名)"""
        self.show_warning_dialog(標題, 訊息)
    
    def 顯示資訊(self, 標題, 訊息):
        """顯示資訊對話框 (兼容舊方法名)"""
        self.show_info_dialog(標題, 訊息)
    
    def 顯示確認(self, 標題, 訊息):
        """顯示確認對話框 (兼容舊方法名)"""
        return self.show_confirm_dialog(標題, 訊息)
    
    def 獲取網址(self):
        """獲取URL輸入框的值 (兼容舊方法名)"""
        return self.get_url()
    
    def 顯示商品分頁(self, products):
        """以分頁方式顯示商品列表"""
        # 清空當前狀態文本
        self.清空日誌()
        
        # 獲取商品總數
        if not products or len(products) == 0:
            self.日誌訊息("未找到任何產品")
            return
        
        # 顯示總共找到的商品數量
        total_products = len(products)
        total_specs = sum(len(product.get('specs', [])) for product in products)
        
        self.日誌訊息("===== 商品分析摘要 =====")
        self.日誌訊息(f"總共找到: {total_products} 個商品, {total_specs} 個規格")
        self.日誌訊息("=" * 80)
        
        # 計算總頁數
        page_size = 10
        total_pages = (total_products + page_size - 1) // page_size
        
        # 創建頁面選擇Frame
        if hasattr(self, 'page_frame') and self.page_frame:
            try:
                self.page_frame.grid_forget()
            except:
                pass
            
        self.page_frame = ttk.Frame(self.main_frame)
        self.page_frame.grid(row=3, column=0, pady=5)
        
        # 頁碼標籤
        self.page_label = ttk.Label(self.page_frame, text=f"頁面 1 / {total_pages}")
        self.page_label.grid(row=0, column=1, padx=5)
        
        # 當前頁面
        self.current_page = 1
        
        # 頁面切換按鈕
        if total_pages > 1:
            self.prev_btn = ttk.Button(self.page_frame, text="上一頁", state="disabled",
                                    command=lambda: self.顯示指定頁商品(products, self.current_page-1, page_size))
            self.prev_btn.grid(row=0, column=0, padx=10)
            
            self.next_btn = ttk.Button(self.page_frame, text="下一頁", 
                                    command=lambda: self.顯示指定頁商品(products, self.current_page+1, page_size))
            self.next_btn.grid(row=0, column=2, padx=10)
        
        # 顯示第一頁商品
        self.顯示指定頁商品(products, 1, page_size)
    
    def 顯示指定頁商品(self, products, page, page_size=10):
        """顯示指定頁碼的商品信息"""
        # 清空當前商品顯示
        self.清空日誌()
        
        # 計算總頁數
        total_products = len(products)
        total_pages = (total_products + page_size - 1) // page_size
        
        # 確保頁碼合法
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
            
        self.current_page = page
        
        # 更新頁碼標籤
        if hasattr(self, 'page_label'):
            self.page_label.config(text=f"頁面 {page} / {total_pages}")
        
        # 更新按鈕狀態
        if hasattr(self, 'prev_btn'):
            self.prev_btn.config(state="normal" if page > 1 else "disabled")
        if hasattr(self, 'next_btn'):
            self.next_btn.config(state="normal" if page < total_pages else "disabled")
        
        # 計算當前頁顯示的商品
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_products)
        
        # 頁面標題使用更明顯的視覺樣式
        self.text_area.tag_configure("page_header", font=("Arial", 11, "bold"), foreground="#1E90FF")
        page_header = f"===== 商品列表 (顯示 {start_idx+1}-{end_idx} / 共 {total_products} 個商品) ====="
        self.text_area.insert(tk.END, page_header + "\n", "page_header")
        
        # 定義視覺樣式
        self.text_area.tag_configure("product_name", font=("Arial", 10, "bold"), foreground="#000080")
        self.text_area.tag_configure("divider", foreground="#A0A0A0")
        self.text_area.tag_configure("stat_label", foreground="#555555")
        self.text_area.tag_configure("stat_value", foreground="#333333", font=("Arial", 9, "bold"))
        self.text_area.tag_configure("high_value", foreground="#006400", font=("Arial", 9, "bold"))
        self.text_area.tag_configure("low_value", foreground="#8B0000", font=("Arial", 9, "bold"))
        self.text_area.tag_configure("spec_preview", foreground="#555555", font=("Arial", 9, "bold"))
        
        # 規格狀態標籤
        self.text_area.tag_configure("status_on", foreground="#006400", font=("Arial", 9, "bold"))
        self.text_area.tag_configure("status_off", foreground="#8B0000", font=("Arial", 9, "bold"))
        self.text_area.tag_configure("status_disabled", foreground="#808080", font=("Arial", 9, "bold"))
        
        # 庫存狀態標籤
        self.text_area.tag_configure("stock_ok", foreground="#006400")
        self.text_area.tag_configure("stock_low", foreground="#FF8C00")
        self.text_area.tag_configure("stock_out", foreground="#8B0000")
        
        # 價格顯示樣式
        self.text_area.tag_configure("price_normal", foreground="#000080")
        self.text_area.tag_configure("price_high", foreground="#8B0000")
        self.text_area.tag_configure("price_low", foreground="#006400")
        
        # 顯示當前頁的商品
        for i in range(start_idx, end_idx):
            product = products[i]
            product_name = product.get('name', f"商品 #{i+1}")
            specs = product.get('specs', [])
            
            # 添加商品標題和分隔線，使用更美觀的格式
            self.text_area.insert(tk.END, f"\n{i+1}. ", "stat_label")
            self.text_area.insert(tk.END, product_name, "product_name")
            self.text_area.insert(tk.END, "\n", "normal")
            self.text_area.insert(tk.END, "-" * 80 + "\n", "divider")
            
            # 規格計數
            total_specs = len(specs)
            open_specs = sum(1 for spec in specs if spec.get('status') == '開啟')
            closed_specs = total_specs - open_specs
            
            # 庫存計數
            in_stock = sum(1 for spec in specs if spec.get('stock') and ''.join(filter(str.isdigit, str(spec.get('stock', '0')))) != '0')
            sold_out = total_specs - in_stock
            
            # 顯示規格統計 (增強的視覺效果)
            self.text_area.insert(tk.END, "規格總數: ", "stat_label")
            self.text_area.insert(tk.END, f"{total_specs}", "stat_value")
            self.text_area.insert(tk.END, " | 開啟狀態: ", "stat_label")
            
            # 根據開啟狀態顯示不同顏色
            if open_specs > 0:
                self.text_area.insert(tk.END, f"{open_specs}", "high_value")
            else:
                self.text_area.insert(tk.END, f"{open_specs}", "low_value")
                
            self.text_area.insert(tk.END, " | 關閉狀態: ", "stat_label")
            
            if closed_specs > 0:
                self.text_area.insert(tk.END, f"{closed_specs}", "low_value")
            else:
                self.text_area.insert(tk.END, f"{closed_specs}", "stat_value")
            
            self.text_area.insert(tk.END, "\n", "normal")
            
            # 顯示庫存統計
            self.text_area.insert(tk.END, "有庫存規格: ", "stat_label")
            
            if in_stock > 0:
                self.text_area.insert(tk.END, f"{in_stock}", "high_value")
            else:
                self.text_area.insert(tk.END, f"{in_stock}", "low_value")
                
            self.text_area.insert(tk.END, " | 售罄規格: ", "stat_label")
            
            if sold_out > 0:
                self.text_area.insert(tk.END, f"{sold_out}", "low_value")
            else:
                self.text_area.insert(tk.END, f"{sold_out}", "stat_value")
                
            self.text_area.insert(tk.END, "\n", "normal")
            
            # 顯示前5個規格的簡要信息
            if specs:
                self.text_area.insert(tk.END, "\n規格預覽:\n", "spec_preview")
                for j, spec in enumerate(specs[:5]):  # 只顯示前5個規格
                    spec_name = spec.get('name', '未知規格')
                    stock = spec.get('stock', '0')
                    price = spec.get('price', '0')
                    status = spec.get('status', '未知')
                    disabled = spec.get('disabled', False)
                    
                    # 處理可能過長的規格名稱
                    if len(spec_name) > 30:
                        spec_name = spec_name[:27] + "..."
                    
                    # 顯示規格名稱
                    self.text_area.insert(tk.END, f"- {spec_name}", "normal")
                    
                    # 顯示庫存 (根據數量使用不同顏色)
                    stock_num = 0
                    try:
                        stock_num = int(''.join(filter(str.isdigit, str(stock))))
                    except:
                        pass
                        
                    self.text_area.insert(tk.END, " | 庫存: ", "stat_label")
                    
                    if stock_num > 10:
                        self.text_area.insert(tk.END, f"{stock}", "stock_ok")
                    elif stock_num > 0:
                        self.text_area.insert(tk.END, f"{stock}", "stock_low")
                    else:
                        self.text_area.insert(tk.END, f"{stock}", "stock_out")
                    
                    # 顯示價格 (根據價格範圍使用不同顏色)
                    price_num = 0
                    try:
                        price_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(price))))
                    except:
                        pass
                        
                    self.text_area.insert(tk.END, " | 價格: ", "stat_label")
                    
                    if price_num > 500:
                        self.text_area.insert(tk.END, f"{price}", "price_high")
                    elif price_num <= 0:
                        self.text_area.insert(tk.END, f"{price}", "price_low") 
                    else:
                        self.text_area.insert(tk.END, f"{price}", "price_normal")
                    
                    # 顯示狀態 (使用不同顏色)
                    self.text_area.insert(tk.END, " | 狀態: ", "stat_label")
                    
                    if status == '開啟':
                        self.text_area.insert(tk.END, status, "status_on")
                    else:
                        self.text_area.insert(tk.END, status, "status_off")
                        
                    if disabled:
                        self.text_area.insert(tk.END, " (已禁用)", "status_disabled")
                        
                    self.text_area.insert(tk.END, "\n", "normal")
                
                if len(specs) > 5:
                    self.text_area.insert(tk.END, f"... 還有 {len(specs) - 5} 個規格未顯示 ...\n", "stat_label")
    
    def 取消處理(self):
        """取消處理並清理界面"""
        # 清空顯示區域
        self.清空日誌()
        self.日誌訊息("處理已取消") 