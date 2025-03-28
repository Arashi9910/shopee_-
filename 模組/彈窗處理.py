"""
彈窗處理模組 - 負責處理各種彈窗和對話框

包含功能:
- 檢測頁面中的彈窗
- 處理注意類型彈窗
- 處理折扣活動編輯時的確認彈窗
- 提供多種彈窗操作方法
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("彈窗處理")

class 彈窗處理:
    """專門處理各種彈窗的類"""
    
    def __init__(self, driver):
        """初始化彈窗處理物件"""
        self.driver = driver
    
    def 檢查彈窗存在(self):
        """檢查頁面上是否存在彈窗"""
        try:
            modal_selectors = [
                '.eds-modal__content', 
                '.shopee-modal__container', 
                '[role="dialog"]', 
                '.eds-modal__box',
                '.eds-modal__content--normal',  # 新增特定彈窗的選擇器
                'div[data-v-d2d4c1c8].eds-modal__content'  # 新增特定彈窗的選擇器
            ]
            
            for selector in modal_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0 and elements[0].is_displayed():
                    logger.info(f"找到彈窗: {selector}")
                    return elements[0]  # 返回找到的彈窗元素
            
            return None  # 沒有找到彈窗
        except Exception as e:
            logger.error(f"檢查彈窗時發生錯誤: {str(e)}")
            return None
    
    def 檢查注意彈窗(self):
        """檢查頁面上是否存在「注意」彈窗"""
        try:
            modal_element = self.檢查彈窗存在()
            if not modal_element:
                return False
                
            # 檢查標題是否含有「注意」
            try:
                modal_title = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__title").text
                if "注意" in modal_title:
                    logger.info("檢測到「注意」彈窗")
                    return True
            except:
                pass
                
            return False
        except Exception as e:
            logger.error(f"檢查注意彈窗時發生錯誤: {str(e)}")
            return False
    
    def 檢查折扣編輯彈窗(self):
        """檢查頁面上是否存在折扣編輯彈窗"""
        try:
            modal_element = self.檢查彈窗存在()
            if not modal_element:
                return False
                
            # 檢查標題或內容是否相關
            try:
                # 檢查標題
                try:
                    modal_title = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__title").text
                    if "折扣" in modal_title or "活動" in modal_title:
                        logger.info("檢測到折扣活動相關彈窗")
                        return True
                except:
                    pass
                    
                # 檢查內容
                try:
                    modal_body = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__body").text
                    if ("確認" in modal_body and ("折扣" in modal_body or "活動" in modal_body or "商品" in modal_body)):
                        logger.info("檢測到折扣活動編輯確認彈窗")
                        return True
                except:
                    pass
            except:
                pass
                
            return False
        except Exception as e:
            logger.error(f"檢查折扣編輯彈窗時發生錯誤: {str(e)}")
            return False
    
    def 點擊確認按鈕(self):
        """點擊頁面上的確認按鈕"""
        try:
            logger.info("尋找並點擊確認按鈕...")
            
            # 方法0: 針對特定彈窗結構的直接定位
            try:
                logger.info("嘗試針對特定彈窗結構精確定位確認按鈕...")
                specific_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button[data-v-2e4150da][data-v-d2d4c1c8].eds-button.eds-button--primary")
                
                if specific_buttons:
                    for button in specific_buttons:
                        if button.is_displayed():
                            button_text = button.text
                            logger.info(f"找到特定結構確認按鈕: {button_text}")
                            
                            # 高亮顯示按鈕
                            self.driver.execute_script("arguments[0].style.border='3px solid purple';", button)
                            
                            # 嘗試不同點擊方法
                            click_methods = [
                                lambda b=button: b.click(),  # 標準點擊
                                lambda b=button: self.driver.execute_script("arguments[0].click();", b),  # JS點擊
                                lambda b=button: self.模擬真實點擊(b)  # 模擬真實點擊
                            ]
                            
                            for click_method in click_methods:
                                try:
                                    click_method()
                                    logger.info(f"✓ 成功點擊特定結構確認按鈕: {button_text}")
                                    time.sleep(1)
                                    
                                    # 檢查彈窗是否關閉
                                    if not self.檢查彈窗存在():
                                        return True
                                except Exception as e:
                                    logger.error(f"點擊特定結構確認按鈕失敗: {str(e)}")
            except Exception as e:
                logger.error(f"定位特定結構確認按鈕失敗: {str(e)}")
            
            # 嘗試通過JavaScript精確定位並點擊特定結構的確認按鈕
            try:
                logger.info("嘗試通過JavaScript精確定位特定結構確認按鈕...")
                js_result = self.driver.execute_script("""
                    // 嘗試找到特定結構的確認按鈕
                    const specificButton = document.querySelector('button[data-v-2e4150da][data-v-d2d4c1c8].eds-button.eds-button--primary');
                    if (specificButton && specificButton.offsetParent !== null) {
                        console.log('找到特定結構確認按鈕:', specificButton.innerText);
                        specificButton.style.border = '5px solid gold';  // 標記找到的按鈕
                        specificButton.click();
                        return true;
                    }
                    return false;
                """)
                
                if js_result:
                    logger.info("✓ JavaScript成功找到並點擊特定結構確認按鈕")
                    time.sleep(1)
                    
                    # 檢查彈窗是否關閉
                    if not self.檢查彈窗存在():
                        return True
            except Exception as e:
                logger.error(f"JavaScript定位特定結構確認按鈕失敗: {str(e)}")
            
            # 方法1: 使用CSS選擇器直接查找
            primary_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button.eds-button.eds-button--primary, .eds-modal__footer-buttons .eds-button--primary")
                
            for button in primary_buttons:
                try:
                    if button.is_displayed():
                        button_text = button.text
                        logger.info(f"找到確認按鈕: {button_text}")
                        
                        # 高亮顯示按鈕
                        self.driver.execute_script("arguments[0].style.border='3px solid red';", button)
                        
                        # 滾動到按鈕並點擊
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # 嘗試點擊
                        button.click()
                        logger.info(f"✓ 成功點擊確認按鈕: {button_text}")
                        time.sleep(1)
                        
                        # 檢查彈窗是否關閉
                        if not self.檢查彈窗存在():
                            return True
                except Exception as e:
                    logger.error(f"點擊確認按鈕失敗: {str(e)}")
            
            # 方法2: 使用XPath查找帶有「確認」文字的按鈕
            confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., '確認')]")
            for button in confirm_buttons:
                try:
                    if button.is_displayed():
                        logger.info(f"找到確認按鈕: {button.text}")
                        
                        # 高亮顯示按鈕
                        self.driver.execute_script("arguments[0].style.border='3px solid blue';", button)
                        
                        # 嘗試不同點擊方法
                        methods = [
                            (button.click, "標準點擊"),
                            (lambda: self.driver.execute_script("arguments[0].click();", button), "JavaScript點擊"),
                            (lambda: self.模擬真實點擊(button), "模擬真實點擊")
                        ]
                        
                        for click_method, method_name in methods:
                            try:
                                logger.info(f"嘗試{method_name}...")
                                click_method()
                                time.sleep(1)
                                
                                # 檢查彈窗是否關閉
                                if not self.檢查彈窗存在():
                                    logger.info(f"✓ {method_name}成功關閉彈窗")
                                    return True
                            except Exception as inner_e:
                                logger.error(f"{method_name}失敗: {str(inner_e)}")
                except Exception as e:
                    logger.error(f"處理確認按鈕失敗: {str(e)}")
            
            # 方法3: 使用JavaScript精確查找並點擊按鈕
            js_result = self.driver.execute_script("""
                function clickConfirmButton() {
                    // 尋找帶有'確認'文字的按鈕
                    const buttons = Array.from(document.querySelectorAll('button'));
                    for (const btn of buttons) {
                        if (btn.innerText.includes('確認') && btn.offsetParent !== null) {
                            console.log('找到確認按鈕:', btn.innerText);
                            btn.style.border = '3px solid green';
                            btn.click();
                            return true;
                        }
                    }
                    
                    // 尋找主要按鈕
                    const primaryButtons = document.querySelectorAll('.eds-button--primary');
                    for (const btn of primaryButtons) {
                        if (btn.offsetParent !== null) {
                            console.log('找到主要按鈕:', btn.innerText);
                            btn.style.border = '3px solid yellow';
                            btn.click();
                            return true;
                        }
                    }
                    
                    // 尋找指定CSS類名的按鈕
                    const specificButton = document.querySelector('button[data-v-2e4150da][data-v-d2d4c1c8].eds-button.eds-button--primary');
                    if (specificButton && specificButton.offsetParent !== null) {
                        console.log('找到特定類名按鈕:', specificButton.innerText);
                        specificButton.style.border = '3px solid purple';
                        specificButton.click();
                        return true;
                    }
                    
                    return false;
                }
                
                return clickConfirmButton();
            """)
            
            if js_result:
                logger.info("✓ JavaScript成功找到並點擊確認按鈕")
                time.sleep(1)
                
                # 檢查彈窗是否關閉
                if not self.檢查彈窗存在():
                    return True
            
            logger.warning("✗ 未能找到並點擊確認按鈕")
            return False
            
        except Exception as e:
            logger.error(f"點擊確認按鈕時發生錯誤: {str(e)}")
            return False

    def 處理注意彈窗(self, modal_element=None):
        """專門處理「注意」類型的彈窗"""
        logger.info("開始處理「注意」彈窗...")
        
        if not modal_element:
            modal_element = self.檢查彈窗存在()
            if not modal_element:
                logger.info("未檢測到彈窗，無需處理")
                return True
        
        # 先嘗試處理特定結構的注意彈窗
        if self.處理特定注意彈窗():
            logger.info("✓ 成功處理特定結構「注意」彈窗")
            return True
        
        try:
            # 嘗試點擊確認按鈕
            if self.點擊確認按鈕():
                logger.info("✓ 成功點擊確認按鈕關閉彈窗")
                return True
                
            # 以下是備用方法
            # 讀取彈窗內容
            try:
                modal_body = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__body").text
                logger.info(f"彈窗內容: {modal_body}")
            except:
                pass
            
            # 方法1: 使用JavaScript直接定位並點擊按鈕
            logger.info("方法1: 使用JavaScript直接點擊...")
            js_result = self.driver.execute_script("""
                try {
                    // 直接獲取確認按鈕
                    const confirmButton = document.querySelector('.eds-modal__footer-buttons .eds-button--primary');
                    if (confirmButton) {
                        // 高亮顯示按鈕
                        confirmButton.style.border = '3px solid red';
                        
                        // 記錄按鈕資訊
                        console.log('確認按鈕文字:', confirmButton.innerText);
                        console.log('確認按鈕類名:', confirmButton.className);
                        
                        // 嘗試點擊
                        confirmButton.click();
                        return true;
                    }
                } catch (e) {
                    console.error('JavaScript點擊失敗:', e);
                    return false;
                }
                return false;
            """)
            
            if js_result:
                logger.info("✓ JavaScript方法成功點擊按鈕")
                time.sleep(1)
                
                # 檢查彈窗是否消失
                if not self.檢查彈窗存在():
                    return True
            
            # 方法2: 使用XPath精確定位按鈕
            logger.info("方法2: 使用XPath精確定位...")
            try:
                button = self.driver.find_element(By.XPATH, 
                    "//button[contains(@class, 'eds-button--primary')]//span[contains(text(), '確認')]/parent::button")
                
                if button and button.is_displayed():
                    logger.info(f"找到按鈕: {button.text}")
                    
                    # 標記按鈕
                    self.driver.execute_script("arguments[0].style.border='3px solid blue';", button)
                    
                    # 嘗試點擊方法
                    point_click_methods = [
                        (self.模擬真實點擊, "模擬真實點擊"),
                        (self.JS點擊, "JavaScript點擊"),
                        (self.座標點擊, "座標點擊")
                    ]
                    
                    for click_method, method_name in point_click_methods:
                        logger.info(f"嘗試{method_name}...")
                        if click_method(button):
                            time.sleep(1)
                            if not self.檢查彈窗存在():
                                logger.info(f"✓ {method_name}成功")
                                return True
            except Exception as e:
                logger.error(f"XPath尋找按鈕失敗: {str(e)}")
                
            # 方法3: 直接使用特定選擇器
            logger.info("方法3: 使用特定選擇器...")
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button[data-v-2e4150da][data-v-d2d4c1c8].eds-button.eds-button--primary")
                
                if buttons:
                    for button in buttons:
                        if button.is_displayed():
                            logger.info(f"找到特定類名按鈕: {button.text}")
                            
                            # 標記按鈕
                            self.driver.execute_script("arguments[0].style.border='3px solid purple';", button)
                            
                            # 嘗試點擊
                            button.click()
                            time.sleep(1)
                            
                            # 檢查彈窗是否關閉
                            if not self.檢查彈窗存在():
                                logger.info("✓ 成功點擊特定類名按鈕")
                                return True
            except Exception as e:
                logger.error(f"使用特定選擇器失敗: {str(e)}")
                
            # 方法4: 嘗試發送Escape鍵關閉彈窗
            logger.info("方法4: 使用Escape鍵...")
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            
            if not self.檢查彈窗存在():
                logger.info("✓ Escape鍵成功關閉彈窗")
                return True
            
            logger.warning("❗ 所有自動方法均失敗")
            return False
        
        except Exception as e:
            logger.error(f"處理「注意」彈窗時發生錯誤: {str(e)}")
            return False
    
    def 處理折扣編輯彈窗(self, modal_element):
        """處理折扣活動編輯時出現的彈窗"""
        logger.info("開始處理折扣編輯彈窗...")
        
        try:
            # 讀取彈窗標題和內容
            try:
                modal_title = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__title").text
                modal_body = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__body").text
                logger.info(f"彈窗標題: {modal_title}")
                logger.info(f"彈窗內容: {modal_body}")
            except:
                pass
            
            # 尋找「確認」按鈕 - 多種方式嘗試
            buttons_found = False
            
            # 方法1: 使用文字內容定位確認按鈕
            try:
                # 使用XPath查找包含「確認」文字的按鈕
                confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '確認')]")
                confirm_buttons.extend(self.driver.find_elements(By.XPATH, "//button[contains(., '確認')]"))
                
                if confirm_buttons:
                    buttons_found = True
                    for button in confirm_buttons:
                        if button.is_displayed():
                            logger.info(f"找到確認按鈕: {button.text}")
                            
                            # 嘗試點擊
                            if self.模擬真實點擊(button):
                                time.sleep(1)
                                if not self.檢查彈窗存在():
                                    logger.info("✓ 成功點擊確認按鈕")
                                    return True
                            
                            # 嘗試JavaScript點擊
                            if self.JS點擊(button):
                                time.sleep(1)
                                if not self.檢查彈窗存在():
                                    logger.info("✓ 成功使用JavaScript點擊確認按鈕")
                                    return True
            except Exception as e:
                logger.error(f"尋找確認按鈕失敗: {str(e)}")
            
            # 方法2: 使用CSS選擇器定位確認按鈕
            try:
                confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".eds-modal__footer-buttons .eds-button--primary")
                
                if confirm_buttons:
                    buttons_found = True
                    for button in confirm_buttons:
                        if button.is_displayed():
                            logger.info(f"找到主要按鈕: {button.text}")
                            
                            # 嘗試點擊
                            if self.模擬真實點擊(button):
                                time.sleep(1)
                                if not self.檢查彈窗存在():
                                    logger.info("✓ 成功點擊主要按鈕")
                                    return True
                            
                            # 嘗試JavaScript點擊
                            if self.JS點擊(button):
                                time.sleep(1)
                                if not self.檢查彈窗存在():
                                    logger.info("✓ 成功使用JavaScript點擊主要按鈕")
                                    return True
            except Exception as e:
                logger.error(f"尋找主要按鈕失敗: {str(e)}")
            
            # 方法3: 使用Tab和Enter鍵盤操作
            if not buttons_found:
                logger.info("未找到按鈕，嘗試使用鍵盤操作...")
                if self.鍵盤點擊():
                    time.sleep(1)
                    if not self.檢查彈窗存在():
                        logger.info("✓ 成功使用鍵盤操作關閉彈窗")
                        return True
            
            # 方法4: 嘗試彈窗內的所有按鈕
            try:
                all_buttons = modal_element.find_elements(By.TAG_NAME, "button")
                if all_buttons:
                    buttons_found = True
                    for button in all_buttons:
                        if button.is_displayed():
                            logger.info(f"嘗試點擊彈窗內的按鈕: {button.text}")
                            
                            # 嘗試點擊
                            if self.模擬真實點擊(button):
                                time.sleep(1)
                                if not self.檢查彈窗存在():
                                    logger.info("✓ 成功點擊按鈕")
                                    return True
            except Exception as e:
                logger.error(f"嘗試點擊所有按鈕失敗: {str(e)}")
            
            # 方法5: 使用JavaScript模擬點擊所有可能的確認按鈕
            try:
                js_result = self.driver.execute_script("""
                    // 找到所有可能的確認按鈕
                    function findAndClickConfirmButton() {
                        // 方法1: 查找包含「確認」文字的按鈕
                        const allButtons = document.querySelectorAll('button');
                        for (const btn of allButtons) {
                            if (btn.innerText.includes('確認') && btn.offsetParent !== null) {
                                console.log('找到確認按鈕:', btn.innerText);
                                btn.click();
                                return true;
                            }
                        }
                        
                        // 方法2: 查找主要按鈕
                        const primaryButtons = document.querySelectorAll('.eds-button--primary');
                        for (const btn of primaryButtons) {
                            if (btn.offsetParent !== null) {
                                console.log('找到主要按鈕:', btn.innerText);
                                btn.click();
                                return true;
                            }
                        }
                        
                        // 方法3: 查找彈窗底部按鈕
                        const footerButtons = document.querySelectorAll('.eds-modal__footer-buttons button');
                        for (const btn of footerButtons) {
                            if (btn.offsetParent !== null) {
                                console.log('找到底部按鈕:', btn.innerText);
                                btn.click();
                                return true;
                            }
                        }
                        
                        return false;
                    }
                    
                    return findAndClickConfirmButton();
                """)
                
                if js_result:
                    logger.info("✓ JavaScript成功找到並點擊了按鈕")
                    time.sleep(1)
                    if not self.檢查彈窗存在():
                        return True
            except Exception as e:
                logger.error(f"JavaScript點擊失敗: {str(e)}")
            
            # 方法6: 用Escape嘗試關閉彈窗
            logger.info("嘗試使用Escape鍵關閉彈窗...")
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            
            if not self.檢查彈窗存在():
                logger.info("✓ 成功使用Escape鍵關閉彈窗")
                return True
            
            logger.warning("⚠ 無法自動處理彈窗，請嘗試手動操作")
            return False
        
        except Exception as e:
            logger.error(f"處理折扣編輯彈窗時發生錯誤: {str(e)}")
            return False
    
    def 處理彈窗(self):
        """自動處理頁面上的彈窗"""
        try:
            # 首先檢查是否有彈窗
            modal_element = self.檢查彈窗存在()
            
            if not modal_element:
                logger.info("未發現彈窗，無需處理")
                return False
            
            logger.info("檢測到彈窗，準備處理...")
            
            # 獲取彈窗的文本內容以幫助識別
            modal_text = modal_element.text
            logger.info(f"彈窗內容: {modal_text}")
            
            # 1. 檢查是否是注意彈窗
            if self.檢查注意彈窗():
                logger.info("識別為注意彈窗，進行處理")
                return self.處理注意彈窗(modal_element)
            
            # 2. 檢查是否是折扣編輯彈窗
            if self.檢查折扣編輯彈窗():
                logger.info("識別為折扣編輯彈窗，進行處理")
                return self.處理折扣編輯彈窗(modal_element)
            
            # 3. 嘗試識別編輯確認相關彈窗
            if "編輯" in modal_text or "修改" in modal_text or "確認" in modal_text or "儲存" in modal_text:
                logger.info("可能是編輯相關確認彈窗，嘗試按確認按鈕")
                return self.點擊確認按鈕()
            
            # 4. 嘗試查找所有可能的確認按鈕（通用處理）
            logger.info("未識別特定類型彈窗，使用通用方法處理")
            
            # 嘗試尋找「確定」或「確認」按鈕
            confirm_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(text(), '確定') or contains(text(), '確認') or contains(text(), '保存') or "
                "contains(text(), '儲存') or contains(text(), 'OK') or contains(text(), 'Confirm')]")
            
            for button in confirm_buttons:
                if button.is_displayed() and button.is_enabled():
                    try:
                        logger.info(f"找到確認按鈕: {button.text}")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # 高亮顯示按鈕
                        self.driver.execute_script("arguments[0].style.border='3px solid purple';", button)
                        
                        button.click()
                        logger.info("已點擊確認按鈕")
                        time.sleep(1)
                        
                        # 檢查彈窗是否已關閉
                        if not self.檢查彈窗存在():
                            logger.info("彈窗已關閉")
                            return True
                    except Exception as e:
                        logger.error(f"點擊確認按鈕失敗: {str(e)}")
                        
                        # 嘗試JavaScript點擊
                        try:
                            self.driver.execute_script("arguments[0].click();", button)
                            logger.info("已使用JavaScript點擊確認按鈕")
                            time.sleep(1)
                            
                            if not self.檢查彈窗存在():
                                logger.info("彈窗已關閉")
                                return True
                        except Exception as js_e:
                            logger.error(f"JavaScript點擊確認按鈕失敗: {str(js_e)}")
            
            # 5. 尋找並點擊主要按鈕（通常是主要操作按鈕）
            primary_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button.eds-button--primary, button.shopee-button--primary, button.btn-primary, .primary")
            
            for button in primary_buttons:
                if button.is_displayed() and button.is_enabled():
                    try:
                        logger.info(f"找到主要按鈕: {button.text}")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # 高亮顯示按鈕
                        self.driver.execute_script("arguments[0].style.border='3px solid green';", button)
                        
                        button.click()
                        logger.info("已點擊主要按鈕")
                        time.sleep(1)
                        
                        # 檢查彈窗是否已關閉
                        if not self.檢查彈窗存在():
                            logger.info("彈窗已關閉")
                            return True
                    except Exception as e:
                        logger.error(f"點擊主要按鈕失敗: {str(e)}")
                        
                        # 嘗試JavaScript點擊
                        try:
                            self.driver.execute_script("arguments[0].click();", button)
                            logger.info("已使用JavaScript點擊主要按鈕")
                            time.sleep(1)
                            
                            if not self.檢查彈窗存在():
                                logger.info("彈窗已關閉")
                                return True
                        except Exception as js_e:
                            logger.error(f"JavaScript點擊主要按鈕失敗: {str(js_e)}")
            
            # 6. 嘗試使用JavaScript特殊處理編輯確認按鈕
            logger.info("嘗試使用JavaScript特殊處理彈窗按鈕")
            try:
                button_clicked = self.driver.execute_script("""
                    // 針對特定結構的確認按鈕
                    const specificButton = document.querySelector('button[data-v-2e4150da][data-v-d2d4c1c8].eds-button.eds-button--primary');
                    if (specificButton && specificButton.offsetParent !== null) {
                        console.log('找到特定結構確認按鈕:', specificButton.innerText);
                        specificButton.style.border = '5px solid gold';
                        specificButton.click();
                        return true;
                    }
                    
                    // 查找所有可能的確認按鈕
                    const confirmTexts = ['確認', '確定', '保存', '儲存', 'OK', 'Confirm', 'Save'];
                    
                    for (const text of confirmTexts) {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        for (const btn of buttons) {
                            if (btn.innerText.includes(text) && btn.offsetParent !== null) {
                                console.log(`找到確認按鈕: ${btn.innerText}`);
                                btn.style.border = '3px solid orange';
                                btn.scrollIntoView({block: 'center'});
                                
                                try {
                                    btn.click();
                                    console.log('點擊成功');
                                    return true;
                                } catch (e) {
                                    console.error('點擊失敗:', e);
                                }
                            }
                        }
                    }
                    
                    // 查找主要按鈕
                    const primaryButtons = document.querySelectorAll('.eds-button--primary, .shopee-button--primary, .btn-primary, [class*="primary"]');
                    for (const btn of primaryButtons) {
                        if (btn.offsetParent !== null) {
                            console.log(`找到主要按鈕: ${btn.innerText}`);
                            btn.style.border = '3px solid blue';
                            btn.scrollIntoView({block: 'center'});
                            
                            try {
                                btn.click();
                                console.log('點擊成功');
                                return true;
                            } catch (e) {
                                console.error('點擊失敗:', e);
                            }
                        }
                    }
                    
                    return false;
                """)
                
                if button_clicked:
                    logger.info("JavaScript成功找到並點擊了彈窗按鈕")
                    time.sleep(1)
                    
                    if not self.檢查彈窗存在():
                        logger.info("彈窗已關閉")
                        return True
            except Exception as js_e:
                logger.error(f"JavaScript處理彈窗失敗: {str(js_e)}")
            
            # 如果以上所有方法都失敗，嘗試按ESC鍵關閉彈窗
            try:
                logger.info("嘗試按ESC鍵關閉彈窗")
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
                
                if not self.檢查彈窗存在():
                    logger.info("使用ESC鍵成功關閉彈窗")
                    return True
            except Exception as esc_e:
                logger.error(f"按ESC鍵失敗: {str(esc_e)}")
            
            logger.warning("無法自動處理彈窗")
            return False
            
        except Exception as e:
            logger.error(f"處理彈窗時發生錯誤: {str(e)}")
            import traceback
            logger.error(f"詳細錯誤信息: {traceback.format_exc()}")
            return False
    
    def 模擬真實點擊(self, 元素):
        """模擬真實的人類點擊行為"""
        try:
            # 滾動到元素可見
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 元素)
            time.sleep(0.5)  # 等待滾動完成
            
            # 高亮顯示元素
            self.driver.execute_script("arguments[0].style.border='3px solid red';", 元素)
            
            # 使用ActionChains模擬真實的滑鼠行為
            actions = ActionChains(self.driver)
            actions.move_to_element(元素)  # 移動滑鼠到元素上
            actions.pause(0.5)  # 暫停片刻，模擬人類行為
            actions.click()  # 點擊元素
            actions.perform()  # 執行這些動作
            
            logger.info(f"成功模擬真實點擊: {元素.text if hasattr(元素, 'text') else '元素'}")
            return True
        except Exception as e:
            logger.error(f"模擬真實點擊時發生錯誤: {str(e)}")
            return False
    
    def JS點擊(self, 元素):
        """使用JavaScript點擊元素"""
        try:
            self.driver.execute_script("arguments[0].click();", 元素)
            logger.info("成功使用JavaScript點擊元素")
            return True
        except Exception as e:
            logger.error(f"使用JavaScript點擊元素時發生錯誤: {str(e)}")
            return False
    
    def 座標點擊(self, 元素):
        """使用座標點擊元素"""
        try:
            # 獲取元素座標
            rect = self.driver.execute_script("""
                const rect = arguments[0].getBoundingClientRect();
                return {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                };
            """, 元素)
            
            # 計算元素中心點
            center_x = rect['left'] + rect['width'] / 2
            center_y = rect['top'] + rect['height'] / 2
            
            # 使用ActionChains進行座標點擊
            actions = ActionChains(self.driver)
            actions.move_by_offset(center_x, center_y)
            actions.click()
            actions.perform()
            
            logger.info(f"成功進行座標點擊: x={center_x}, y={center_y}")
            return True
        except Exception as e:
            logger.error(f"座標點擊時發生錯誤: {str(e)}")
            return False
    
    def 鍵盤點擊(self):
        """使用鍵盤模擬點擊（先Tab聚焦，再按Enter）"""
        try:
            # 使用Escape鍵清除當前焦點
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            
            # 使用Tab鍵移動焦點
            for i in range(5):  # 嘗試最多5次Tab
                ActionChains(self.driver).send_keys(Keys.TAB).perform()
                time.sleep(0.3)
            
            # 使用Enter鍵模擬點擊
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            logger.info("成功使用鍵盤模擬點擊")
            return True
        except Exception as e:
            logger.error(f"使用鍵盤模擬點擊時發生錯誤: {str(e)}")
            return False
    
    def 處理特定注意彈窗(self):
        """處理特定結構的「注意」彈窗"""
        try:
            logger.info("嘗試處理特定結構的「注意」彈窗...")
            
            # 使用XPath精確定位特定結構的注意彈窗
            specific_modal = self.driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'eds-modal__content') and .//div[contains(@class, 'eds-modal__title') and text()='注意']]")
            
            if not specific_modal:
                logger.info("未找到特定結構的「注意」彈窗")
                return False
                
            logger.info("找到特定結構的「注意」彈窗，尋找確認按鈕...")
            
            # 精確定位確認按鈕
            confirm_button = None
            try:
                # 方法1: 使用CSS選擇器定位
                confirm_button = self.driver.find_element(By.CSS_SELECTOR, 
                    "button[data-v-2e4150da][data-v-d2d4c1c8].eds-button.eds-button--primary")
                
                if confirm_button and confirm_button.is_displayed():
                    logger.info(f"找到特定結構確認按鈕: {confirm_button.text}")
                    
                    # 高亮顯示按鈕
                    self.driver.execute_script("arguments[0].style.border='5px solid orange';", confirm_button)
                    
                    # 嘗試點擊
                    confirm_button.click()
                    logger.info("✓ 成功點擊特定結構確認按鈕")
                    time.sleep(1)
                    
                    # 檢查彈窗是否關閉
                    if not self.檢查彈窗存在():
                        return True
            except Exception as e:
                logger.error(f"點擊特定結構確認按鈕失敗: {str(e)}")
            
            # 方法2: 使用JavaScript精確定位並點擊
            try:
                js_result = self.driver.execute_script("""
                    // 嘗試找到特定結構的確認按鈕
                    const specificModal = document.querySelector('div[data-v-d2d4c1c8].eds-modal__content');
                    if (specificModal) {
                        const confirmButton = specificModal.querySelector('button[data-v-2e4150da].eds-button--primary');
                        if (confirmButton) {
                            console.log('通過JavaScript找到特定結構確認按鈕:', confirmButton.innerText);
                            confirmButton.style.border = '5px solid lime';  // 標記找到的按鈕
                            confirmButton.click();
                            return true;
                        }
                    }
                    return false;
                """)
                
                if js_result:
                    logger.info("✓ JavaScript成功找到並點擊特定結構確認按鈕")
                    time.sleep(1)
                    
                    # 檢查彈窗是否關閉
                    if not self.檢查彈窗存在():
                        return True
            except Exception as e:
                logger.error(f"JavaScript點擊特定結構確認按鈕失敗: {str(e)}")
            
            return False
        except Exception as e:
            logger.error(f"處理特定結構「注意」彈窗時發生錯誤: {str(e)}")
            return False 