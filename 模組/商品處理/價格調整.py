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
        MAX_RETRIES = 3  # 減少最大重試次數，提高效率
        success = False
        調整記錄 = {
            "商品名稱": 商品名稱,
            "規格名稱": 規格名稱,
            "輸入價格": 新價格,
            "原價格": "未知",
            "調整結果": False,
            "調整時間": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for retry_count in range(MAX_RETRIES):
            try:
                if retry_count == 0:
                    logger.info(f"嘗試調整商品 '{商品名稱}' 規格 '{規格名稱}' 的價格為 {新價格}")
                else:
                    logger.info(f"【重試 {retry_count + 1}/{MAX_RETRIES}】嘗試調整商品 '{商品名稱}' 規格 '{規格名稱}' 的價格為 {新價格}")
                
                # 嘗試直接使用規格名稱找到對應的行
                try:
                    logger.info(f"尋找規格 '{規格名稱}' 的元素...")
                    
                    # 尋找並突出顯示規格行 - 使用更美觀的高亮效果
                    spec_row = self.driver.execute_script("""
                        function findAndHighlightSpecRow(productName, specName) {
                            console.log(`尋找商品 '${productName}' 規格 '${specName}' 的元素`);
                            
                            // 高亮顯示操作中的元素，方便用戶定位
                            function highlightElement(element, color, backgroundColor, duration) {
                                if (!element) return;
                                
                                // 保存原始樣式
                                const originalBackgroundColor = element.style.backgroundColor;
                                const originalBorder = element.style.border;
                                const originalBoxShadow = element.style.boxShadow;
                                const originalTransition = element.style.transition;
                                const originalColor = element.style.color;
                                
                                // 設置高亮樣式
                                element.style.transition = 'all 0.3s ease-in-out';
                                element.style.backgroundColor = backgroundColor || 'rgba(255, 255, 0, 0.2)';
                                element.style.boxShadow = `0 0 10px ${color || 'rgba(255, 215, 0, 0.5)'}`;
                                element.style.border = `2px solid ${color || 'rgba(255, 215, 0, 0.8)'}`;
                                if (color) element.style.color = color;
                                
                                // 在指定時間後恢復原始樣式
                                if (duration) {
                                    setTimeout(() => {
                                        element.style.backgroundColor = originalBackgroundColor;
                                        element.style.border = originalBorder;
                                        element.style.boxShadow = originalBoxShadow;
                                        element.style.color = originalColor;
                                        
                                        setTimeout(() => {
                                            element.style.transition = originalTransition;
                                        }, 300);
                                    }, duration);
                                }
                                
                                // 確保元素可見
                                element.scrollIntoView({block: 'center', behavior: 'smooth'});
                                return element;
                            }
                            
                            // 1. 優先在編輯模式下尋找
                            // 先尋找商品容器
                            let productContainer = null;
                            const productContainers = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                            
                            for (const container of productContainers) {
                                const nameEl = container.querySelector('div.ellipsis-content.single');
                                if (nameEl && nameEl.innerText.trim() === productName) {
                                    productContainer = container;
                                    // 輕微高亮商品容器
                                    highlightElement(container, null, 'rgba(144, 238, 144, 0.1)', 5000);
                                    console.log('找到商品容器');
                                    break;
                                }
                            }
                            
                            // 如果找到商品容器，查找規格
                            if (productContainer) {
                                // 尋找規格元素
                                const specElements = productContainer.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                                
                                for (const specElement of specElements) {
                                    const specNameEl = specElement.querySelector('div.ellipsis-content.single');
                                    if (specNameEl && specNameEl.innerText.trim() === specName) {
                                        console.log('找到規格元素');
                                        // 高亮規格元素
                                        highlightElement(specElement, null, 'rgba(135, 206, 250, 0.2)', 8000);
                                        // 高亮規格名稱
                                        highlightElement(specNameEl, '#1E90FF', null, 5000);
                                        return specElement;
                                    }
                                }
                            }
                            
                            // 2. 如果通過商品名稱找不到，嘗試只通過規格名查找
                            console.log('通過商品名找不到，嘗試只用規格名查找');
                            const specNameElements = document.querySelectorAll('div.ellipsis-content.single');
                            
                            for (const elem of specNameElements) {
                                if (elem.innerText.trim() === specName) {
                                    console.log('找到規格名稱匹配的元素');
                                    // 高亮顯示規格名稱
                                    highlightElement(elem, '#1E90FF', null, 5000);
                                    
                                    // 向上查找規格行
                                    let current = elem;
                                    let specRow = null;
                                    
                                    for (let i = 0; i < 5; i++) {
                                        if (!current) break;
                                        
                                        if (current.classList && 
                                            (current.classList.contains('discount-view-item-model-component') || 
                                             current.classList.contains('discount-edit-item-model-component') ||
                                             current.classList.contains('discount-edit-item-model-row'))) {
                                            specRow = current;
                                            break;
                                        }
                                        current = current.parentElement;
                                    }
                                    
                                    if (specRow) {
                                        console.log('找到規格行');
                                        highlightElement(specRow, null, 'rgba(135, 206, 250, 0.2)', 8000);
                                        return specRow;
                                    } else {
                                        // 如果沒找到明確的規格行，使用父元素作為替代
                                        console.log('未找到明確的規格行，使用父元素');
                                        let parent = elem.parentElement;
                                        if (parent) {
                                            highlightElement(parent, null, 'rgba(255, 255, 224, 0.3)', 8000);
                                            return parent;
                                        }
                                    }
                                    
                                    return elem.parentElement; // 至少返回一些內容
                                }
                            }
                            
                            console.log('未找到規格元素');
                            return null;
                        }
                        
                        return findAndHighlightSpecRow(arguments[0], arguments[1]);
                    """, 商品名稱, 規格名稱)
                    
                    if not spec_row:
                        logger.warning(f"未找到規格 '{規格名稱}' 的元素，重試中...")
                        time.sleep(1)
                        continue
                    
                    logger.info("找到規格行，準備調整價格...")
                    
                    # 獲取當前價格
                    try:
                        當前價格 = self.driver.execute_script("""
                            if (!arguments[0]) return 'N/A';
                            
                            // 查找價格欄位
                            const input = arguments[0].querySelector('input.eds-input__input');
                            if (input) {
                                return input.value;
                            }
                            
                            // 如果沒有找到輸入框，嘗試查找只讀價格
                            const priceElement = arguments[0].querySelector('.currency-input');
                            if (priceElement) {
                                return priceElement.textContent.trim();
                            }
                            
                            return 'N/A';
                        """, spec_row)
                        
                        if 當前價格 and 當前價格 != 'N/A':
                            調整記錄["原價格"] = 當前價格
                            logger.info(f"當前價格: {當前價格}")
                    except Exception as e:
                        logger.warning(f"獲取當前價格時出錯: {str(e)}")
                    
                    # 確保規格開關已開啟
                    switch_status = self.driver.execute_script("""
                        const row = arguments[0];
                        const switchEl = row.querySelector('div.eds-switch');
                        
                        if (switchEl) {
                            const isOpen = switchEl.classList.contains('eds-switch--open');
                            const isDisabled = switchEl.classList.contains('eds-switch--disabled');
                            
                            if (isDisabled) {
                                console.log('開關被禁用');
                                switchEl.style.border = '2px solid red';
                                return { success: false, message: '開關被禁用' };
                            }
                            
                            if (!isOpen) {
                                console.log('開關未開啟，嘗試點擊');
                                // 突出顯示開關
                                switchEl.style.boxShadow = '0 0 8px rgba(255, 165, 0, 0.8)';
                                switchEl.scrollIntoView({block: 'center', behavior: 'smooth'});
                                
                                // 點擊開關
                                setTimeout(() => {
                                    try {
                                        switchEl.click();
                                        console.log('已點擊開關');
                                        setTimeout(() => {
                                            if (switchEl.classList.contains('eds-switch--open')) {
                                                switchEl.style.boxShadow = '0 0 8px rgba(0, 255, 0, 0.8)';
                                            } else {
                                                switchEl.style.boxShadow = '0 0 8px rgba(255, 0, 0, 0.8)';
                                            }
                                        }, 500);
                                    } catch(e) {
                                        console.error('點擊開關失敗:', e);
                                    }
                                }, 300);
                                
                                return { success: true, message: '已嘗試開啟開關' };
                            }
                            
                            return { success: true, message: '開關已開啟' };
                        }
                        
                        return { success: false, message: '未找到開關' };
                    """, spec_row)
                    
                    if switch_status and switch_status.get('success', False):
                        if switch_status.get('message') == '已嘗試開啟開關':
                            logger.info("已嘗試開啟規格開關，等待UI更新...")
                            time.sleep(2.5)  # 等待開關切換和UI更新
                    else:
                        logger.warning(f"開關狀態檢查結果: {switch_status.get('message', '未知')}")
                    
                    # 找到並增強折扣價欄位
                    discount_input = self.driver.execute_script("""
                        function findAndHighlightPriceInput(row) {
                            console.log('尋找並高亮顯示價格輸入框...');
                            
                            // 高亮顯示輸入框
                            function highlightInput(input, color, message) {
                                if (!input) return input;
                                
                                const container = input.parentElement;
                                const originalBorderColor = input.style.borderColor;
                                
                                // 建立一個狀態指示器
                                let statusElement = document.createElement('div');
                                statusElement.style.position = 'absolute';
                                statusElement.style.right = '-120px';
                                statusElement.style.top = '0';
                                statusElement.style.padding = '2px 8px';
                                statusElement.style.borderRadius = '4px';
                                statusElement.style.fontSize = '12px';
                                statusElement.style.fontWeight = 'bold';
                                statusElement.style.backgroundColor = color || 'rgba(255, 255, 0, 0.8)';
                                statusElement.style.color = '#000';
                                statusElement.style.boxShadow = '0 0 5px rgba(0, 0, 0, 0.2)';
                                statusElement.style.zIndex = '9999';
                                statusElement.textContent = message || '準備輸入';
                                statusElement.style.transition = 'all 0.3s ease';
                                statusElement.style.opacity = '0.9';
                                statusElement.className = 'price-input-status';
                                
                                // 刪除可能存在的舊狀態元素
                                const oldStatus = container.querySelector('.price-input-status');
                                if (oldStatus) {
                                    oldStatus.remove();
                                }
                                
                                // 將狀態元素添加到輸入框容器
                                if (container.style.position !== 'relative' && container.style.position !== 'absolute') {
                                    container.style.position = 'relative';
                                }
                                container.appendChild(statusElement);
                                
                                // 高亮輸入框
                                input.style.transition = 'all 0.3s ease';
                                input.style.boxShadow = `0 0 8px ${color || 'rgba(255, 215, 0, 0.8)'}`;
                                input.style.border = `1px solid ${color || 'rgba(255, 215, 0, 0.8)'}`;
                                
                                // 確保輸入框可見並點擊以啟用
                                input.scrollIntoView({block: 'center', behavior: 'smooth'});
                                setTimeout(() => {
                                    try {
                                        // 嘗試激活輸入框
                                        input.click();
                                    } catch(e) {
                                        console.log('輸入框點擊失敗，可能已經激活');
                                    }
                                }, 100);
                                
                                return input;
                            }
                            
                            // 準備接收輸入框的變數
                            let priceInput = null;
                            
                            // 1. 直接查找規格行中帶有NT$前綴的輸入框 (最可靠的方法)
                            const prefixContainers = row.querySelectorAll('.eds-input__inner');
                            console.log(`找到 ${prefixContainers.length} 個輸入框容器`);
                            
                            for (const container of prefixContainers) {
                                // 檢查是否有NT$前綴
                                const prefix = container.querySelector('.eds-input__prefix');
                                if (prefix && prefix.textContent.includes('NT$')) {
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
                                        
                                        console.log('找到折扣價輸入框(NT$前綴)');
                                        priceInput = input;
                                        break;
                                    }
                                }
                            }
                            
                            // 2. 如果上面的方法沒找到，嘗試從編輯區塊中查找價格輸入
                            if (!priceInput) {
                                const editableSection = row.closest('.discount-edit-item-component') || 
                                                      row.closest('.discount-edit-item') || 
                                                      row;
                                
                                if (editableSection) {
                                    const editInputs = editableSection.querySelectorAll('input.eds-input__input');
                                    
                                    // 檢查所有輸入框，尋找帶有NT$前綴的
                                    for (const input of editInputs) {
                                        const inputParent = input.parentElement;
                                        if (inputParent) {
                                            const prefix = inputParent.querySelector('.eds-input__prefix');
                                            if (prefix && prefix.textContent.includes('NT$')) {
                                                console.log('從編輯區塊找到NT$輸入框');
                                                priceInput = input;
                                                break;
                                            }
                                        }
                                    }
                                    
                                    // 如果還沒找到，檢查是否有多個輸入框，第一個通常是價格
                                    if (!priceInput && editInputs.length > 0) {
                                        console.log('使用編輯區的第一個輸入框');
                                        priceInput = editInputs[0];
                                    }
                                }
                            }
                            
                            // 3. 如果前兩種方法都沒找到，回退到常規方法
                            if (!priceInput) {
                                // 收集頁面上所有可能的價格輸入框
                                const allInputs = row.querySelectorAll('input.eds-input__input');
                                console.log('找到輸入欄位數量:', allInputs.length);
                                
                                if (allInputs.length >= 2) {
                                    // 檢查輸入值模式 - 通常價格 > 10，折扣率 < 10
                                    const firstValue = allInputs[0].value ? parseFloat(allInputs[0].value) : 0;
                                    const secondValue = allInputs[1].value ? parseFloat(allInputs[1].value) : 0;
                                    
                                    if (firstValue > 10 && secondValue < 10) {
                                        // 第一個是價格
                                        console.log('基於數值範圍選擇第一個輸入框作為價格');
                                        priceInput = allInputs[0];
                                    } else if (firstValue < 10 && secondValue > 10) {
                                        // 第二個是價格
                                        console.log('基於數值範圍選擇第二個輸入框作為價格');
                                        priceInput = allInputs[1];
                                    } else {
                                        // 無法確定，使用第一個
                                        console.log('無法區分價格與折扣率，使用第一個輸入框');
                                        priceInput = allInputs[0];
                                    }
                                } else if (allInputs.length === 1) {
                                    // 只有一個輸入框
                                    console.log('只找到單個輸入框');
                                    priceInput = allInputs[0];
                                }
                            }
                            
                            // 如果找到了價格輸入框，進行高亮處理
                            if (priceInput) {
                                return highlightInput(priceInput, 'rgba(135, 206, 250, 0.8)', '價格輸入框');
                            }
                            
                            return null;
                        }
                        
                        return findAndHighlightPriceInput(arguments[0]);
                    """, spec_row)
                    
                    if not discount_input:
                        logger.warning("未找到價格輸入框，重試中...")
                        time.sleep(1.5)
                        continue
                    
                    logger.info("找到價格輸入框，準備輸入新價格...")
                    
                    # 清除輸入框當前值並輸入新價格 (帶視覺反饋)
                    input_result = self.driver.execute_script("""
                        function setInputValueWithAnimation(input, value) {
                            if (!input) {
                                console.error('輸入框不存在');
                                return { success: false, message: '輸入框不存在' };
                            }
                            
                            try {
                                console.log(`準備將 ${input.value || '空值'} 更改為 ${value}`);
                                
                                // 更新狀態指示器
                                const container = input.parentElement;
                                const statusElement = container.querySelector('.price-input-status');
                                if (statusElement) {
                                    statusElement.textContent = '清除中...';
                                    statusElement.style.backgroundColor = 'rgba(255, 165, 0, 0.8)';
                                }
                                
                                // 強制獲取焦點並多次嘗試清除
                                input.focus();
                                input.click();
                                
                                // 清除輸入框內容 - 先模擬選擇全部文字
                                input.select();
                                
                                // 確保所有文字都被選中後刪除
                                input.value = '';
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                
                                // 直接設置新值 - 不使用setTimeout
                                if (statusElement) {
                                    statusElement.textContent = '輸入中...';
                                    statusElement.style.backgroundColor = 'rgba(30, 144, 255, 0.8)';
                                }
                                
                                // 多次分步輸入 - 有時候直接賦值可能不會觸發頁面的驗證邏輯
                                input.value = value;
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                
                                // 確保輸入成功
                                if (input.value !== value) {
                                    console.log('直接賦值失敗，嘗試按鍵輸入方式');
                                    input.value = ''; // 再次清空
                                    
                                    // 模擬逐個字符輸入
                                    for (let i = 0; i < value.length; i++) {
                                        input.value += value[i];
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                    }
                                    input.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                                
                                // 按Enter確認輸入
                                input.dispatchEvent(new KeyboardEvent('keydown', {
                                    key: 'Enter',
                                    code: 'Enter',
                                    keyCode: 13,
                                    which: 13,
                                    bubbles: true
                                }));
                                
                                // 點擊輸入框外部確認輸入
                                document.body.click();
                                
                                // 再次檢查輸入是否成功
                                if (input.value !== value) {
                                    console.error(`輸入失敗，當前值為: ${input.value}，期望值為: ${value}`);
                                    if (statusElement) {
                                        statusElement.textContent = '輸入失敗!';
                                        statusElement.style.backgroundColor = 'rgba(255, 0, 0, 0.8)';
                                    }
                                    return { success: false, message: '輸入失敗，值不匹配' };
                                }
                                
                                // 更新狀態為成功
                                if (statusElement) {
                                    statusElement.textContent = '輸入成功!';
                                    statusElement.style.backgroundColor = 'rgba(46, 139, 87, 0.8)';
                                    // 淡出狀態指示器
                                    setTimeout(() => {
                                        statusElement.style.opacity = '0';
                                        setTimeout(() => {
                                            statusElement.remove();
                                        }, 300);
                                    }, 1000);
                                }
                                
                                console.log('價格輸入完成');
                                return { success: true, message: '價格輸入成功' };
                            } catch (e) {
                                console.error('設置輸入值時出錯:', e);
                                return { success: false, message: e.toString() };
                            }
                        }
                        
                        return setInputValueWithAnimation(arguments[0], arguments[1]);
                    """, discount_input, str(新價格))
                    
                    # 等待較短時間
                    time.sleep(1.5)
                    
                    # 檢查輸入結果
                    if input_result and input_result.get('success', False):
                        logger.info(f"✓ 價格更新成功: {新價格}")
                        
                        # 最後檢查是否有錯誤訊息
                        is_error = self.driver.execute_script("""
                            // 檢查是否有錯誤訊息
                            const errorMsgs = document.querySelectorAll('.eds-input__error-msg');
                            for (const error of errorMsgs) {
                                if (error.offsetParent !== null) {
                                    console.log('發現錯誤訊息:', error.textContent);
                                    return error.textContent;
                                }
                            }
                            return null;
                        """)
                        
                        if is_error:
                            logger.warning(f"❗ 價格輸入後有錯誤訊息: {is_error}")
                            # 繼續下一次重試
                            continue
                        
                        success = True
                        調整記錄["調整結果"] = True
                        return success, 調整記錄
                    else:
                        error_msg = input_result.get('message', '未知錯誤') if input_result else '輸入操作失敗'
                        logger.warning(f"❌ 價格輸入失敗: {error_msg}")
                        
                        # 只有在特定錯誤情況下才重試
                        if error_msg == '輸入失敗，值不匹配' or error_msg == '輸入框不存在':
                            # 值沒有成功設置，需要重試
                            continue
                        else:
                            # 其他錯誤嘗試更直接的方法輸入一次
                            try:
                                logger.info("嘗試使用更直接的方法輸入價格...")
                                # 直接使用 Selenium 的方法清除並輸入值
                                discount_input_selenium = self.driver.execute_script("return arguments[0]", discount_input)
                                if discount_input_selenium:
                                    discount_input_selenium.clear()
                                    discount_input_selenium.send_keys(str(新價格))
                                    discount_input_selenium.send_keys(Keys.ENTER)
                                    time.sleep(1)
                                    
                                    # 檢查是否成功
                                    current_value = self.driver.execute_script("return arguments[0].value", discount_input)
                                    if current_value == str(新價格):
                                        logger.info(f"✓ 使用直接方法成功設置價格: {新價格}")
                                        success = True
                                        調整記錄["調整結果"] = True
                                        return success, 調整記錄
                            except Exception as direct_input_error:
                                logger.error(f"直接輸入方法失敗: {str(direct_input_error)}")
                except Exception as e:
                    logger.error(f"尋找規格元素時發生錯誤: {str(e)}")
            
            except Exception as e:
                logger.error(f"調整價格時發生錯誤: {str(e)}")
            
            # 重試前等待
            wait_time = 1 + retry_count * 0.5  # 更合理的等待時間增長
            logger.info(f"等待 {wait_time:.1f} 秒後重試...")
            time.sleep(wait_time)
        
        if not success:
            logger.error(f"❌ 無法調整商品 '{商品名稱}' 規格 '{規格名稱}' 的價格，已達到最大重試次數")
        
        return success, 調整記錄 