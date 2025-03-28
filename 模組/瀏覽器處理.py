"""
瀏覽器處理模組 - 負責所有瀏覽器相關的操作

包含功能:
- 啟動Chrome瀏覽器
- 連接到已開啟的瀏覽器
- 等待元素加載
- 頁面操作輔助功能
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import subprocess
import time
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("瀏覽器處理")

class 瀏覽器控制:
    """瀏覽器控制類，提供瀏覽器操作的基本功能"""
    
    def __init__(self, chrome_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        """初始化瀏覽器控制物件"""
        self.chrome_path = chrome_path
        self.driver = None
        self.debug_port = 9222
    
    def launch_browser(self, url="", use_debugging=True):
        """啟動Chrome瀏覽器並返回WebDriver對象 (與主程式兼容的方法)"""
        try:
            logger.info("正在啟動Chrome瀏覽器...")
            
            if use_debugging:
                # 啟動可除錯的Chrome (先啟動瀏覽器，後連接)
                if url:
                    # 使用系統命令啟動瀏覽器
                    chrome_cmd = [
                        self.chrome_path,
                        f'--remote-debugging-port={self.debug_port}',
                        '--remote-allow-origins=*',
                        url
                    ]
                    subprocess.Popen(chrome_cmd)
                    time.sleep(3)  # 等待瀏覽器啟動
                
                # 連接到瀏覽器
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info(f"已連接到Chrome瀏覽器，當前URL: {self.driver.current_url}")
            else:
                # 直接啟動新的瀏覽器
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                self.driver = webdriver.Chrome(options=chrome_options)
                
                if url:
                    self.driver.get(url)
                    logger.info(f"導航到URL: {url}")
            
            return self.driver
        except Exception as e:
            logger.error(f"啟動Chrome瀏覽器時發生錯誤: {str(e)}")
            return None

    def connect_to_browser(self):
        """連接到已開啟的Chrome瀏覽器 (與主程式兼容的方法)"""
        try:
            logger.info("正在連接到已開啟的Chrome瀏覽器...")
            
            # 設定Chrome選項
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
            
            # 連接到Chrome瀏覽器
            self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info(f"成功連接到Chrome瀏覽器，當前網址: {self.driver.current_url}")
            return self.driver
        except Exception as e:
            logger.error(f"連接Chrome瀏覽器時發生錯誤: {str(e)}")
            return None
    
    def take_screenshot(self, filename="screenshot.png"):
        """獲取當前頁面的截圖 (與主程式兼容的方法)"""
        try:
            if self.driver:
                self.driver.save_screenshot(filename)
                logger.info(f"截圖已保存到: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"截圖時發生錯誤: {str(e)}")
            return False
    
    def close_browser(self):
        """關閉瀏覽器 (與主程式兼容的方法)"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("成功關閉瀏覽器")
            except Exception as e:
                logger.error(f"關閉瀏覽器時發生錯誤: {str(e)}")
        
    def 啟動瀏覽器(self, url):
        """啟動Chrome瀏覽器並導航到指定網址"""
        try:
            logger.info(f"正在啟動Chrome瀏覽器，訪問 {url}")
            
            # 設定Chrome命令行參數
            chrome_cmd = [
                self.chrome_path,
                f'--remote-debugging-port={self.debug_port}',
                '--remote-allow-origins=*',
                url
            ]
            
            # 執行Chrome
            subprocess.Popen(chrome_cmd)
            
            return True
        except Exception as e:
            logger.error(f"啟動Chrome瀏覽器時發生錯誤: {str(e)}")
            return False
            
    def 連接瀏覽器(self):
        """連接到已開啟的Chrome瀏覽器"""
        try:
            logger.info("正在連接到已開啟的Chrome瀏覽器...")
            
            # 設定Chrome選項
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
            
            # 連接到Chrome瀏覽器
            self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info(f"成功連接到Chrome瀏覽器，當前網址: {self.driver.current_url}")
            return True
        except Exception as e:
            logger.error(f"連接Chrome瀏覽器時發生錯誤: {str(e)}")
            return False
    
    def 等待元素(self, 定位方式, 選擇器, 超時時間=10):
        """等待元素出現在頁面上"""
        try:
            element = WebDriverWait(self.driver, 超時時間).until(
                EC.presence_of_element_located((定位方式, 選擇器))
            )
            return element
        except Exception as e:
            logger.error(f"等待元素 {選擇器} 超時: {str(e)}")
            return None
    
    def 等待元素可見(self, 定位方式, 選擇器, 超時時間=10):
        """等待元素變為可見"""
        try:
            element = WebDriverWait(self.driver, 超時時間).until(
                EC.visibility_of_element_located((定位方式, 選擇器))
            )
            return element
        except Exception as e:
            logger.error(f"等待元素 {選擇器} 變為可見超時: {str(e)}")
            return None
    
    def 等待元素可點擊(self, 定位方式, 選擇器, 超時時間=10):
        """等待元素變為可點擊"""
        try:
            element = WebDriverWait(self.driver, 超時時間).until(
                EC.element_to_be_clickable((定位方式, 選擇器))
            )
            return element
        except Exception as e:
            logger.error(f"等待元素 {選擇器} 變為可點擊超時: {str(e)}")
            return None
    
    def 獲取當前網址(self):
        """獲取當前瀏覽器網址"""
        if self.driver:
            return self.driver.current_url
        return None
    
    def 導航到網址(self, url, 等待時間=3):
        """導航到指定網址"""
        try:
            if self.driver:
                logger.info(f"正在導航到: {url}")
                self.driver.get(url)
                time.sleep(等待時間)  # 等待頁面加載
                return True
            else:
                logger.error("瀏覽器未連接")
                return False
        except Exception as e:
            logger.error(f"導航到網址 {url} 時發生錯誤: {str(e)}")
            return False
    
    def 頁面截圖(self, 檔名="螢幕截圖.png"):
        """獲取當前頁面的截圖"""
        try:
            if self.driver:
                self.driver.save_screenshot(檔名)
                logger.info(f"截圖已保存到: {檔名}")
                return True
            return False
        except Exception as e:
            logger.error(f"截圖時發生錯誤: {str(e)}")
            return False
    
    def 執行JS指令(self, js_代碼, *參數):
        """執行JavaScript代碼"""
        try:
            if self.driver:
                return self.driver.execute_script(js_代碼, *參數)
            return None
        except Exception as e:
            logger.error(f"執行JavaScript代碼時發生錯誤: {str(e)}")
            return None
    
    def 關閉瀏覽器(self):
        """關閉瀏覽器"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("成功關閉瀏覽器")
            except Exception as e:
                logger.error(f"關閉瀏覽器時發生錯誤: {str(e)}")
    
    def __del__(self):
        """確保瀏覽器在物件被銷毀時關閉"""
        self.關閉瀏覽器() 