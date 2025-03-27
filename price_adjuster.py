import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import subprocess

class PriceAdjusterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("蝦皮價格調整器")
        self.root.geometry("600x400")
        
        # 建立主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL輸入區域
        ttk.Label(main_frame, text="請輸入蝦皮活動網址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 啟動Chrome按鈕
        self.start_chrome_button = ttk.Button(main_frame, text="啟動Chrome", command=self.start_chrome_browser)
        self.start_chrome_button.grid(row=1, column=0, columnspan=3, pady=10)
        
        # 開始調整按鈕
        self.start_button = ttk.Button(main_frame, text="開始調整", command=self.start_adjustment)
        self.start_button.grid(row=2, column=0, columnspan=3, pady=10)
        
        # 狀態顯示區域
        self.status_text = tk.Text(main_frame, height=10, width=50)
        self.status_text.grid(row=3, column=0, columnspan=3, pady=5)
        
        # 捲動條
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=3, column=3, sticky=(tk.N, tk.S))
        self.status_text['yscrollcommand'] = scrollbar.set
        
        self.driver = None
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
    def log_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        
    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            self.log_status(f"等待元素 {value} 超時: {str(e)}")
            return None
            
    def start_chrome_browser(self):
        """啟動Chrome瀏覽器"""
        try:
            url = self.url_entry.get().strip()
            if not url:
                messagebox.showerror("錯誤", "請先輸入網址")
                return
                
            self.log_status("正在啟動Chrome...")
            
            # 啟動Chrome的命令
            chrome_cmd = [
                self.chrome_path,
                '--remote-debugging-port=9222',
                '--remote-allow-origins=*',
                url
            ]
            
            # 執行Chrome
            subprocess.Popen(chrome_cmd)
            self.log_status("Chrome已啟動，請在Chrome中完成登入後再點擊「開始調整」")
            
            # 禁用啟動Chrome按鈕
            self.start_chrome_button.config(state='disabled')
            
        except Exception as e:
            self.log_status(f"啟動Chrome時發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"啟動Chrome失敗: {str(e)}")
            
    def start_chrome(self):
        """連接到已開啟的Chrome瀏覽器"""
        try:
            self.log_status("正在連接到Chrome...")
            
            # 設定Chrome選項
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            # 直接使用 ChromeDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            self.log_status("成功連接到Chrome")
            
        except Exception as e:
            self.log_status(f"連接Chrome時發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"連接Chrome失敗: {str(e)}\n請確保已使用正確的參數啟動Chrome")
            if self.driver:
                self.driver.quit()
                self.driver = None
            
    def start_adjustment(self):
        try:
            # 連接到Chrome
            self.start_chrome()
            
            if not self.driver:
                raise Exception("Chrome驅動程式初始化失敗")
            
            # 等待登入頁面載入
            self.log_status("等待登入頁面載入...")
            time.sleep(5)  # 給予足夠時間載入登入頁面
            
            # 檢查是否需要登入
            if "login" in self.driver.current_url.lower():
                self.log_status("需要登入，請在瀏覽器中手動登入...")
                messagebox.showinfo("登入提示", "請在瀏覽器中手動完成登入，然後點擊確定繼續")
            
            # 確保在正確的網頁
            target_url = self.url_entry.get().strip()
            if target_url not in self.driver.current_url:
                self.log_status(f"正在切換到目標網頁: {target_url}")
                self.driver.get(target_url)
                time.sleep(3)  # 等待頁面載入
            
            # 等待編輯按鈕出現
            self.log_status("等待編輯按鈕出現...")
            edit_button = self.wait_for_element(By.CSS_SELECTOR, "button.eds-button.eds-button--link.eds-button--normal.edit-button")
            
            if edit_button:
                self.log_status("找到編輯按鈕，準備點擊...")
                
                # 移除可能遮擋的元素
                try:
                    self.log_status("嘗試移除遮擋元素...")
                    # 移除遮擋的 content-box
                    self.driver.execute_script("""
                        var elements = document.getElementsByClassName('content-box');
                        for(var i = 0; i < elements.length; i++) {
                            elements[i].style.display = 'none';
                        }
                    """)
                    time.sleep(1)
                except Exception as e:
                    self.log_status(f"移除遮擋元素時發生錯誤: {str(e)}")
                
                # 確保按鈕可見和可點擊
                self.log_status("正在滾動到按鈕位置...")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
                time.sleep(2)  # 等待滾動完成
                
                # 使用 JavaScript 點擊
                self.log_status("使用 JavaScript 點擊按鈕...")
                self.driver.execute_script("""
                    var button = arguments[0];
                    button.style.zIndex = '9999';
                    button.click();
                """, edit_button)
                self.log_status("點擊成功！")
                
                # 等待編輯頁面載入
                self.log_status("等待編輯頁面載入...")
                time.sleep(3)
                
                # 檢查是否成功進入編輯頁面
                current_url = self.driver.current_url
                self.log_status(f"當前URL: {current_url}")
                self.log_status(f"頁面標題: {self.driver.title}")
                
                # 檢查頁面內容
                try:
                    # 檢查是否有編輯相關的元素
                    edit_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='edit'], [class*='Edit'], [class*='EDIT']")
                    if edit_elements:
                        self.log_status("找到編輯相關元素，可能已成功進入編輯畫面！")
                    else:
                        self.log_status("未找到編輯相關元素，可能未成功進入編輯畫面")
                except Exception as e:
                    self.log_status(f"檢查編輯元素時發生錯誤: {str(e)}")
            else:
                self.log_status("錯誤：找不到編輯按鈕")
                # 輸出頁面原始碼以便除錯
                self.log_status("正在獲取頁面原始碼...")
                self.log_status(self.driver.page_source[:500])  # 只顯示前500個字元
            
        except Exception as e:
            self.log_status(f"發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"執行過程中發生錯誤: {str(e)}")
            if self.driver:
                self.driver.quit()
                self.driver = None
            
    def __del__(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceAdjusterGUI(root)
    root.mainloop() 