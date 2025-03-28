"""
按鈕操作模組

包含與頁面按鈕操作相關的功能：
- 點擊編輯按鈕
- 檢查是否編輯模式
- 進入編輯模式
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 設置日誌
logger = logging.getLogger(__name__)

class 按鈕操作:
    """處理頁面按鈕操作相關功能的類"""
    
    def __init__(self, driver):
        """初始化按鈕操作類
        
        Args:
            driver: Selenium WebDriver實例
        """
        self.driver = driver
    
    def 點擊編輯按鈕(self):
        """尋找並點擊折扣活動編輯按鈕"""
        try:
            logger.info("尋找頁面上的編輯按鈕...")
            
            # 方法1: 使用XPath查找包含「編輯」文字的按鈕
            edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '編輯')]")
            
            # 方法2: 使用多個可能的選擇器
            if not edit_buttons:
                selectors = [
                    ".edit-button",
                    "button.eds-button--primary",
                    "button.activity-edit-btn",
                    ".activity-operation-btn button",
                    ".activity-operation__edit-btn"
                ]
                
                for selector in selectors:
                    temp_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if temp_buttons:
                        for btn in temp_buttons:
                            if "編輯" in btn.text:
                                edit_buttons.append(btn)
            
            # 嘗試點擊找到的編輯按鈕
            if edit_buttons:
                for button in edit_buttons:
                    if button.is_displayed():
                        logger.info(f"找到編輯按鈕: {button.text}")
                        
                        # 滾動到按鈕可見
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # 高亮顯示按鈕
                        self.driver.execute_script("arguments[0].style.border='3px solid red';", button)
                        
                        # 點擊按鈕
                        button.click()
                        logger.info("✓ 成功點擊編輯按鈕")
                        
                        # 等待頁面加載
                        time.sleep(3)
                        return True
            
            # 方法3: 使用JavaScript查找和點擊編輯按鈕
            logger.info("嘗試使用JavaScript查找編輯按鈕...")
            js_result = self.driver.execute_script("""
                // 查找所有按鈕
                const allButtons = document.querySelectorAll('button');
                
                // 遍歷按鈕尋找編輯按鈕
                for (const btn of allButtons) {
                    if (btn.innerText.includes('編輯') && btn.offsetParent !== null) {
                        console.log('找到編輯按鈕:', btn.innerText);
                        btn.scrollIntoView({block: 'center'});
                        btn.style.border = '3px solid green';
                        btn.click();
                        return true;
                    }
                }
                
                // 查找可能的編輯按鈕類名
                const possibleEditButtons = document.querySelectorAll('.edit-button, .eds-button--primary, .activity-edit-btn');
                for (const btn of possibleEditButtons) {
                    if (btn.offsetParent !== null) {
                        console.log('找到可能的編輯按鈕:', btn.innerText);
                        btn.scrollIntoView({block: 'center'});
                        btn.style.border = '3px solid blue';
                        btn.click();
                        return true;
                    }
                }
                
                return false;
            """)
            
            if js_result:
                logger.info("✓ JavaScript成功找到並點擊了編輯按鈕")
                time.sleep(3)
                return True
            
            logger.warning("✗ 未找到編輯按鈕")
            return False
        
        except Exception as e:
            logger.error(f"點擊編輯按鈕時發生錯誤: {str(e)}")
            return False
    
    def 檢查是否編輯模式(self):
        """檢查頁面是否處於編輯模式"""
        try:
            # 方法1: 查找編輯模式特有元素
            edit_mode_indicators = [
                ".discount-edit-item",  # 編輯模式中的商品元素
                ".eds-button--confirm",  # 確認按鈕
                ".eds-switch",  # 開關元素
                ".activity-edit-page"   # 編輯頁面容器
            ]
            
            for selector in edit_mode_indicators:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0 and elements[0].is_displayed():
                    logger.info(f"✓ 檢測到編輯模式元素: {selector}")
                    return True
            
            # 方法2: 使用JavaScript檢查頁面狀態
            js_result = self.driver.execute_script("""
                // 檢查編輯模式的特徵
                const hasEditItems = document.querySelectorAll('.discount-edit-item').length > 0;
                const hasConfirmButton = document.querySelectorAll('.eds-button--confirm').length > 0;
                const hasSwitches = document.querySelectorAll('.eds-switch').length > 0;
                
                // 檢查URL是否包含編輯相關參數
                const isEditUrl = window.location.href.includes('edit') || window.location.href.includes('discount');
                
                return {
                    isEditMode: hasEditItems || hasConfirmButton || hasSwitches,
                    hasEditItems: hasEditItems,
                    hasConfirmButton: hasConfirmButton,
                    hasSwitches: hasSwitches,
                    isEditUrl: isEditUrl
                };
            """)
            
            if js_result and js_result.get('isEditMode', False):
                logger.info(f"✓ JavaScript檢測到編輯模式: {js_result}")
                return True
            
            logger.info("✗ 頁面不在編輯模式")
            return False
            
        except Exception as e:
            logger.error(f"檢查編輯模式時發生錯誤: {str(e)}")
            return False
    
    def 進入編輯模式(self):
        """檢查並進入編輯模式"""
        try:
            # 檢查當前是否已在編輯模式
            if self.檢查是否編輯模式():
                logger.info("✓ 已經處於編輯模式")
                return True
            
            # 尚未進入編輯模式，嘗試點擊編輯按鈕
            logger.info("嘗試進入編輯模式...")
            success = self.點擊編輯按鈕()
            
            if success:
                # 等待頁面加載
                time.sleep(3)
                
                # 再次檢查是否成功進入編輯模式
                if self.檢查是否編輯模式():
                    logger.info("✓ 成功進入編輯模式")
                    return True
                else:
                    logger.warning("⚠ 點擊編輯按鈕後未能進入編輯模式")
            
            # 使用JavaScript嘗試進入編輯模式
            logger.info("嘗試使用JavaScript進入編輯模式...")
            js_result = self.driver.execute_script("""
                // 檢查當前URL並嘗試修改
                const currentUrl = window.location.href;
                
                // 如果URL不包含edit參數，嘗試添加
                if (!currentUrl.includes('/edit')) {
                    // 找到並點擊編輯按鈕
                    const editButtons = document.querySelectorAll('button');
                    for (const btn of editButtons) {
                        if (btn.innerText.includes('編輯') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    
                    // 嘗試直接修改URL
                    if (currentUrl.includes('/discount/')) {
                        const newUrl = currentUrl + '/edit';
                        window.location.href = newUrl;
                        return true;
                    }
                } else {
                    // 已經在編輯模式URL
                    return true;
                }
                
                return false;
            """)
            
            if js_result:
                logger.info("✓ JavaScript嘗試進入編輯模式")
                time.sleep(3)
                
                if self.檢查是否編輯模式():
                    logger.info("✓ 成功進入編輯模式")
                    return True
            
            logger.warning("✗ 無法自動進入編輯模式，請手動操作")
            return False
            
        except Exception as e:
            logger.error(f"進入編輯模式時發生錯誤: {str(e)}")
            return False 