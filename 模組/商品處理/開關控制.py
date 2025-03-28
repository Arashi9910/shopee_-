"""
開關控制模組

包含與商品規格開關控制相關的功能：
- 切換商品規格開關
- 處理需要開啟的規格
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 設置日誌
logger = logging.getLogger(__name__)

class 開關控制:
    """處理商品規格開關控制相關功能的類"""
    
    def __init__(self, driver):
        """初始化開關控制類
        
        Args:
            driver: Selenium WebDriver實例
        """
        self.driver = driver
        
    def 切換商品規格開關(self, 商品名稱, 規格名稱):
        """切換特定商品規格的開關"""
        try:
            logger.info(f"嘗試切換商品 '{商品名稱}' 規格 '{規格名稱}' 的開關...")
            
            # 使用JavaScript查找並操作開關
            result = self.driver.execute_script("""
                function findAndToggleSwitch(productName, specName) {
                    console.log('嘗試尋找開關，商品: ' + productName + ', 規格: ' + specName);
                    
                    // 首先在編輯模式下尋找
                    // 1. 尋找商品容器
                    let productContainer = null;
                    const productContainers = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                    
                    for (const container of productContainers) {
                        const nameEl = container.querySelector('div.ellipsis-content.single');
                        if (nameEl && nameEl.innerText.trim() === productName) {
                            productContainer = container;
                            console.log('找到商品容器');
                            break;
                        }
                    }
                    
                    // 2. 如果找到商品容器，查找規格和對應的開關
                    if (productContainer) {
                        // 尋找規格元素
                        const specElements = productContainer.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                        
                        for (const specElement of specElements) {
                            const specNameEl = specElement.querySelector('div.ellipsis-content.single');
                            if (specNameEl && specNameEl.innerText.trim() === specName) {
                                console.log('找到規格元素');
                                
                                // 尋找開關元素
                                const switchEl = specElement.querySelector('div.eds-switch');
                                if (switchEl) {
                                    console.log('找到開關元素');
                                    
                                    // 檢查開關狀態
                                    const isOpen = switchEl.classList.contains('eds-switch--open');
                                    const isDisabled = switchEl.classList.contains('eds-switch--disabled');
                                    
                                    if (isDisabled) {
                                        return { success: false, message: "開關已被禁用，無法操作" };
                                    }
                                    
                                    if (isOpen) {
                                        return { success: true, message: "開關已經是開啟狀態" };
                                    }
                                    
                                    // 在控制台記錄找到的開關
                                    console.log('找到需要點擊的開關元素，準備點擊');
                                    
                                    // 滾動到開關位置並點擊
                                    switchEl.scrollIntoView({block: 'center'});
                                    setTimeout(() => {
                                        try {
                                            switchEl.click();
                                            console.log('開關已點擊');
                                        } catch(e) {
                                            console.error('點擊開關失敗: ' + e);
                                        }
                                    }, 300);
                                    
                                    return { success: true, message: "已點擊開關" };
                                }
                            }
                        }
                    }
                    
                    // 如果無法通過商品名和規格名找到，嘗試只通過規格名查找
                    console.log('通過商品名找不到，嘗試只用規格名查找');
                    
                    // 尋找所有包含規格名的元素
                    const specElems = document.querySelectorAll('div.ellipsis-content.single');
                    for (const elem of specElems) {
                        if (elem.innerText.trim() === specName) {
                            console.log('找到規格名稱匹配的元素');
                            
                            // 向上查找開關容器
                            let current = elem;
                            let foundSwitch = null;
                            for (let i = 0; i < 5; i++) {
                                if (!current) break;
                                
                                // 嘗試在當前元素中找開關
                                const switchEls = current.querySelectorAll('div.eds-switch');
                                if (switchEls.length > 0) {
                                    foundSwitch = switchEls[0];
                                    break;
                                }
                                
                                // 向上級查找
                                current = current.parentElement;
                                if (current) {
                                    // 在父元素中查找開關
                                    const parentSwitches = current.querySelectorAll('div.eds-switch');
                                    if (parentSwitches.length > 0) {
                                        foundSwitch = parentSwitches[0];
                                        break;
                                    }
                                }
                            }
                            
                            if (foundSwitch) {
                                console.log('找到開關');
                                
                                // 檢查開關狀態
                                const isOpen = foundSwitch.classList.contains('eds-switch--open');
                                const isDisabled = foundSwitch.classList.contains('eds-switch--disabled');
                                
                                if (isDisabled) {
                                    return { success: false, message: "開關已被禁用，無法操作" };
                                }
                                
                                if (isOpen) {
                                    return { success: true, message: "開關已經是開啟狀態" };
                                }
                                
                                // 在控制台記錄找到的開關
                                console.log('找到需要點擊的開關元素（通過規格名），準備點擊');
                                
                                // 滾動到開關位置並點擊
                                foundSwitch.scrollIntoView({block: 'center'});
                                setTimeout(() => {
                                    try {
                                        foundSwitch.click();
                                        console.log('開關已點擊');
                                    } catch(e) {
                                        console.error('點擊開關失敗: ' + e);
                                    }
                                }, 300);
                                
                                return { success: true, message: "已點擊開關" };
                            }
                        }
                    }
                    
                    return { success: false, message: "找不到對應的開關" };
                }
                
                return findAndToggleSwitch(arguments[0], arguments[1]);
            """, 商品名稱, 規格名稱)
            
            # 等待JavaScript操作完成
            time.sleep(1)
            
            if result and result.get("success", False):
                logger.info(f"✓ {result.get('message', '開關操作成功')}")
                return True
            else:
                error_message = result.get("message", "未知錯誤") if result else "JavaScript執行失敗"
                logger.error(f"✗ {error_message}")
                return False
                
        except Exception as e:
            logger.error(f"切換開關時發生錯誤: {str(e)}")
            return False
    
    def 處理需要開啟的規格(self, products):
        """處理所有需要開啟的規格"""
        total_processed = 0
        total_success = 0
        
        logger.info("開始處理需要開啟的規格...")
        
        for product in products:
            product_name = product.get('name', '未知商品')
            specs = product.get('specs', [])
            
            logger.info(f"處理商品: {product_name}")
            
            for spec in specs:
                spec_name = spec.get('name', '未知規格')
                stock = spec.get('stock', '0')
                status = spec.get('status', '未知')
                disabled = spec.get('disabled', False)
                
                # 嘗試提取庫存數字
                try:
                    stock_number = int(''.join(filter(str.isdigit, str(stock))))
                except:
                    stock_number = 0
                
                # 確定操作動作
                if stock_number > 0 and not disabled:
                    if status != "開啟":
                        logger.info(f"規格 '{spec_name}' 需要開啟")
                        total_processed += 1
                        
                        # 執行開啟操作
                        result = self.切換商品規格開關(product_name, spec_name)
                        if result:
                            logger.info(f"✓ 已成功開啟 {spec_name} 的開關")
                            total_success += 1
                        else:
                            logger.error(f"✗ 開啟 {spec_name} 的開關失敗")
                        
                        # 等待操作完成
                        time.sleep(0.5)
        
        logger.info(f"處理完成，共處理 {total_processed} 個規格，成功 {total_success} 個")
        return total_success, total_processed
    
    def 開啟規格(self, 商品名稱, 規格名稱):
        """開啟特定商品規格
        
        Args:
            商品名稱 (str): 商品名稱
            規格名稱 (str): 規格名稱
            
        Returns:
            bool: 是否成功開啟規格
        """
        logger.info(f"嘗試開啟商品 '{商品名稱}' 的規格 '{規格名稱}'")
        MAX_RETRIES = 3
        
        for retry in range(MAX_RETRIES):
            try:
                logger.info(f"第 {retry + 1}/{MAX_RETRIES} 次尋找規格開關...")
                
                # 尋找規格元素
                spec_elements = self.driver.find_elements(By.XPATH, f"//div[contains(@class, 'ellipsis-content') and contains(text(), '{規格名稱}')]")
                
                if not spec_elements:
                    logger.warning(f"未找到規格元素: {規格名稱}")
                    time.sleep(1)
                    continue
                
                spec_elem = spec_elements[0]
                logger.info(f"找到規格元素: {規格名稱}")
                
                # 滾動使元素可見，但不改變背景色
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", spec_elem)
                time.sleep(0.5)
                
                # 向上尋找規格行
                spec_row = self.driver.execute_script("""
                    let current = arguments[0];
                    for (let i = 0; i < 10; i++) {
                        if (!current) return null;
                        if (current.classList && 
                           (current.classList.contains('discount-edit-item-model-component') ||
                            current.classList.contains('discount-edit-item-model-row'))) {
                            // 找到元素但不改變其樣式
                            return current;
                        }
                        current = current.parentElement;
                    }
                    return null;
                """, spec_elem)
                
                if not spec_row:
                    logger.warning("未找到完整規格行")
                    time.sleep(1)
                    continue
                
                logger.info("找到完整規格行")
                
                # 尋找開關元素
                switch_elements = spec_row.find_elements(By.CSS_SELECTOR, "div.eds-switch")
                if not switch_elements:
                    logger.warning("未找到開關元素")
                    time.sleep(1)
                    continue
                
                switch_elem = switch_elements[0]
                is_open = 'eds-switch--open' in switch_elem.get_attribute('class')
                
                # 如果已經開啟，不需要操作
                if is_open:
                    logger.info(f"規格 '{規格名稱}' 已經處於開啟狀態")
                    return True
                
                # 點擊開關
                logger.info("點擊開關按鈕...")
                self.driver.execute_script("arguments[0].click();", switch_elem)
                time.sleep(2)  # 等待開關狀態變更
                
                # 檢查開關狀態是否已更改
                is_open_after = 'eds-switch--open' in switch_elem.get_attribute('class')
                if is_open_after:
                    logger.info(f"✓ 成功開啟規格 '{規格名稱}'")
                    return True
                else:
                    logger.warning(f"點擊後開關狀態未變更，重試...")
            
            except Exception as e:
                logger.error(f"開啟規格時發生錯誤: {str(e)}")
            
            time.sleep(1)
        
        logger.error(f"⚠ 無法開啟規格 '{規格名稱}'，已達最大重試次數")
        return False 