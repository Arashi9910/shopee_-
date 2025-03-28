import tkinter as tk
from tkinter import ttk, scrolledtext
from playwright.sync_api import sync_playwright
import pygetwindow as gw
import time
import win32gui
import win32con
import math
import re

class RoasCheckerGUI:
    def create_widgets(self):
        """創建GUI元件"""
        # 控制按鈕區域
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=5, padx=10, fill="x")
        
        # 設置區域
        settings_frame = ttk.LabelFrame(control_frame, text="設置")
        settings_frame.pack(fill="x", pady=(0, 5), padx=5)
        
        # 預算調整金額
        budget_frame = ttk.Frame(settings_frame)
        budget_frame.pack(fill="x", pady=2, padx=5)
        ttk.Label(budget_frame, text="預算調整金額:").pack(side="left")
        self.budget_var = tk.StringVar(value="20")
        ttk.Entry(budget_frame, textvariable=self.budget_var, width=10).pack(side="left", padx=5)
        
        # ROAS閾值 (大於)
        roas_frame = ttk.Frame(settings_frame)
        roas_frame.pack(fill="x", pady=2, padx=5)
        ttk.Label(roas_frame, text="ROAS閾值 > ").pack(side="left")
        self.roas_var = tk.StringVar(value="10")
        ttk.Entry(roas_frame, textvariable=self.roas_var, width=10).pack(side="left", padx=5)
        
        # 低ROAS設置框架
        low_roas_frame = ttk.LabelFrame(control_frame, text="低ROAS設置")
        low_roas_frame.pack(fill="x", pady=(0, 5), padx=5)

        # 第一個ROAS範圍設置
        first_roas_frame = ttk.Frame(low_roas_frame)
        first_roas_frame.pack(fill="x", pady=2, padx=5)
        ttk.Label(first_roas_frame, text="第一範圍 ROAS:").pack(side="left")
        self.first_roas_min_var = tk.StringVar(value="5")
        ttk.Entry(first_roas_frame, textvariable=self.first_roas_min_var, width=5).pack(side="left", padx=2)
        ttk.Label(first_roas_frame, text="~").pack(side="left")
        self.first_roas_max_var = tk.StringVar(value="10")
        ttk.Entry(first_roas_frame, textvariable=self.first_roas_max_var, width=5).pack(side="left", padx=2)
        ttk.Label(first_roas_frame, text="預算:").pack(side="left", padx=(10,0))
        self.first_budget_var = tk.StringVar(value="60")
        ttk.Entry(first_roas_frame, textvariable=self.first_budget_var, width=10).pack(side="left", padx=2)

        # 第二個ROAS範圍設置
        second_roas_frame = ttk.Frame(low_roas_frame)
        second_roas_frame.pack(fill="x", pady=2, padx=5)
        ttk.Label(second_roas_frame, text="第二範圍 ROAS ≤").pack(side="left")
        self.second_roas_var = tk.StringVar(value="5")
        ttk.Entry(second_roas_frame, textvariable=self.second_roas_var, width=5).pack(side="left", padx=2)
        ttk.Label(second_roas_frame, text="預算:").pack(side="left", padx=(10,0))
        self.second_budget_var = tk.StringVar(value="40")
        ttk.Entry(second_roas_frame, textvariable=self.second_budget_var, width=10).pack(side="left", padx=2)
        
        # 時間範圍選擇框架
        time_range_select_frame = ttk.LabelFrame(control_frame, text="廣告數據時間範圍")
        time_range_select_frame.pack(fill="x", pady=(0, 5), padx=5)

        # 時間範圍下拉選單
        time_select_frame = ttk.Frame(time_range_select_frame)
        time_select_frame.pack(fill="x", pady=2, padx=5)
        self.time_range_var = tk.StringVar(value="過去一週")
        time_range_combo = ttk.Combobox(time_select_frame, 
            textvariable=self.time_range_var,
            values=["今天", "昨天", "過去一週", "過去一個月", "近三個月"],
            state="readonly",
            width=15)
        time_range_combo.pack(pady=2)
        
        # 定時執行設置
        timer_frame = ttk.LabelFrame(control_frame, text="定時執行設置")
        timer_frame.pack(fill="x", pady=(0, 5), padx=5)
        
        # 執行間隔
        interval_frame = ttk.Frame(timer_frame)
        interval_frame.pack(fill="x", pady=2, padx=5)
        ttk.Label(interval_frame, text="執行間隔(分鐘):").pack(side="left")
        self.interval_var = tk.StringVar(value="30")
        ttk.Entry(interval_frame, textvariable=self.interval_var, width=10).pack(side="left", padx=5)
        
        # 執行時間範圍
        time_range_frame = ttk.Frame(timer_frame)
        time_range_frame.pack(fill="x", pady=2, padx=5)
        
        # 開始時間
        start_time_frame = ttk.Frame(time_range_frame)
        start_time_frame.pack(side="left", padx=(0, 10))
        ttk.Label(start_time_frame, text="開始時間:").pack(side="left")
        self.start_time_var = tk.StringVar(value="00:00")
        ttk.Entry(start_time_frame, textvariable=self.start_time_var, width=8).pack(side="left", padx=5)
        
        # 結束時間
        end_time_frame = ttk.Frame(time_range_frame)
        end_time_frame.pack(side="left")
        ttk.Label(end_time_frame, text="結束時間:").pack(side="left")
        self.end_time_var = tk.StringVar(value="23:59")
        ttk.Entry(end_time_frame, textvariable=self.end_time_var, width=8).pack(side="left", padx=5)
        
        # 添加24小時執行的快捷選項
        self.is_24h_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(time_range_frame, text="24小時執行", 
                        variable=self.is_24h_var,
                        command=self.toggle_24h_mode).pack(side="left", padx=5)
        
        # 自動執行開關
        self.auto_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(timer_frame, text="啟用自動執行", 
                        variable=self.auto_run_var,
                        command=self.toggle_auto_run).pack(pady=2)
        
        # 按鈕區域
        button_frame1 = ttk.Frame(control_frame)
        button_frame1.pack(fill="x", pady=(0, 5))
        
        ttk.Button(button_frame1, text="連接瀏覽器", command=self.connect_browser).pack(side="left", padx=5)
        ttk.Button(button_frame1, text="設置50條/頁", command=self.set_page_size).pack(side="left", padx=5)
        ttk.Button(button_frame1, text="ROI降序排列", command=self.sort_by_roas).pack(side="left", padx=5)
        ttk.Button(button_frame1, text="切換時間範圍", command=self.set_time_range).pack(side="left", padx=5)
        ttk.Button(button_frame1, text="背景化瀏覽器", command=self.toggle_browser_state).pack(side="left", padx=5)
        
        # 執行按鈕區域
        button_frame2 = ttk.Frame(control_frame)
        button_frame2.pack(fill="x", pady=(0, 5))
        
        ttk.Button(button_frame2, text="執行高ROAS調整", 
            command=self.manual_capture,
            style='Accent.TButton').pack(side="left", padx=5)
            
        ttk.Button(button_frame2, text="執行低ROAS調整",
            command=self.execute_low_roas_adjustment,
            style='Accent.TButton').pack(side="left", padx=5)
            
        self.stop_button = ttk.Button(button_frame2, text="停止執行", 
            command=self.stop_execution,
            state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # 日誌顯示區域
        log_frame = ttk.LabelFrame(self.root, text="執行日誌")
        log_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)

        # 統計信息區域
        stats_frame = ttk.LabelFrame(control_frame, text="統計資訊")
        stats_frame.pack(fill="x", pady=(0, 5), padx=5)
        
        # 總調整次數顯示
        self.total_adjustments_var = tk.StringVar(value="總調整次數: 0")
        ttk.Label(stats_frame, textvariable=self.total_adjustments_var).pack(pady=2)
        
        # 最後執行時間
        self.last_run_var = tk.StringVar(value="最後執行: 無")
        ttk.Label(stats_frame, textvariable=self.last_run_var).pack(pady=2)

    def update_statistics(self):
        """更新統計資訊"""
        self.total_adjustments_var.set(f"總調整次數: {self.total_session_adjustments}")
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_run_var.set(f"最後執行: {current_time}")

    def __init__(self, root):
        self.root = root
        self.root.title("蝦皮廣告數據抓取工具")
        self.root.geometry("800x700")
        self.url = "https://seller.shopee.tw/portal/marketing/pas/index?source_page_id=1&from=1732464000&to=1733068799&type=new_cpc_homepage&group=last_week"
        self.browser_hwnd = None

        self.playwright = None
        self.browser = None
        self.page = None
        self.auto_run_timer = None
        
        # 添加總計統計
        self.total_session_adjustments = 0
        
        # 初始化執行狀態
        self.is_running = False
        
        # 初始化低ROAS相關變量
        self.low_roas_min_var = tk.StringVar(value="5")
        self.low_roas_max_var = tk.StringVar(value="10")
        self.first_roas_min_var = tk.StringVar(value="5")
        self.first_roas_max_var = tk.StringVar(value="10")
        self.second_roas_var = tk.StringVar(value="5")
        self.first_budget_var = tk.StringVar(value="60")
        self.second_budget_var = tk.StringVar(value="40")
        
        # 創建界面
        self.create_widgets()

    def toggle_auto_run(self):
        """切換自動執行狀態"""
        if self.auto_run_var.get():
            self.start_auto_run()
        else:
            self.stop_auto_run()

    def is_within_time_range(self, current_time, start_time, end_time):
        """檢查當前時間是否在指定的時間範圍內"""
        # 如果是24小時模式，直接返回True
        if self.is_24h_var.get():
            return True
        
        current_hour, current_minute = map(int, current_time.split(':'))
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        
        current_minutes = current_hour * 60 + current_minute
        start_minutes = start_hour * 60 + start_minute
        end_minutes = end_hour * 60 + end_minute
        
        if end_minutes < start_minutes:  # 跨夜的情況
            return current_minutes >= start_minutes or current_minutes <= end_minutes
        else:
            return start_minutes <= current_minutes <= end_minutes

    def start_auto_run(self):
        """開始自動執行"""
        try:
            # 檢查是否在執行時間範圍內
            current_time = time.strftime("%H:%M")
            start_time = self.start_time_var.get()
            end_time = self.end_time_var.get()
            
            if self.is_within_time_range(current_time, start_time, end_time):
                # 立即執行第一次
                self.log("\n=== 開始自動執行 ===")
                self.manual_capture()
                
                # 設置下一次執行的間隔
                interval = int(self.interval_var.get()) * 60 * 1000  # 轉換為毫秒
                self.auto_run_timer = self.root.after(interval, self.schedule_next_run)
                self.log(f"下一次執行將在 {interval//60000} 分鐘後")
            else:
                self.log(f"當前時間 {current_time} 不在執行時間範圍內 ({start_time} - {end_time})")
                # 仍然設置定時器，以便在到達執行時間時自動開始
                self.schedule_next_run()
                
        except ValueError as e:
            self.log("請輸入有效的執行間隔")
            self.auto_run_var.set(False)
        except Exception as e:
            self.log(f"啟動自動執行時發生錯誤: {str(e)}")
            self.auto_run_var.set(False)

    def stop_auto_run(self):
        """停止自動執行"""
        if self.auto_run_timer:
            self.root.after_cancel(self.auto_run_timer)
            self.auto_run_timer = None
        self.log("自動執行已停止")

    def schedule_next_run(self):
        """安排下一次執行"""
        if not self.auto_run_var.get():
            return
            
        try:
            # 獲取間隔時間
            interval = int(self.interval_var.get()) * 60 * 1000  # 轉換為毫秒
            
            # 如果是24小時模式或在時間範圍內，直接執行
            if self.is_24h_var.get() or self.is_within_time_range(
                time.strftime("%H:%M"), 
                self.start_time_var.get(), 
                self.end_time_var.get()
            ):
                self.manual_capture()
                self.log(f"\n=== 自動執行統計 ===")
                self.log(f"程式運行期間總共調整: {self.total_session_adjustments} 個廣告預算")
                self.log(f"下一次執行將在 {interval//60000} 分鐘後")
            
            # 設置下一次執行
            self.auto_run_timer = self.root.after(interval, self.schedule_next_run)
            
        except Exception as e:
            self.log(f"排程執行失敗: {str(e)}")
            self.auto_run_var.set(False)

    def log(self, message):
        """添加日誌信息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def connect_browser(self):
        """連接到瀏覽器"""
        try:
            if self.playwright:
                self.playwright.stop()
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
            
            # 尋找蝦皮廣告頁面
            target_url = "seller.shopee.tw/portal/marketing/pas/index"
            found_page = None
            
            for page in self.browser.contexts[0].pages:
                if target_url in page.url:
                    # 確認是否為正確的頁面
                    if "source_page_id=1" in page.url:
                        found_page = page
                        break
            
            if found_page:
                self.page = found_page
                self.log("成功連接到蝦皮廣告頁面")
                return True
            else:
                self.log("請確保已打開正確的蝦皮廣告頁面 (source_page_id=1)")
                return False
            
        except Exception as e:
            self.log(f"連接失敗: {str(e)}")
            return False

    def find_chrome_window(self):
        """找到蝦皮廣告的 Chrome 視窗"""
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                print(f"Window found: {title}")  # 添加這行來打印窗口標題
                # 放寬搜尋條件
                if 'Chrome' in title:  # 只要是 Chrome 視窗就先找到
                    self.browser_hwnd = hwnd
                    return False
            return True
        
        win32gui.EnumWindows(callback, None)
        return self.browser_hwnd is not None

    def minimize_browser(self):
        """將瀏覽器視窗最小化"""
        try:
            if self.find_chrome_window():
                win32gui.ShowWindow(self.browser_hwnd, win32con.SW_MINIMIZE)
                self.log("已將瀏覽器最小化")
            else:
                self.log("找不到 Chrome 瀏覽器視窗")
        except Exception as e:
            self.log(f"最小化瀏覽器失敗: {str(e)}")

    def restore_browser(self):
        """還原瀏覽器視窗"""
        try:
            if self.browser_hwnd:
                win32gui.ShowWindow(self.browser_hwnd, win32con.SW_RESTORE)
                self.log("已還原瀏覽器視窗")
            else:
                self.log("找不到瀏覽器視窗句柄")
        except Exception as e:
            self.log(f"還原瀏覽器失敗: {str(e)}")

    def set_time_range(self):
        """設置時間範圍"""
        try:
            
            if not self.page:
                self.log("請先連接瀏覽器")
                return
            
            self.log("正在切換時間範圍...")
            
            # 1. 等待並點擊時間選擇器
            time_selector = self.page.wait_for_selector('div[class*="date-range-picker"]', timeout=5000)
            if not time_selector:
                raise Exception("找不到時間選擇器")
            
            time_selector.click()
            time.sleep(2)
            
            # 2. 根據選擇的時間範圍點擊對應選項
            selected_range = self.time_range_var.get()
            option_text = {
                "今天": "今天",
                "昨天": "昨天",
                "過去一週": "過去一週",
                "過去一個月": "過去一個月",
                "近三個月": "近三個月"
            }.get(selected_range)
            
            if not option_text:
                raise Exception(f"無效的時間範圍選擇: {selected_range}")
            
            # 使用文字內容查找並點擊對應選項
            option = self.page.query_selector(f'li:has-text("{option_text}")')
            if option:
                option.click()
                time.sleep(2)
                self.log(f"成功切換到{selected_range}")
            else:
                raise Exception(f"找不到{selected_range}選項")
            
        except Exception as e:
            self.log(f"切換時間範圍失敗: {str(e)}")


    def sort_by_roas(self):
        """確保ROI為降序排序"""
        try:
            # 等待ROI列的標題元素出現
            self.page.wait_for_selector("th:nth-child(3)", timeout=5000)
            
            # 檢查當前排序狀態
            sort_element = self.page.query_selector("th:nth-child(3) .eds-table__cell-actions")
            sort_class = sort_element.get_attribute("class") if sort_element else ""
            
            if "sort-desc" in sort_class:
                self.log("ROI已經是降序排列")
                return
            
            # 點擊排序按鈕
            self.log("設置ROI降序排列...")
            
            # 嘗試點擊直到成功排序
            max_attempts = 3
            for attempt in range(max_attempts):
                # 點擊排序按鈕
                self.page.click("th:nth-child(3) .eds-table__sort-icons")
                time.sleep(1)  # 等待排序響應
                
                # 檢查排序狀態
                sort_element = self.page.query_selector("th:nth-child(3) .eds-table__cell-actions")
                sort_class = sort_element.get_attribute("class") if sort_element else ""
                
                if "sort-desc" in sort_class:
                    self.log("成功切換到降序排列")
                    return
                elif "sort-asc" in sort_class:
                    self.log("當前為升序，再次點擊切換為降序...")
                    self.page.click("th:nth-child(3) .eds-table__sort-icons")
                    time.sleep(1)
                    
                    # 再次檢查是否成功切換到降序
                    sort_element = self.page.query_selector("th:nth-child(3) .eds-table__cell-actions")
                    sort_class = sort_element.get_attribute("class") if sort_element else ""
                    if "sort-desc" in sort_class:
                        self.log("成功切換到降序排列")
                        return
                
                if attempt < max_attempts - 1:
                    self.log(f"排序未成功，正在重試... (第{attempt + 1}次)")
                    time.sleep(1)
            
            self.log("警告：在多次嘗試後仍未能成功設置降序排列")
            
        except Exception as e:
            self.log(f"排序失敗: {str(e)}")

    def set_page_size(self):
        """設置每頁顯示50條數據"""
        try:
            # 等待分頁大小選擇出現
            self.page.wait_for_selector(".eds-pagination-sizes__content", timeout=5000)
            
            # 檢查當前每頁顯示數量
            current_size = self.page.evaluate("""
                () => {
                    const sizeElement = document.querySelector('.eds-pagination-sizes__content');
                    return sizeElement ? sizeElement.textContent.trim() : '';
                }
            """)
            
            if "50 / page" in current_size:
                self.log("已經設置為每頁顯示50條")
                return
                
            # 點擊下拉選單
            self.log("打開頁面大小選單...")
            self.page.click(".eds-pagination-sizes__content")
            
            # 等待下拉選單出現並選擇50
            self.page.wait_for_selector("li:has-text('50')", timeout=5000)
            self.page.click("li:has-text('50')")
            
            # 等待頁面重新加載
            time.sleep(2)
            
            # 驗證設置
            new_size = self.page.evaluate("""
                () => {
                    const sizeElement = document.querySelector('.eds-pagination-sizes__content');
                    return sizeElement ? sizeElement.textContent.trim() : '';
                }
            """)
            
            if "50 / page" in new_size:
                self.log("成功設置為每頁顯示50條")
            else:
                self.log("警告：頁面大小可能未成功更改")
                
        except Exception as e:
            self.log(f"設置頁面大小失敗: {str(e)}")

    def adjust_budget(self, row_element, current_budget_text):
        """調整預算"""
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                # 使用設置的預算調整金額
                budget_adjust = float(self.budget_var.get())
                current_budget = float(current_budget_text.replace('NT$', '').strip().split()[0])
                target_budget = int(current_budget + budget_adjust)
                
                # 1. 點擊編輯圖標
                edit_icon = row_element.query_selector('td:nth-child(4) div.title i svg')
                if edit_icon:
                    parent_div = row_element.query_selector('td:nth-child(4) div.title')
                    if parent_div:
                        parent_div.hover()
                        time.sleep(1)
                    edit_icon.click()
                    time.sleep(2)
                else:
                    self.log(f"嘗試 {attempt + 1}: 未找到編輯圖標")
                    continue

                # 2. 等待並處理輸入框
                input_xpath = '//body/div[last()]/div/div/div[1]/div[2]/div[1]/div/input'
                input_box = self.page.wait_for_selector(input_xpath, timeout=3000)
                if input_box:
                    input_box.click()
                    input_box.fill(str(target_budget))
                    time.sleep(1)
                else:
                    self.log(f"嘗試 {attempt + 1}: 未找到預算輸入框")
                    self.click_cancel_button()
                    continue

                # 3. 找到並點擊確認按鈕
                confirm_xpath = '//body/div[last()]/div/div/div[2]/button[2]'
                confirm_button = self.page.wait_for_selector(confirm_xpath, timeout=3000)
                if confirm_button:
                    confirm_button.click()
                    time.sleep(2)
                    self.log(f"   預算從 NT${current_budget} 調整為 NT${target_budget}")
                    return True
                else:
                    self.log(f"嘗試 {attempt + 1}: 未找到確認按鈕")
                    self.click_cancel_button()
                    continue

            except Exception as e:
                if "could not convert string to float" in str(e):
                    self.log(f"預算文字解析錯誤，原始文字: '{current_budget_text}'")
                self.log(f"嘗試 {attempt + 1} 失敗: {str(e)}")
                self.click_cancel_button()
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                    continue
                    
        self.log(f"商品預算調整失敗，達到最大重試次數")
        return False

    def click_cancel_button(self):
        """點擊取消按鈕"""
        try:
            cancel_xpath = '//body/div[last()]/div/div/div[2]/button[1]'
            cancel_button = self.page.wait_for_selector(cancel_xpath, timeout=3000)
            if cancel_button:
                cancel_button.click()
            time.sleep(1)
        except Exception as e:
            self.log(f"點擊取消按鈕失敗: {str(e)}")

    def manual_capture(self):
        """手動抓取當前選擇的元素"""
        if not self.page:
            self.log("請先連接瀏覽器")
            return
                
        try:
            # 檢查當前頁面是否為正確的廣告頁面
            if "seller.shopee.tw/portal/marketing/pas/index" not in self.page.url or "source_page_id=1" not in self.page.url:
                self.log("請確保當前頁面為正確的蝦皮廣告頁面")
                return
            
            # 初始化統計數據
            self.total_adjustments = 0
            self.total_pages = 0
            
            # 重新整理頁面
            self.log("正在重新整理頁面...")
            self.page.reload()
            time.sleep(5)  # 等待頁面完全加載
            self.log("頁面重新整理完成")


            # 獲取ROAS閾值
            roas_threshold = float(self.roas_var.get())
            
            # 設置時間範圍
            self.set_time_range()
            time.sleep(2)
            
            # 設置每頁顯示50條
            self.set_page_size()
            time.sleep(2)

            # 先進行ROI排序
            self.sort_by_roas()
            time.sleep(2)

            while True:
                self.total_pages += 1
                self.log(f"\n=== 正在處理第 {self.total_pages} 頁 ===")
                
                # 處理當前頁面
                continue_next_page = self.process_current_page(roas_threshold)
                
                if not continue_next_page:
                    self.log("\n已達到ROAS閾值，停止處理")
                    break
                    
                # 檢查是否有下一頁按鈕且可點擊
                try:
                    # 使用新的 XPath 檢查下一頁按鈕狀態
                    next_button_status = self.page.evaluate('''() => {
                        const nextBtn = document.evaluate(
                            '/html/body/div[1]/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div[3]/div[3]/div[5]/div/div[1]/button[2]',
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;
                        if (!nextBtn) return 'not_found';
                        if (nextBtn.disabled) return 'disabled';
                        return 'clickable';
                    }''')
                    
                    if next_button_status == 'not_found':
                        self.log("\n未找到下一頁按鈕")
                        break
                    elif next_button_status == 'disabled':
                        self.log("\n已到達最後一頁")
                        break
                        
                    # 點擊下一頁
                    self.page.evaluate('''() => {
                        const nextBtn = document.evaluate(
                            '/html/body/div[1]/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div[3]/div[3]/div[5]/div/div[1]/button[2]',
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;
                        if (nextBtn) nextBtn.click();
                    }''')
                    time.sleep(3)  # 等待頁面加載
                    
                except Exception as e:
                    self.log(f"翻頁失敗: {str(e)}")
                    break
            
            # 更新總計統計
            self.total_session_adjustments += self.total_adjustments
            
            # 輸出最終統計
            self.log("\n=== 處理完成 ===")
            self.log(f"本次共處理 {self.total_pages} 頁")
            self.log(f"本次共調整 {self.total_adjustments} 個廣告預算")
            self.log(f"程式運行期間總共調整: {self.total_session_adjustments} 個廣告預算")
            
            # 更新統計顯示
            self.update_statistics()
            # 執行完成後還原瀏覽器
            self.restore_browser()
                        
        except Exception as e:
            self.log(f"抓取失敗: {str(e)}")
            self.log(f"當前頁面URL: {self.page.url}")
            self.restore_browser()

    def process_current_page(self, roas_threshold):
        """處理當前頁面的數據"""
        try:
            js_code = """
            () => {
                const results = [];
                const rows = document.querySelectorAll('div.eds-table tbody tr');
                const totalRows = rows.length / 2;  // 實際行數是顯示行數的一半
                
                for (let i = 0; i < totalRows; i++) {
                    try {
                        // ROI 值從後半部分獲取
                        const roasRow = rows[i + totalRows];
                        const roasElement = roasRow.querySelector('td:nth-child(3) .report-format-number');
                        
                        // 預算值從前半部分獲取
                        const budgetRow = rows[i];
                        const budgetCell = budgetRow.querySelector('td:nth-child(4)');
                        const budgetElement = budgetCell ? budgetCell.querySelector('.ellipsis-content.single') : null;
                        
                        // 檢查預算警告圖標
                        const budgetTipElement = budgetCell ? budgetCell.querySelector('svg[data-name="Layer 1"]') : null;
                        
                        const roasValue = roasElement ? roasElement.textContent.trim() : '';
                        const budgetValue = budgetElement ? budgetElement.textContent.trim().split(' ')[0].replace('NT$', '') : '';
                        
                        if (roasValue || budgetValue) {
                            results.push({
                                roas: roasValue,
                                budget: budgetValue,
                                has_budget_warning: !!budgetTipElement,
                                row_index: i
                            });
                        }
                    } catch (err) {
                        console.error(`解析第 ${i + 1} 行時出錯:`, err);
                    }
                }
                return results;
            }
            """
            
            results = self.page.evaluate(js_code)
            
            if results:
                rows = self.page.query_selector_all('div.eds-table tbody tr')
                total_rows = len(rows) // 2
                
                for i, item in enumerate(results, 1):
                    warning = " ⚠️" if item['has_budget_warning'] else ""
                    
                    # 處理包含 'k' 的 ROAS 值
                    roas_str = item['roas'].lower() if item['roas'] else '0'
                    if 'k' in roas_str:
                        roi = float(roas_str.replace('k', '')) * 1000
                    else:
                        roi = float(roas_str) if roas_str else 0
                    
                    self.log(f"{i}. ROI：{item['roas']}  預算：{item['budget']}{warning}")
                    
                    if roi < float(roas_threshold):
                        return False
                    
                    if item['has_budget_warning']:
                        self.log(f"   正在調整預算...")
                        row = rows[item['row_index']]
                        if self.adjust_budget(row, item['budget']):
                            self.log(f"   預算調整成功")
                            self.total_adjustments += 1
                        else:
                            self.log(f"   預算調整失敗")
                        time.sleep(1)
                
                return True
                
            else:
                self.log("未找到任何數據")
                return False
                
        except Exception as e:
            self.log(f"處理當前頁面失敗: {str(e)}")
            return False
    
    def on_closing(self):
        """關閉程式時清理資源"""
        self.stop_auto_run()
        try:
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        self.root.destroy()

    def toggle_browser_state(self):
        """切換瀏覽器的前景/背景狀態"""
        try:
            if not self.browser_hwnd:
                self.find_chrome_window()
            
            # 獲取當前窗口狀態
            current_state = win32gui.IsIconic(self.browser_hwnd)
            
            if current_state:  # 如果當前是最小化狀態
                self.restore_browser()
                self.log("已將瀏覽器還原到前景")
            else:  # 如果當前是正常狀態
                self.minimize_browser()
                self.log("已將瀏覽器最小化到背景")
            
        except Exception as e:
            self.log(f"切換瀏覽器狀態失敗: {str(e)}")

    def get_average_spend(self, row_element):
        """獲取七日內的平均花費"""
        try:
            # 1. 找到並點擊編輯圖標
            edit_icon = row_element.query_selector('td:nth-child(4) div.title i svg')
            if edit_icon:
                parent_div = row_element.query_selector('td:nth-child(4) div.title')
                if parent_div:
                    parent_div.hover()
                    time.sleep(1)
                parent_div.click()
                time.sleep(3)
            else:
                self.log("未找到編輯圖標")
                return None

            # 2. 等待並獲取平均花費
            try:
                # 獲取當前行的位置信息
                rect = row_element.bounding_box()
                if not rect:
                    self.log("無法獲取行位置")
                    return None
                    
                js_code = """
                (rowY) => {
                    return new Promise((resolve) => {
                        let attempts = 0;
                        const maxAttempts = 20;
                        
                        const checkElement = () => {
                            try {
                                const popups = Array.from(document.querySelectorAll('.budget-edit-cell'));
                                let targetPopup = null;
                                let minDistance = Infinity;
                                
                                popups.forEach(popup => {
                                    if (window.getComputedStyle(popup).display !== 'none') {
                                        const rect = popup.getBoundingClientRect();
                                        const distance = Math.abs(rect.top - rowY);
                                        if (distance < minDistance) {
                                            minDistance = distance;
                                            targetPopup = popup;
                                        }
                                    }
                                });
                                
                                if (targetPopup) {
                                    const tipItems = targetPopup.querySelectorAll('.tip-item');
                                    let avgSpend = null;
                                    
                                    tipItems.forEach(item => {
                                        const text = item.textContent.trim();
                                        if (text.includes('七日內的平均花費')) {
                                            avgSpend = text.split('NT$')[1].trim();
                                        }
                                    });
                                    
                                    resolve({
                                        value: avgSpend,
                                        distance: minDistance
                                    });
                                } else if (attempts >= maxAttempts) {
                                    resolve({ value: null });
                                } else {
                                    attempts++;
                                    setTimeout(checkElement, 500);
                                }
                            } catch (err) {
                                resolve({ value: null, error: err.toString() });
                            }
                        };
                        checkElement();
                    });
                }
                """
                
                result = self.page.evaluate(js_code, rect['y'])
                
                if result.get('error'):
                    self.log(f"JavaScript錯誤: {result['error']}")
                    return None
                
                if result['value']:
                    spend = float(result['value'])
                    self.log(f"七日內的平均花費: NT${spend}")
                    
                    # 3. 點擊取消按鈕關閉編輯框
                    self.click_cancel_button()
                    return spend
                else:
                    self.log("未找到平均花費")
                    self.click_cancel_button()
                    return None
                    
            except Exception as e:
                self.log(f"解析平均花費時出錯: {str(e)}")
                self.click_cancel_button()
                return None
            
        except Exception as e:
            self.log(f"獲取平均花費失敗: {str(e)}")
            self.click_cancel_button()
            return None

    def get_target_budget(self, avg_spend):
        """根據平均花費決定目標預算"""
        if avg_spend <= 40:
            return 40
        elif avg_spend <= 60:
            return 60
        elif avg_spend <= 80:
            return 80
        else:
            # 向上取整到下一個20的倍數
            return math.ceil(avg_spend / 20) * 20

    def test_low_roas_adjustment(self):
        """測試ROAS<10的廣告預算調整"""
        if not self.page:
            self.log("請先連接瀏覽器")
            return
        
        try:
            self.log("\n=== 開始測試低ROAS廣告預算調整 ===")
            
            # 獲取低ROAS範圍
            low_roas_min = float(self.low_roas_min_var.get())
            low_roas_max = float(self.low_roas_max_var.get())
            
            # 重新整理頁面
            self.log("正在重新整理頁面...")
            self.page.reload()
            time.sleep(5)  # 等待頁面完全加載
            self.log("頁面重新整理完成")
            
            # 設置時間範圍
            self.set_time_range()
            time.sleep(2)
            
            # 設置每頁顯示50條
            self.set_page_size()
            time.sleep(2)
            
            # 先進行ROI排序
            self.sort_by_roas()
            time.sleep(2)
            
            # 處理當前頁面
            self.process_low_roas_page(low_roas_min, low_roas_max)
            
            self.log("\n=== 低ROAS廣告預算調整完成 ===")
            self.log(f"本次共調整 {self.total_adjustments} 個廣告預算")
            
            # 執行完成後還原瀏覽器
            self.restore_browser()
            
        except Exception as e:
            self.log(f"執行過程發生錯誤: {str(e)}")
            self.restore_browser()

    def execute_low_roas_adjustment(self):
        """執行低ROAS調整"""
        if not self.page:
            self.log("請先連接瀏覽器")
            return
        
        try:
            self.is_running = True
            self.stop_button.configure(state="normal")
            # 初始化統計數據
            self.total_adjustments = 0
            self.total_pages = 0
            
            # 獲取ROAS範圍
            low_roas_min = float(self.low_roas_min_var.get())
            low_roas_max = float(self.low_roas_max_var.get())
            
            # 重新整理頁面
            self.log("正在重新整理頁面...")
            self.page.reload()
            time.sleep(5)
            self.log("頁面重新整理完成")
            
            # 設置時間範圍
            self.set_time_range()
            time.sleep(2)
            
            # 設置每頁顯示50條
            self.set_page_size()
            time.sleep(2)
            
            # 先進行ROI排序
            self.sort_by_roas()
            time.sleep(2)
            
            while self.is_running:
                self.total_pages += 1
                self.log(f"\n=== 正在處理第 {self.total_pages} 頁 ===")
                
                # 處理當前頁面，傳入ROAS範圍
                self.process_low_roas_page(low_roas_min, low_roas_max)
                
                # 檢查是否有下一頁按鈕且可點擊
                try:
                    # 使用新的 XPath 檢查下一頁按鈕狀態
                    next_button_status = self.page.evaluate('''() => {
                        const nextBtn = document.evaluate(
                            '/html/body/div[1]/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div[3]/div[3]/div[5]/div/div[1]/button[2]',
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;
                        if (!nextBtn) return 'not_found';
                        if (nextBtn.disabled) return 'disabled';
                        return 'clickable';
                    }''')
                    
                    if next_button_status == 'not_found':
                        self.log("\n未找到下一頁按鈕")
                        break
                    elif next_button_status == 'disabled':
                        self.log("\n已到達最後一頁")
                        break
                        
                    # 點擊下一頁
                    self.page.evaluate('''() => {
                        const nextBtn = document.evaluate(
                            '/html/body/div[1]/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div[3]/div[3]/div[5]/div/div[1]/button[2]',
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;
                        if (nextBtn) nextBtn.click();
                    }''')
                    time.sleep(3)  # 等待頁面加載
                    
                except Exception as e:
                    self.log(f"翻頁失敗: {str(e)}")
                    break
            
            # 更新總計統計
            self.total_session_adjustments += self.total_adjustments
            
            # 輸出最終統計
            self.log("\n=== 處理完成 ===")
            self.log(f"本次共處理 {self.total_pages} 頁")
            self.log(f"本次共調整 {self.total_adjustments} 個廣告預算")
            self.log(f"程式運行期間總共調整: {self.total_session_adjustments} 個廣告預算")
            
            # 更新統計顯示
            self.update_statistics()
            # 執行完成後還原瀏覽器
            self.restore_browser()
            
        except Exception as e:
            self.log(f"執行過程發生錯誤: {str(e)}")
            self.restore_browser()

    def process_low_roas_page(self, low_roas_min, low_roas_max):
        """處理當前頁面的低ROAS數據"""
        try:
            js_code = """
            () => {
                const results = [];
                const rows = document.querySelectorAll('div.eds-table tbody tr');
                const totalRows = rows.length / 2;  // 實際行數是顯示行數的一半
                
                for (let i = 0; i < totalRows; i++) {
                    try {
                        // ROI 值從後半部分獲取
                        const roasRow = rows[i + totalRows];
                        const roasElement = roasRow.querySelector('td:nth-child(3) .report-format-number');
                        
                        // 預算值從前半部分獲取
                        const budgetRow = rows[i];
                        const budgetCell = budgetRow.querySelector('td:nth-child(4)');
                        const budgetElement = budgetCell ? budgetCell.querySelector('.ellipsis-content.single') : null;
                        
                        // 獲取商品名稱
                        const nameElement = budgetRow.querySelector('td:nth-child(2)');
                        
                        if (roasElement) {
                            const result = {
                                roas: roasElement.textContent.trim(),
                                budget: budgetElement ? budgetElement.textContent.trim() : '',
                                name: nameElement ? nameElement.textContent.trim() : '未知商品',
                                row_index: i
                            };
                            results.push(result);
                        }
                    } catch (err) {
                        console.error(`解析第 ${i + 1} 行時出錯:`, err);
                    }
                }
                return results;
            }
            """
            
            results = self.page.evaluate(js_code)
            
            if results:
                rows = self.page.query_selector_all('div.eds-table tbody tr')
                total_rows = len(rows) // 2

                for i, item in enumerate(results, 1):
                    if not self.is_running:
                        return False
                    
                    self.root.update()
                    
                    # 處理包含 'k' 的 ROAS 值，並處理 'nt$0.00' 的情況
                    roas_str = item['roas'].lower() if item['roas'] else '0'
                    roas_str = roas_str.replace('nt$', '').replace(',', '')
                    
                    try:
                        if 'k' in roas_str:
                            roi = float(roas_str.replace('k', '')) * 1000
                        else:
                            roi = float(roas_str) if roas_str else 0
                    except ValueError:
                        roi = 0  # 如果無法轉換，設為0
                    
                    # 移除預算中的逗號和NT$符號，並處理可能的格式問題
                    budget_str = item['budget'].replace('NT$', '').replace('nt$', '').replace(',', '').strip()
                    try:
                        current_budget = float(budget_str)
                    except ValueError:
                        current_budget = 0  # 如果無法轉換，設為0
                    
                    self.log(f"\n{i}. 商品：{item['name']}")
                    self.log(f"   ROI：{item['roas']}  預算：{item['budget']}")
                    
                    # 根據不同的ROAS範圍設置目標預算
                    first_roas_min = float(self.first_roas_min_var.get())
                    first_roas_max = float(self.first_roas_max_var.get())
                    second_roas_threshold = float(self.second_roas_var.get())
                    
                    target_budget = None
                    if first_roas_min <= roi <= first_roas_max:
                        target_budget = float(self.first_budget_var.get())
                    elif roi <= second_roas_threshold:
                        target_budget = float(self.second_budget_var.get())
                    
                    if target_budget is not None:
                        row = rows[item['row_index']]
                        if self.adjust_budget_with_target(row, current_budget, target_budget, item['name']):
                            self.total_adjustments += 1
                    
                    self.root.update()
                
                return True
                
            else:
                self.log("未找到任何數據")
                return False
                
        except Exception as e:
            self.log(f"處理當前頁面失敗: {str(e)}")
            return False

    def adjust_budget_with_target(self, row_element, current_budget, target_budget, product_name):
        """根據指定的目標預算進行調整"""
        try:
            # 檢查是否需要調整
            if abs(current_budget - target_budget) < 1:  # 允許1元誤差
                self.log(f"   當前預算 NT${current_budget} 已經接近目標預算 NT${target_budget}，無需調整")
                return True

            # 找到並點擊編輯圖標
            edit_icon = row_element.query_selector('td:nth-child(4) div.title i svg')
            if not edit_icon:
                self.log("未找到編輯圖標")
                return False

            parent_div = row_element.query_selector('td:nth-child(4) div.title')
            if parent_div:
                parent_div.hover()
                time.sleep(1)
            edit_icon.click()
            time.sleep(2)

            # 調整預算
            input_xpath = '//body/div[last()]/div/div/div[1]/div[2]/div[1]/div/input'
            input_box = self.page.wait_for_selector(input_xpath, timeout=3000)
            if input_box:
                input_box.click()
                input_box.fill(str(int(target_budget)))
                time.sleep(1)

                # 確認修改
                confirm_xpath = '//body/div[last()]/div/div/div[2]/button[2]'
                confirm_button = self.page.wait_for_selector(confirm_xpath, timeout=3000)
                if confirm_button:
                    confirm_button.click()
                    time.sleep(2)
                    self.log(f"✅ 預算調整成功\n   商品：{product_name}\n   從 NT${current_budget} 調整為 NT${target_budget}")
                    return True
                else:
                    self.log("未找到確認按鈕")
                    self.click_cancel_button()
            else:
                self.log("未找到預算輸入框")
                self.click_cancel_button()

        except Exception as e:
            self.log(f"調整預算失敗: {str(e)}")
            self.click_cancel_button()
        
        return False

    def get_average_spend_from_popup(self):
        """從已打開的編輯框中獲取平均花費"""
        try:
            # 等待平均花費元素出現
            avg_spend_element = self.page.wait_for_selector('div.budget-edit-cell__average-spend', timeout=3000)
            if avg_spend_element:
                avg_spend_text = avg_spend_element.text_content()
                # 提取數字
                avg_spend = float(re.search(r'NT\$\s*([\d,.]+)', avg_spend_text).group(1).replace(',', ''))
                return avg_spend
            return None
        except Exception as e:
            self.log(f"獲取平均花費失敗: {str(e)}")
            return None

    def stop_execution(self):
        """停止執行"""
        self.is_running = False
        self.stop_button.configure(state="disabled")
        self.log("\n=== 執行已停止 ===")
        self.log(f"本次共調整 {self.total_adjustments} 個廣告預算")

    def toggle_24h_mode(self):
        """切換24小時執行模式"""
        if self.is_24h_var.get():
            self.start_time_var.set("00:00")
            self.end_time_var.set("23:59")
            # 禁用時間輸入
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Entry) and (widget.get() == "00:00" or widget.get() == "23:59"):
                    widget.configure(state="disabled")
        else:
            # 啟用時間輸入
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Entry) and (widget.get() == "00:00" or widget.get() == "23:59"):
                    widget.configure(state="normal")

def main():
    root = tk.Tk()
    app = RoasCheckerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()