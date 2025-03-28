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
            
            # 使用JavaScript查找並操作開關，同時加強視覺效果
            result = self.driver.execute_script("""
                function findAndToggleSwitch(productName, specName) {
                    console.log('嘗試尋找開關，商品: ' + productName + ', 規格: ' + specName);
                    
                    // 高亮顯示操作中的商品和規格，方便用戶定位
                    function highlightElement(element, color, duration) {
                        if (!element) return;
                        
                        // 保存原始樣式
                        const originalBackground = element.style.backgroundColor;
                        const originalTransition = element.style.transition;
                        const originalBoxShadow = element.style.boxShadow;
                        
                        // 設置高亮樣式
                        element.style.transition = 'background-color 0.3s, box-shadow 0.3s';
                        element.style.backgroundColor = color;
                        element.style.boxShadow = '0 0 8px ' + color;
                        
                        // 在指定時間後恢復原始樣式
                        if (duration) {
                            setTimeout(() => {
                                element.style.backgroundColor = originalBackground;
                                element.style.boxShadow = originalBoxShadow;
                                setTimeout(() => {
                                    element.style.transition = originalTransition;
                                }, 300);
                            }, duration);
                        }
                    }
                    
                    // 首先在編輯模式下尋找
                    // 1. 尋找商品容器
                    let productContainer = null;
                    const productContainers = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                    
                    for (const container of productContainers) {
                        const nameEl = container.querySelector('div.ellipsis-content.single');
                        if (nameEl && nameEl.innerText.trim() === productName) {
                            productContainer = container;
                            console.log('找到商品容器');
                            // 高亮商品容器
                            highlightElement(container, 'rgba(144, 238, 144, 0.2)', 2000);
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
                                // 高亮規格元素
                                highlightElement(specElement, 'rgba(135, 206, 250, 0.3)', 3000);
                                
                                // 尋找開關元素
                                const switchEl = specElement.querySelector('div.eds-switch');
                                if (switchEl) {
                                    console.log('找到開關元素');
                                    
                                    // 檢查開關狀態
                                    const isOpen = switchEl.classList.contains('eds-switch--open');
                                    const isDisabled = switchEl.classList.contains('eds-switch--disabled');
                                    
                                    if (isDisabled) {
                                        // 標記禁用的開關
                                        highlightElement(switchEl, 'rgba(220, 20, 60, 0.3)', 2000);
                                        return { success: false, message: "開關已被禁用，無法操作" };
                                    }
                                    
                                    if (isOpen) {
                                        // 標記已開啟的開關
                                        highlightElement(switchEl, 'rgba(46, 139, 87, 0.4)', 2000);
                                        return { success: true, message: "開關已經是開啟狀態" };
                                    }
                                    
                                    // 在控制台記錄找到的開關
                                    console.log('找到需要點擊的開關元素，準備點擊');
                                    
                                    // 滾動到開關位置
                                    switchEl.scrollIntoView({block: 'center', behavior: 'smooth'});
                                    
                                    // 高亮開關並添加動畫效果
                                    highlightElement(switchEl, 'rgba(255, 215, 0, 0.5)', 3000);
                                    
                                    setTimeout(() => {
                                        try {
                                            switchEl.click();
                                            console.log('開關已點擊');
                                            
                                            // 點擊後再次高亮以顯示成功
                                            setTimeout(() => {
                                                if (switchEl.classList.contains('eds-switch--open')) {
                                                    highlightElement(switchEl, 'rgba(46, 139, 87, 0.4)', 2000);
                                                }
                                            }, 500);
                                        } catch(e) {
                                            console.error('點擊開關失敗: ' + e);
                                            highlightElement(switchEl, 'rgba(220, 20, 60, 0.3)', 2000);
                                        }
                                    }, 500);
                                    
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
                            // 高亮規格名稱元素
                            highlightElement(elem, 'rgba(135, 206, 250, 0.3)', 3000);
                            
                            // 向上查找開關容器
                            let current = elem;
                            let foundSwitch = null;
                            
                            // 向上查找最近的規格容器
                            let specContainer = null;
                            for (let i = 0; i < 5; i++) {
                                if (!current) break;
                                
                                if (current.classList && 
                                    (current.classList.contains('discount-view-item-model-component') || 
                                     current.classList.contains('discount-edit-item-model-component'))) {
                                    specContainer = current;
                                    break;
                                }
                                current = current.parentElement;
                            }
                            
                            // 如果找到規格容器，高亮顯示
                            if (specContainer) {
                                highlightElement(specContainer, 'rgba(135, 206, 250, 0.2)', 3000);
                            }
                            
                            // 重新從規格名稱元素開始查找
                            current = elem;
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
                                    // 標記禁用的開關
                                    highlightElement(foundSwitch, 'rgba(220, 20, 60, 0.3)', 2000);
                                    return { success: false, message: "開關已被禁用，無法操作" };
                                }
                                
                                if (isOpen) {
                                    // 標記已開啟的開關
                                    highlightElement(foundSwitch, 'rgba(46, 139, 87, 0.4)', 2000);
                                    return { success: true, message: "開關已經是開啟狀態" };
                                }
                                
                                // 在控制台記錄找到的開關
                                console.log('找到需要點擊的開關元素（通過規格名），準備點擊');
                                
                                // 滾動到開關位置
                                foundSwitch.scrollIntoView({block: 'center', behavior: 'smooth'});
                                
                                // 高亮開關並添加動畫效果
                                highlightElement(foundSwitch, 'rgba(255, 215, 0, 0.5)', 3000);
                                
                                setTimeout(() => {
                                    try {
                                        foundSwitch.click();
                                        console.log('開關已點擊');
                                        
                                        // 點擊後再次高亮以顯示成功
                                        setTimeout(() => {
                                            if (foundSwitch.classList.contains('eds-switch--open')) {
                                                highlightElement(foundSwitch, 'rgba(46, 139, 87, 0.4)', 2000);
                                            }
                                        }, 500);
                                    } catch(e) {
                                        console.error('點擊開關失敗: ' + e);
                                        highlightElement(foundSwitch, 'rgba(220, 20, 60, 0.3)', 2000);
                                    }
                                }, 500);
                                
                                return { success: true, message: "已點擊開關" };
                            }
                        }
                    }
                    
                    return { success: false, message: "找不到對應的開關" };
                }
                
                return findAndToggleSwitch(arguments[0], arguments[1]);
            """, 商品名稱, 規格名稱)
            
            # 等待JavaScript操作完成 (增加等待時間以便用戶看清視覺效果)
            time.sleep(1.5)
            
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
        """處理所有需要開啟的規格
        
        只處理庫存>0且未開啟的規格，符合需求
        
        Args:
            products (list): 包含商品規格信息的列表
            
        Returns:
            tuple: (成功數, 總處理數)
        """
        總處理數 = 0
        成功數 = 0
        
        logger.info("開始處理需要開啟的規格...")
        
        # 遍歷每個商品
        for product in products:
            商品名稱 = product.get('name', '未知商品')
            規格列表 = product.get('specs', [])
            
            logger.info(f"商品 '{商品名稱}': 檢查 {len(規格列表)} 個規格")
            
            # 檢查商品的每個規格
            for spec in 規格列表:
                規格名稱 = spec.get('name', '未知規格')
                狀態 = spec.get('status', '關閉')
                庫存 = spec.get('stock', '0')
                
                # 確保庫存是數字
                try:
                    庫存數字 = int(''.join(filter(str.isdigit, str(庫存))))
                except:
                    庫存數字 = 0
                
                # 只處理庫存>0且未開啟的規格
                if 庫存數字 > 0 and 狀態 != "開啟":
                    logger.info(f"規格 '{規格名稱}' 庫存為 {庫存數字}，狀態為 {狀態}，需要開啟")
                    總處理數 += 1
                    
                    # 嘗試開啟規格
                    if self.開啟規格(商品名稱, 規格名稱):
                        成功數 += 1
                        logger.info(f"✓ 成功開啟規格 '{規格名稱}'")
                    else:
                        logger.warning(f"⚠ 無法開啟規格 '{規格名稱}'")
        
        logger.info(f"規格開啟處理完成: 總共 {總處理數} 個規格，成功開啟 {成功數} 個")
        return 成功數, 總處理數
    
    def 開啟規格(self, 商品名稱, 規格名稱):
        """開啟特定商品規格
        
        Args:
            商品名稱 (str): 商品名稱
            規格名稱 (str): 規格名稱
            
        Returns:
            bool: 是否成功開啟
        """
        logger.info(f"嘗試開啟商品 '{商品名稱}' 的規格 '{規格名稱}'")
        
        # 使用增強的開關控制功能
        success = self.切換商品規格開關(商品名稱, 規格名稱)
        
        # 等待一段時間讓UI更新
        time.sleep(1.5)
        
        # 嘗試驗證是否成功開啟 - 再次查詢該規格狀態
        try:
            # 使用JavaScript查找並獲取狀態
            開關狀態 = self.driver.execute_script("""
                function getSpecStatus(productName, specName) {
                    console.log('檢查規格狀態，商品: ' + productName + ', 規格: ' + specName);
                    
                    // 查找商品容器
                    const productContainers = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                    for (const container of productContainers) {
                        const nameEl = container.querySelector('div.ellipsis-content.single');
                        if (nameEl && nameEl.innerText.trim() === productName) {
                            // 查找規格元素
                            const specElements = container.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                            for (const specElement of specElements) {
                                const specNameEl = specElement.querySelector('div.ellipsis-content.single');
                                if (specNameEl && specNameEl.innerText.trim() === specName) {
                                    // 檢查開關狀態
                                    const switchEl = specElement.querySelector('div.eds-switch');
                                    if (switchEl) {
                                        return {
                                            found: true,
                                            isOpen: switchEl.classList.contains('eds-switch--open'),
                                            isDisabled: switchEl.classList.contains('eds-switch--disabled')
                                        };
                                    }
                                }
                            }
                        }
                    }
                    
                    // 如果無法精確匹配，用更寬鬆的方式查找
                    const specElems = document.querySelectorAll('div.ellipsis-content.single');
                    for (const elem of specElems) {
                        if (elem.innerText.trim() === specName) {
                            let current = elem;
                            let foundSwitch = null;
                            for (let i = 0; i < 5; i++) {
                                if (!current) break;
                                const switchEls = current.querySelectorAll('div.eds-switch');
                                if (switchEls.length > 0) {
                                    foundSwitch = switchEls[0];
                                    break;
                                }
                                current = current.parentElement;
                            }
                            
                            if (foundSwitch) {
                                return {
                                    found: true,
                                    isOpen: foundSwitch.classList.contains('eds-switch--open'),
                                    isDisabled: foundSwitch.classList.contains('eds-switch--disabled')
                                };
                            }
                        }
                    }
                    
                    return { found: false };
                }
                
                return getSpecStatus(arguments[0], arguments[1]);
            """, 商品名稱, 規格名稱)
            
            if 開關狀態 and 開關狀態.get("found", False):
                is_open = 開關狀態.get("isOpen", False)
                is_disabled = 開關狀態.get("isDisabled", False)
                
                if is_open:
                    logger.info(f"✓ 規格 '{規格名稱}' 已確認為開啟狀態")
                    return True
                elif is_disabled:
                    logger.warning(f"⚠ 規格 '{規格名稱}' 的開關已被禁用")
                    return False
                else:
                    logger.warning(f"⚠ 規格 '{規格名稱}' 尚未開啟，嘗試重新開啟")
                    # 再次嘗試開啟
                    second_attempt = self.切換商品規格開關(商品名稱, 規格名稱)
                    time.sleep(1.5)  # 等待UI更新
                    return second_attempt
            else:
                logger.warning(f"⚠ 無法確認規格 '{規格名稱}' 的狀態")
                return success  # 返回之前的結果
                
        except Exception as e:
            logger.error(f"確認規格狀態時發生錯誤: {str(e)}")
            return success  # 發生錯誤時返回之前的結果
    
    def 關閉規格(self, 商品名稱, 規格名稱):
        """關閉特定商品規格 (目前不需要，但保留功能完整性)"""
        # 與開啟規格類似，需要實現關閉功能
        # 目前需求主要是開啟規格，因此可以簡化實現
        return False
    
    def 控制商品規格開關(self, 商品名稱, 規格名稱, 開啟狀態=True):
        """控制商品規格的開關狀態
        
        參數:
            商品名稱 (str): 商品名稱
            規格名稱 (str): 規格名稱
            開啟狀態 (bool): True表示開啟，False表示關閉
            
        返回:
            bool: 操作是否成功
        """
        logger.info(f"控制商品 '{商品名稱}' 規格 '{規格名稱}' 的開關狀態為: {'開啟' if 開啟狀態 else '關閉'}")
        
        if 開啟狀態:
            return self.開啟規格(商品名稱, 規格名稱)
        else:
            return self.關閉規格(商品名稱, 規格名稱) 