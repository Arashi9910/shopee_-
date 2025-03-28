"""
價格調整模組

包含與商品規格價格調整相關的功能：
- 調整商品價格
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 設置日誌
logger = logging.getLogger(__name__)

class 價格調整:
    """處理商品規格價格調整相關功能的類"""
    
    def __init__(self, driver):
        """初始化價格調整類
        
        Args:
            driver: Selenium WebDriver實例
        """
        self.driver = driver
        
    def 調整商品價格(self, 商品名稱, 規格名稱, 新價格):
        """調整特定商品規格的價格，使用接近人工操作的方式並實現可靠的重試機制"""
        MAX_RETRIES = 5  # 最大重試次數維持5次
        
        for retry_count in range(MAX_RETRIES):
            try:
                logger.info(f"【重試 {retry_count + 1}/{MAX_RETRIES}】嘗試調整商品 '{商品名稱}' 規格 '{規格名稱}' 的價格為 {新價格}")
                
                # 嘗試直接使用規格名稱找到對應的行
                try:
                    logger.info(f"尋找規格 '{規格名稱}' 的元素...")
                    
                    # 尋找並突出顯示規格行
                    spec_elements = self.driver.find_elements(By.XPATH, f"//div[contains(@class, 'ellipsis-content') and contains(text(), '{規格名稱}')]")
                    
                    if spec_elements:
                        spec_elem = spec_elements[0]
                        logger.info(f"找到規格元素: {規格名稱}")
                        
                        # 使用JavaScript突出顯示元素
                        self.driver.execute_script("arguments[0].style.background='yellow'; arguments[0].scrollIntoView({block: 'center'});", spec_elem)
                        
                        # 向上尋找規格行
                        spec_row = self.driver.execute_script("""
                            let current = arguments[0];
                            for (let i = 0; i < 10; i++) {
                                if (!current) return null;
                                if (current.classList && 
                                   (current.classList.contains('discount-edit-item-model-component') ||
                                    current.classList.contains('discount-edit-item-model-row'))) {
                                    current.style.border = '3px solid blue';
                                    return current;
                                }
                                current = current.parentElement;
                            }
                            return null;
                        """, spec_elem)
                        
                        if spec_row:
                            logger.info("找到完整規格行")
                            
                            # 確保規格開關已開啟
                            switch_elements = spec_row.find_elements(By.CSS_SELECTOR, "div.eds-switch")
                            if switch_elements:
                                switch_elem = switch_elements[0]
                                is_open = 'eds-switch--open' in switch_elem.get_attribute('class')
                                
                                if not is_open:
                                    logger.info("規格開關未開啟，點擊開啟...")
                                    self.driver.execute_script("arguments[0].click();", switch_elem)
                                    time.sleep(3)  # 等待開關切換和UI更新
                            
                            # 找到折扣價欄位（不是原價）
                            try:
                                # 增強的折扣價欄位查找與輸入
                                logger.info("尋找折扣價欄位...")
                                
                                # 使用JavaScript查找帶有NT$前綴的輸入欄位
                                discount_input = self.driver.execute_script("""
                                    const row = arguments[0];
                                    
                                    // 首先查找帶有NT$前綴的輸入框 (最可靠的方法)
                                    const prefixContainers = row.querySelectorAll('.eds-input__inner');
                                    console.log(`找到 ${prefixContainers.length} 個輸入框容器`);
                                    
                                    // 優先處理：查找帶有NT$前綴的輸入框
                                    for (const container of prefixContainers) {
                                        // 檢查是否有NT$前綴
                                        const prefix = container.querySelector('.eds-input__prefix');
                                        if (prefix && prefix.textContent.includes('NT$')) {
                                            console.log('找到帶NT$前綴的輸入框');
                                            
                                            // 獲取實際的input元素
                                            const input = container.querySelector('input.eds-input__input');
                                            if (input) {
                                                // 判斷這是折扣價還是原價
                                                const parent = container.closest('.eds-form-control');
                                                const label = parent ? parent.querySelector('.eds-form-control__label') : null;
                                                const labelText = label ? label.textContent.trim() : '';
                                                                    
                                                // 如果標籤指明是原價，則跳過
                                                if (labelText.includes('原價') || labelText.toLowerCase().includes('original')) {
                                                    console.log('跳過原價輸入框:', labelText);
                                                    continue;
                                                }
                                                
                                                // 不再設置輸入框樣式
                                                console.log('找到折扣價輸入框(NT$前綴)');
                                                return input;
                                            }
                                        }
                                    }
                                    
                                    // 嘗試使用靜態結構定位NT$輸入框 (第一個輸入框通常是特價，第二個是折扣率)
                                    const allInputs = row.querySelectorAll('input.eds-input__input');
                                    if (allInputs.length >= 2) {
                                        // 檢查第一個輸入框是否在帶有NT$的容器中
                                        const firstInput = allInputs[0];
                                        const firstInputParent = firstInput.parentElement;
                                        if (firstInputParent) {
                                            const firstPrefix = firstInputParent.querySelector('.eds-input__prefix');
                                            if (firstPrefix && firstPrefix.textContent.includes('NT$')) {
                                                // 不再設置輸入框樣式
                                                console.log('找到可能的特價輸入框(第一個NT$輸入框)');
                                                return firstInput;
                                            }
                                        }
                                    }
                                    
                                    // 如果沒有找到帶前綴的輸入框，尋找其他常見的折扣價輸入框
                                    // 找到所有價格相關的輸入框和父元素
                                    const priceInputContainers = row.querySelectorAll('.currency-input, .discount-percent-input');
                                    
                                    for (const container of priceInputContainers) {
                                        const input = container.querySelector('input');
                                        if (input) {
                                            // 檢查是否是折扣價輸入框
                                            const isDiscount = container.classList.contains('discount-percent-input') || 
                                                             !container.parentElement.classList.contains('origin-price');
                                            
                                            // 如果找到折扣價輸入框
                                            if (isDiscount) {
                                                // 不再設置輸入框樣式
                                                console.log('找到折扣價輸入框(特殊類名)');
                                                return input;
                                            }
                                        }
                                    }
                                    
                                    // 尋找所有輸入欄位
                                    console.log('找到輸入欄位數量:', allInputs.length);
                                    
                                    // 如果沒有明確的折扣價，查找所有輸入框
                                    if (allInputs.length >= 2) {
                                        // 根據經驗，第一個輸入框通常是特價，第二個是折扣率
                                        // 檢查第一個輸入框數值 - 通常特價大於10，折扣率小於10
                                        const firstValue = allInputs[0].value ? parseFloat(allInputs[0].value) : 0;
                                        const secondValue = allInputs[1].value ? parseFloat(allInputs[1].value) : 0;
                                        
                                        if (firstValue > 10 && secondValue < 10) {
                                            // 值模式符合：第一個是特價，第二個是折扣率
                                            // 不再設置輸入框樣式
                                            console.log('找到可能的特價輸入框(第一個輸入框，值大於10)');
                                            return allInputs[0];
                                        } else if (firstValue < 10 && secondValue > 10) {
                                            // 這種情況不太常見：第一個是折扣率，第二個是特價
                                            // 不再設置輸入框樣式
                                            console.log('找到可能的特價輸入框(第二個輸入框，值大於10)');
                                            return allInputs[1];
                                        } else {
                                            // 無法通過值區分時，默認使用第一個輸入框
                                            // 不再設置輸入框樣式
                                            console.log('找到可能的特價輸入框(預設第一個輸入框)');
                                            return allInputs[0];
                                        }
                                    } else if (allInputs.length === 1) {
                                        // 不再設置輸入框樣式
                                        console.log('找到單個輸入框');
                                        return allInputs[0];
                                    }
                                    
                                    // 嘗試查找"或"後面的輸入框（例如 "NT$499 或 4.9折 24件"）
                                    const priceTexts = row.querySelectorAll('.item-price, .item-content.item-price');
                                    for (const priceText of priceTexts) {
                                        if (priceText.textContent.includes('或')) {
                                            // 點擊這個元素
                                            priceText.click();
                                            console.log('點擊了包含"或"的價格欄位');
                                            
                                            // 等待輸入框出現
                                            setTimeout(() => {
                                                const inputs = row.querySelectorAll('input.eds-input__input');
                                                if (inputs.length > 0) {
                                                    // 尋找表示折扣的輸入框
                                                    for (const input of inputs) {
                                                        // 檢查是否為NT$輸入框
                                                        const parent = input.parentElement;
                                                        const prefix = parent ? parent.querySelector('.eds-input__prefix') : null;
                                                        if (prefix && prefix.textContent.includes('NT$')) {
                                                            input.style.border = '3px solid blue';
                                                            console.log('找到特價輸入框(NT$前綴)');
                                                            return input;
                                                        }
                                                    }
                                                    
                                                    // 如果找不到明確的特價輸入框，返回第一個輸入框
                                                    inputs[0].style.border = '3px solid blue';
                                                    return inputs[0];
                                                }
                                            }, 500);
                                            break;
                                        }
                                    }
                                    
                                    return null;
                                """, spec_row)
                                
                                # 如果沒有找到折扣價輸入框，嘗試點擊折扣價欄位
                                if not discount_input:
                                    logger.info("未找到折扣價輸入框，嘗試點擊折扣價欄位...")
                                    
                                    # 點擊折扣價欄位
                                    clicked = self.driver.execute_script("""
                                        const row = arguments[0];
                                        
                                        // 尋找所有價格欄位
                                        const priceFields = row.querySelectorAll('.item-price, .item-content.item-price, [class*="price"]');
                                        console.log('找到價格欄位:', priceFields.length);
                                        
                                        // 檢查這些欄位中包含折扣信息的
                                        for (const field of priceFields) {
                                            const text = field.textContent.trim();
                                            // 如果價格欄位包含"折"或"或"字樣，可能是折扣價欄位
                                            if (text.includes('折') || text.includes('或')) {
                                                field.scrollIntoView({block: 'center'});
                                                field.style.border = '3px solid red';
                                                field.click();
                                                console.log('點擊了可能的折扣價欄位:', text);
                                                return true;
                                            }
                                        }
                                        
                                        // 如果沒有找到明確的折扣價欄位，嘗試點擊第二個價格欄位
                                        if (priceFields.length >= 2) {
                                            priceFields[1].scrollIntoView({block: 'center'});
                                            priceFields[1].style.border = '3px solid orange';
                                            priceFields[1].click();
                                            console.log('點擊了第二個價格欄位');
                                            return true;
                                        } else if (priceFields.length > 0) {
                                            // 如果只有一個價格欄位，點擊它
                                            priceFields[0].scrollIntoView({block: 'center'});
                                            priceFields[0].style.border = '3px solid yellow';
                                            priceFields[0].click();
                                            console.log('點擊了唯一的價格欄位');
                                            return true;
                                        }
                                        
                                        return false;
                                    """, spec_row)
                                    
                                    if clicked:
                                        logger.info("點擊價格欄位成功，等待輸入框出現...")
                                        time.sleep(2)
                                    
                                        # 再次嘗試找到可能出現的輸入框
                                        discount_input = self.driver.execute_script("""
                                            // 獲取當前焦點元素
                                            const activeElement = document.activeElement;
                                            if (activeElement && activeElement.tagName === 'INPUT') {
                                                activeElement.style.border = '3px solid green';
                                                console.log('找到當前焦點輸入框');
                                                return activeElement;
                                            }
                                            
                                            // 查找所有可見的輸入框
                                            const inputs = document.querySelectorAll('input.eds-input__input:not([disabled])');
                                            for (const input of inputs) {
                                                const rect = input.getBoundingClientRect();
                                                if (rect.width > 0 && rect.height > 0 && input.offsetParent !== null) {
                                                    input.style.border = '3px solid pink';
                                                    console.log('找到可見輸入框');
                                                    return input;
                                                }
                                            }
                                            
                                            return null;
                                        """)
                                
                                if discount_input:
                                    logger.info("✓ 找到折扣價輸入框")
                                    
                                    # 獲取當前值以確認是折扣價還是折扣率
                                    current_value = self.driver.execute_script("return arguments[0].value;", discount_input)
                                    is_discount_rate = False
                                    
                                    if current_value:
                                        try:
                                            current_num = float(current_value)
                                            # 如果當前值小於10，很可能是折扣率而非價格
                                            if current_num < 10:
                                                is_discount_rate = True
                                                logger.info(f"檢測到可能是折扣率輸入框，當前值: {current_value}")
                                        except ValueError:
                                            pass
                                    
                                    # 先清除輸入框的值
                                    self.driver.execute_script("""
                                        // 1. 先確保輸入框有焦點
                                        arguments[0].focus();
                                        // 2. 清空當前值
                                        arguments[0].value = '';
                                        // 3. 觸發輸入事件讓網頁知道值已變化
                                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                    """, discount_input)
                                    time.sleep(0.5)
                                    
                                    # 使用JavaScript設置新值
                                    self.driver.execute_script("""
                                        // 1. 設置新值
                                        arguments[0].value = arguments[1];
                                        // 2. 模擬輸入事件
                                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                    """, discount_input, str(新價格))
                                    
                                    logger.info(f"已設置輸入框值為: {新價格}")
                                    time.sleep(1)
                                    
                                    # 檢查是否出現"無效的價格"錯誤
                                    error_visible = self.driver.execute_script("""
                                        const input = arguments[0];
                                        const errorMsg = input.closest('.eds-form-control') ? 
                                                         input.closest('.eds-form-control').querySelector('.eds-input__error-msg') : 
                                                         document.querySelector('.eds-input__error-msg');
                                        
                                        if (errorMsg && errorMsg.offsetParent !== null && 
                                            errorMsg.textContent.includes('無效的價格')) {
                                            errorMsg.style.border = '2px solid red';
                                            return errorMsg.textContent;
                                        }
                                        return null;
                                    """, discount_input)
                                    
                                    if error_visible:
                                        logger.warning(f"出現錯誤信息: {error_visible}")
                                        
                                        # 如果是折扣率但嘗試輸入價格值，則嘗試輸入折扣率
                                        if is_discount_rate:
                                            logger.info("嘗試作為折扣率重新輸入...")
                                            
                                            # 計算折扣率（假設原價為主站顯示價格的兩倍左右）
                                            discount_rate = min(9.9, round(新價格 / 999.0 * 10, 1))  # 限制最大折扣率為9.9折
                                            
                                            logger.info(f"使用折扣率輸入: {discount_rate}")
                                            
                                            # 再次清除和設置值
                                            self.driver.execute_script("""
                                                arguments[0].focus();
                                                arguments[0].value = '';
                                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                                
                                                arguments[0].value = arguments[1];
                                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                            """, discount_input, str(discount_rate))
                                            
                                            # 等待錯誤信息消失
                                            time.sleep(1.5)
                                    else:
                                        logger.info("未出現價格錯誤，輸入成功")
                                    
                                    # 按Enter確認輸入
                                    self.driver.execute_script("""
                                        arguments[0].dispatchEvent(new KeyboardEvent('keydown', {
                                            key: 'Enter',
                                            code: 'Enter',
                                            keyCode: 13,
                                            which: 13,
                                            bubbles: true
                                        }));
                                    """, discount_input)
                                    
                                    logger.info("按下Enter鍵確認輸入")
                                    time.sleep(1)
                                    
                                    # 增加點擊其他元素來確認更改
                                    self.driver.execute_script("""
                                        document.body.click();
                                    """)
                                    time.sleep(2)  # 等待UI更新
                                    
                                    # 再次檢查是否有錯誤消息
                                    error_still_visible = self.driver.execute_script("""
                                        const errorMsgs = document.querySelectorAll('.eds-input__error-msg');
                                        for (const error of errorMsgs) {
                                            if (error.offsetParent !== null && 
                                                error.textContent.includes('無效的價格')) {
                                                return true;
                                            }
                                        }
                                        return false;
                                    """)
                                    
                                    if not error_still_visible:
                                        logger.info("✓ 沒有檢測到錯誤消息，價格調整成功")
                                        return True
                                    else:
                                        logger.warning("⚠ 依然存在錯誤消息，價格調整可能失敗")
                                else:
                                    logger.warning("⚠ 未找到折扣價輸入框")
                            except Exception as e:
                                logger.warning(f"處理折扣價欄位時發生錯誤: {str(e)}")
                        else:
                            logger.warning("未能找到完整的規格行")
                    else:
                        logger.warning(f"未找到規格元素: {規格名稱}")
                
                except Exception as e:
                    logger.warning(f"處理規格時發生錯誤: {str(e)}")
                
                # 記錄重試訊息
                logger.warning(f"第 {retry_count + 1}/{MAX_RETRIES} 次嘗試失敗，等待後重試...")
                
                # 增加等待時間
                wait_time = 3 + retry_count
                time.sleep(wait_time)
            
            except Exception as e:
                logger.error(f"調整價格時發生未預期的錯誤: {str(e)}")
                time.sleep(3)
        
        logger.error(f"⚠ 經過 {MAX_RETRIES} 次嘗試後仍未能調整價格")
        return False 