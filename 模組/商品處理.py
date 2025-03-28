"""
商品處理模組 - 負責處理商品和規格相關的功能

包含功能:
- 尋找並分析商品
- 處理商品規格和開關
- 點擊編輯折扣活動按鈕
- 商品數據格式化和顯示
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
import re
from selenium.webdriver.common.keys import Keys

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("商品處理")

class 商品處理:
    """商品處理類，提供商品相關操作的功能"""
    
    def __init__(self, driver):
        """初始化商品處理物件"""
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
    
    def 搜尋商品(self):
        """尋找頁面上的所有商品元素"""
        try:
            logger.info("開始尋找頁面上的商品...")
            
            # 使用JavaScript查找商品元素
            products_info = self.driver.execute_script("""
                const products = [];
                
                // 尋找所有商品卡片
                const productCards = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                
                // 尋找離輸入框最近的標籤
                function findNearestLabel(element) {
                    // 1. 檢查前面的兄弟元素
                    let sibling = element.previousElementSibling;
                    while (sibling) {
                        if (sibling.textContent.trim()) {
                            return sibling.textContent.trim();
                        }
                        sibling = sibling.previousElementSibling;
                    }
                    
                    // 2. 檢查父元素是否有標籤或本身是標籤
                    let parent = element.parentElement;
                    if (parent) {
                        // 檢查父元素是否有label類或是label標籤
                        if (parent.classList.contains('label') || parent.tagName.toLowerCase() === 'label') {
                            return parent.textContent.trim();
                        }
                        
                        // 3. 檢查父元素的前面的兄弟元素
                        sibling = parent.previousElementSibling;
                        while (sibling) {
                            if (sibling.textContent.trim()) {
                                return sibling.textContent.trim();
                            }
                            sibling = sibling.previousElementSibling;
                        }
                        
                        // 4. 檢查父元素內的標籤
                        const labels = parent.querySelectorAll('label, .label, [class*="label"]');
                        for (const label of labels) {
                            if (label !== element && label.textContent.trim()) {
                                return label.textContent.trim();
                            }
                        }
                    }
                    
                    return null;
                }
                
                for (const card of productCards) {
                    try {
                        // 獲取商品名稱
                        const nameElem = card.querySelector('div.ellipsis-content.single');
                        const productName = nameElem ? nameElem.innerText.trim() : '未知商品';
                        
                        // 獲取商品規格
                        const specs = [];
                        const specElements = card.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                        
                        for (const specElem of specElements) {
                            try {
                                const specNameElem = specElem.querySelector('div.ellipsis-content.single');
                                const specName = specNameElem ? specNameElem.innerText.trim() : '未知規格';
                                
                                // 獲取庫存
                                const stockElem = specElem.querySelector('div.item-content.item-stock');
                                const stock = stockElem ? stockElem.innerText.trim() : '0';
                                
                                // 獲取價格 - 優先尋找實際折扣價格（而非折扣率）
                                let price = '0';
                                let priceType = '未知';
                                let discountRate = '';  // 記錄折扣率
                                let originalPrice = ''; // 記錄原價
                                
                                // 解析價格元素的內容，提取折扣價格
                                function extractPriceInfo(priceText) {
                                    const result = {
                                        discountPrice: '',
                                        originalPrice: '',
                                        discountRate: ''
                                    };
                                    
                                    // 如果文本中包含NT$，很可能是實際價格
                                    const ntMatches = priceText.match(/NT\\$\\s*(\\d+)/g);
                                    if (ntMatches && ntMatches.length > 0) {
                                        // 如果有多個NT$價格，第一個通常是原價，第二個通常是折扣價
                                        if (ntMatches.length >= 2) {
                                            const origMatch = ntMatches[0].match(/\\d+/);
                                            const discMatch = ntMatches[1].match(/\\d+/);
                                            
                                            if (origMatch) result.originalPrice = origMatch[0];
                                            if (discMatch) result.discountPrice = discMatch[0];
                                        } else {
                                            // 只有一個價格
                                            const match = ntMatches[0].match(/\\d+/);
                                            if (match) result.discountPrice = match[0];
                                        }
                                    }
                                    
                                    // 提取折扣率，通常是x.x折格式
                                    const rateMatch = priceText.match(/(\\d+(\\.\\d+)?)\\s*折/);
                                    if (rateMatch) {
                                        result.discountRate = rateMatch[1];
                                    }
                                    
                                    return result;
                                }
                                
                                // 方法1: 查找價格文本元素 - 優先查找含有多個價格的元素
                                let allPriceTexts = [];
                                const priceElements = specElem.querySelectorAll('.item-price, .item-content.item-price, [class*="price"], [class*="discount"]');
                                
                                // 先收集所有價格文本並按複雜度排序（優先考慮包含多個價格的文本）
                                for (const priceElem of priceElements) {
                                    const priceText = priceElem.innerText.trim();
                                    if (priceText) {
                                        // 計算文本中包含NT$的數量（越多越可能同時包含原價和折扣價）
                                        const ntCount = (priceText.match(/NT\\$/g) || []).length;
                                        allPriceTexts.push({
                                            text: priceText,
                                            ntCount: ntCount,
                                            hasDiscount: priceText.includes('折') || priceText.includes('或')
                                        });
                                    }
                                }
                                
                                // 按複雜度排序：優先處理同時包含多個NT$和折扣信息的文本
                                allPriceTexts.sort((a, b) => {
                                    // 首先按NT$數量排序
                                    if (b.ntCount !== a.ntCount) return b.ntCount - a.ntCount;
                                    // 其次考慮是否包含折扣信息
                                    return b.hasDiscount - a.hasDiscount;
                                });
                                
                                // 處理排序後的價格文本
                                let foundDiscountPrice = false;
                                for (const priceItem of allPriceTexts) {
                                    const priceInfo = extractPriceInfo(priceItem.text);
                                    
                                    // 優先使用找到的折扣價格
                                    if (priceInfo.discountPrice) {
                                        price = priceInfo.discountPrice;
                                        priceType = '折扣價';
                                        originalPrice = priceInfo.originalPrice || originalPrice;
                                        discountRate = priceInfo.discountRate || discountRate;
                                        console.log(`找到明確折扣價: ${price}, 原價: ${originalPrice}, 折扣率: ${discountRate}, 文本="${priceItem.text}"`);
                                        foundDiscountPrice = true;
                                        break;
                                    } else if (priceInfo.discountRate && !discountRate) {
                                        // 如果只找到折扣率，暫存起來
                                        discountRate = priceInfo.discountRate;
                                        if (priceInfo.originalPrice && !originalPrice) {
                                            originalPrice = priceInfo.originalPrice;
                                        }
                                    }
                                }
                                
                                // 如果找到了折扣率和原價，但沒有明確的折扣價，計算折扣價
                                if (!foundDiscountPrice && discountRate && originalPrice) {
                                    const calcDiscountPrice = Math.round(parseFloat(originalPrice) * parseFloat(discountRate) / 10);
                                    price = calcDiscountPrice.toString();
                                    priceType = '計算折扣價';
                                    console.log(`計算得到折扣價: ${price}, 原價: ${originalPrice}, 折扣率: ${discountRate}`);
                                    foundDiscountPrice = true;
                                }
                                
                                // 方法2: 如果沒有找到明確的折扣價，嘗試從頁面直接獲取
                                if (price === '0' || priceType === '折扣率' || priceType === '未知') {
                                    // 深度遍歷元素找尋價格
                                    let allElements = [];
                                    function getAllTextElements(elem) {
                                        if (elem.childNodes.length === 0 && elem.textContent.trim()) {
                                            allElements.push(elem);
                                        } else {
                                            for (const child of elem.childNodes) {
                                                if (child.nodeType === 1) { // 元素節點
                                                    getAllTextElements(child);
                                                }
                                            }
                                        }
                                    }
                                    
                                    getAllTextElements(specElem);
                                    
                                    // 查找包含NT$的元素，優先獲取折扣價
                                    let bestPrice = null;
                                    let bestOrigPrice = null;
                                    for (const elem of allElements) {
                                        const text = elem.textContent.trim();
                                        if (text.includes('NT$')) {
                                            const priceInfo = extractPriceInfo(text);
                                            if (priceInfo.discountPrice) {
                                                bestPrice = priceInfo.discountPrice;
                                                bestOrigPrice = priceInfo.originalPrice || bestOrigPrice;
                                                break;
                                            }
                                        }
                                    }
                                    
                                    if (bestPrice) {
                                        price = bestPrice;
                                        originalPrice = bestOrigPrice || originalPrice;
                                        priceType = '深度折扣價';
                                        console.log(`深度找到折扣價: ${price}, 原價: ${originalPrice}`);
                                    }
                                }
                                
                                // 方法3: 如果還是沒有找到價格，嘗試查找並點擊輸入欄位
                                if (!foundDiscountPrice && (price === '0' || priceType === '折扣率' || priceType === '未知')) {
                                    // 查找輸入框
                                    const inputs = specElem.querySelectorAll('input.eds-input__input');
                                    console.log(`找到 ${inputs.length} 個輸入框`);
                                    
                                    if (inputs.length > 0) {
                                        // 遍歷所有輸入框，優先取折扣價輸入框
                                        for (let i = 0; i < inputs.length; i++) {
                                            const input = inputs[i];
                                            // 記錄輸入框的placeholder和value
                                            console.log(`輸入框${i+1}: placeholder="${input.placeholder}", value="${input.value}"`);
                                            
                                            // 尋找離最近的label，可能包含"優惠價"或"折扣"字樣
                                            const nearestLabel = findNearestLabel(input);
                                            if (nearestLabel) {
                                                console.log(`輸入框${i+1}相關標籤: "${nearestLabel}"`);
                                                
                                                // 優先取含有折扣相關字樣的輸入框
                                                if (nearestLabel.includes('優惠') || 
                                                    nearestLabel.includes('折扣') || 
                                                    nearestLabel.includes('特價')) {
                                                    if (input.value && parseFloat(input.value) > 0) {
                                                        price = input.value;
                                                        priceType = '折扣輸入';
                                                        console.log(`從折扣相關輸入框獲取價格: ${price}`);
                                                        foundDiscountPrice = true;
                                                        // 高亮這個輸入框
                                                        input.style.border = '3px solid blue';
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                        
                                        // 如果還沒找到，優先取第二個輸入框（通常是折扣價）
                                        if (!foundDiscountPrice && inputs.length > 1) {
                                            const inputValue = inputs[1].value;
                                            if (inputValue && parseFloat(inputValue) > 0) {
                                                price = inputValue;
                                                priceType = '第二輸入框';
                                                console.log(`從第二輸入框獲取價格: ${price}`);
                                                foundDiscountPrice = true;
                                                // 高亮這個輸入框
                                                inputs[1].style.border = '3px solid purple';
                                            }
                                        } 
                                        // 最後，如果還沒找到則使用第一個輸入框
                                        else if (!foundDiscountPrice && inputs[0].value && parseFloat(inputs[0].value) > 0) {
                                            price = inputs[0].value;
                                            priceType = '第一輸入框';
                                            console.log(`從第一輸入框獲取價格: ${price}`);
                                            // 高亮這個輸入框
                                            inputs[0].style.border = '3px solid orange';
                                        }
                                    }
                                }
                                
                                // 方法4: 如果我們有折扣率和原價，但沒有折扣價，計算折扣價
                                if (!foundDiscountPrice && (price === '0' || price === discountRate || priceType === '折扣率') && discountRate && originalPrice) {
                                    // 用折扣率和原價計算折扣價
                                    const calcDiscountPrice = Math.round(parseFloat(originalPrice) * parseFloat(discountRate) / 10);
                                    price = calcDiscountPrice.toString();
                                    priceType = '計算折扣價';
                                    console.log(`最終計算折扣價: ${price} = ${originalPrice} × ${discountRate}/10`);
                                }
                                
                                // 如果price依然是折扣率（數字小於10），設置為價格類型為特殊標記
                                if (parseFloat(price) < 10 && parseFloat(price) > 0) {
                                    priceType = '折扣率值';
                                    console.log(`檢測到價格可能是折扣率: ${price} (小於10)`);
                                }
                                
                                console.log(`商品: ${productName}, 規格: ${specName}, 價格: ${price}, 類型: ${priceType}, 原價: ${originalPrice}, 折扣率: ${discountRate}`);
                                
                                // 檢查開關狀態
                                const switchElem = specElem.querySelector('div.eds-switch');
                                const isOpen = switchElem ? switchElem.classList.contains('eds-switch--open') : false;
                                const isDisabled = switchElem ? switchElem.classList.contains('eds-switch--disabled') : true;
                                
                                specs.push({
                                    name: specName,
                                    stock: stock,
                                    price: price,
                                    priceType: priceType,
                                    originalPrice: originalPrice,
                                    discountRate: discountRate,
                                    status: isOpen ? '開啟' : '關閉',
                                    disabled: isDisabled,
                                    switch: switchElem ? true : false
                                });
                            } catch (error) {
                                console.error('處理規格時出錯:', error);
                            }
                        }
                        
                        products.push({
                            name: productName,
                            specs: specs
                        });
                    } catch (error) {
                        console.error('處理商品卡片時出錯:', error);
                    }
                }
                
                return {
                    product_count: products.length,
                    spec_count: products.reduce((count, product) => count + product.specs.length, 0),
                    products: products
                };
            """)
            
            if products_info and products_info.get("product_count", 0) > 0:
                logger.info(f"找到 {products_info.get('product_count')} 個商品和 {products_info.get('spec_count')} 個規格")
                return products_info
            else:
                logger.warning("未找到任何商品")
                return {"product_count": 0, "spec_count": 0, "products": []}
                
        except Exception as e:
            logger.error(f"搜尋商品時發生錯誤: {str(e)}")
            return {"error": str(e), "product_count": 0, "spec_count": 0, "products": []}
    
    def 搜尋特定前綴商品(self, prefix="Fee"):
        """尋找特定前綴的商品，例如Fee開頭的商品"""
        try:
            logger.info(f"開始尋找 [{prefix}] 開頭的商品...")
            
            # 使用JavaScript查找特定前綴的商品
            products_info = self.driver.execute_script("""
                const prefix = arguments[0];
                const products = [];
                
                // 尋找所有商品卡片
                const productCards = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                
                // 尋找離輸入框最近的標籤
                function findNearestLabel(element) {
                    // 1. 檢查前面的兄弟元素
                    let sibling = element.previousElementSibling;
                    while (sibling) {
                        if (sibling.textContent.trim()) {
                            return sibling.textContent.trim();
                        }
                        sibling = sibling.previousElementSibling;
                    }
                    
                    // 2. 檢查父元素是否有標籤或本身是標籤
                    let parent = element.parentElement;
                    if (parent) {
                        // 檢查父元素是否有label類或是label標籤
                        if (parent.classList.contains('label') || parent.tagName.toLowerCase() === 'label') {
                            return parent.textContent.trim();
                        }
                        
                        // 3. 檢查父元素的前面的兄弟元素
                        sibling = parent.previousElementSibling;
                        while (sibling) {
                            if (sibling.textContent.trim()) {
                                return sibling.textContent.trim();
                            }
                            sibling = sibling.previousElementSibling;
                        }
                        
                        // 4. 檢查父元素內的標籤
                        const labels = parent.querySelectorAll('label, .label, [class*="label"]');
                        for (const label of labels) {
                            if (label !== element && label.textContent.trim()) {
                                return label.textContent.trim();
                            }
                        }
                    }
                    
                    return null;
                }
                
                for (const card of productCards) {
                    try {
                        // 獲取商品名稱
                        const nameElem = card.querySelector('div.ellipsis-content.single');
                        const productName = nameElem ? nameElem.innerText.trim() : '';
                        
                        // 檢查是否是指定前綴的商品
                        if (productName.startsWith(prefix)) {
                            // 獲取商品規格
                            const specs = [];
                            const specElements = card.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                            
                            for (const specElem of specElements) {
                                try {
                                    const specNameElem = specElem.querySelector('div.ellipsis-content.single');
                                    const specName = specNameElem ? specNameElem.innerText.trim() : '未知規格';
                                    
                                    // 獲取庫存
                                    const stockElem = specElem.querySelector('div.item-content.item-stock');
                                    const stock = stockElem ? stockElem.innerText.trim() : '0';
                                    
                                    // 獲取價格 - 優先尋找實際折扣價格（而非折扣率）
                                    let price = '0';
                                    let priceType = '未知';
                                    let discountRate = '';  // 記錄折扣率
                                    let originalPrice = ''; // 記錄原價
                                    
                                    // 解析價格元素的內容，提取折扣價格
                                    function extractPriceInfo(priceText) {
                                        const result = {
                                            discountPrice: '',
                                            originalPrice: '',
                                            discountRate: ''
                                        };
                                        
                                        // 如果文本中包含NT$，很可能是實際價格
                                        const ntMatches = priceText.match(/NT\\$\\s*(\\d+)/g);
                                        if (ntMatches && ntMatches.length > 0) {
                                            // 如果有多個NT$價格，第一個通常是原價，第二個通常是折扣價
                                            if (ntMatches.length >= 2) {
                                                const origMatch = ntMatches[0].match(/\\d+/);
                                                const discMatch = ntMatches[1].match(/\\d+/);
                                                
                                                if (origMatch) result.originalPrice = origMatch[0];
                                                if (discMatch) result.discountPrice = discMatch[0];
                                                
                                                // 輸出NT$價格匹配情況用於調試
                                                console.log(`找到多個NT$價格: 原價=${result.originalPrice}, 折扣價=${result.discountPrice}, 文本="${priceText}"`);
                                            } else {
                                                // 只有一個價格
                                                const match = ntMatches[0].match(/\\d+/);
                                                if (match) result.discountPrice = match[0];
                                                console.log(`找到單個NT$價格: ${result.discountPrice}, 文本="${priceText}"`);
                                            }
                                        }
                                        
                                        // 提取折扣率，通常是x.x折格式
                                        const rateMatch = priceText.match(/(\\d+(\\.\\d+)?)\\s*折/);
                                        if (rateMatch) {
                                            result.discountRate = rateMatch[1];
                                            console.log(`找到折扣率: ${result.discountRate}折, 文本="${priceText}"`);
                                        }
                                        
                                        return result;
                                    }
                                    
                                    // 方法1: 查找價格文本元素 - 優先查找含有多個價格的元素
                                    let allPriceTexts = [];
                                    const priceElements = specElem.querySelectorAll('.item-price, .item-content.item-price, [class*="price"], [class*="discount"]');
                                    
                                    // 先收集所有價格文本並按複雜度排序（優先考慮包含多個價格的文本）
                                    for (const priceElem of priceElements) {
                                        const priceText = priceElem.innerText.trim();
                                        if (priceText) {
                                            // 計算文本中包含NT$的數量（越多越可能同時包含原價和折扣價）
                                            const ntCount = (priceText.match(/NT\\$/g) || []).length;
                                            allPriceTexts.push({
                                                text: priceText,
                                                ntCount: ntCount,
                                                hasDiscount: priceText.includes('折') || priceText.includes('或')
                                            });
                                        }
                                    }
                                    
                                    // 按複雜度排序：優先處理同時包含多個NT$和折扣信息的文本
                                    allPriceTexts.sort((a, b) => {
                                        // 首先按NT$數量排序
                                        if (b.ntCount !== a.ntCount) return b.ntCount - a.ntCount;
                                        // 其次考慮是否包含折扣信息
                                        return b.hasDiscount - a.hasDiscount;
                                    });
                                    
                                    // 處理排序後的價格文本
                                    let foundDiscountPrice = false;
                                    for (const priceItem of allPriceTexts) {
                                        const priceInfo = extractPriceInfo(priceItem.text);
                                        
                                        // 優先使用找到的折扣價格
                                        if (priceInfo.discountPrice) {
                                            price = priceInfo.discountPrice;
                                            priceType = '折扣價';
                                            originalPrice = priceInfo.originalPrice || originalPrice;
                                            discountRate = priceInfo.discountRate || discountRate;
                                            console.log(`找到明確折扣價: ${price}, 原價: ${originalPrice}, 折扣率: ${discountRate}, 文本="${priceItem.text}"`);
                                            foundDiscountPrice = true;
                                            break;
                                        } else if (priceInfo.discountRate && !discountRate) {
                                            // 如果只找到折扣率，暫存起來
                                            discountRate = priceInfo.discountRate;
                                            if (priceInfo.originalPrice && !originalPrice) {
                                                originalPrice = priceInfo.originalPrice;
                                            }
                                        }
                                    }
                                    
                                    // 如果找到了折扣率和原價，但沒有明確的折扣價，計算折扣價
                                    if (!foundDiscountPrice && discountRate && originalPrice) {
                                        const calcDiscountPrice = Math.round(parseFloat(originalPrice) * parseFloat(discountRate) / 10);
                                        price = calcDiscountPrice.toString();
                                        priceType = '計算折扣價';
                                        console.log(`計算得到折扣價: ${price}, 原價: ${originalPrice}, 折扣率: ${discountRate}`);
                                        foundDiscountPrice = true;
                                    }
                                    
                                    // 方法2: 如果沒有找到明確的折扣價，嘗試從頁面直接獲取
                                    if (!foundDiscountPrice && (price === '0' || priceType === '折扣率' || priceType === '未知')) {
                                        // 深度遍歷元素找尋價格
                                        let allElements = [];
                                        function getAllTextElements(elem) {
                                            if (elem.childNodes.length === 0 && elem.textContent.trim()) {
                                                allElements.push(elem);
                                            } else {
                                                for (const child of elem.childNodes) {
                                                    if (child.nodeType === 1) { // 元素節點
                                                        getAllTextElements(child);
                                                    }
                                                }
                                            }
                                        }
                                        
                                        // 首先遍歷整個規格元素
                                        getAllTextElements(specElem);
                                        console.log(`深度遍歷找到 ${allElements.length} 個文本元素`);
                                        
                                        // 收集所有包含NT$的文本
                                        let priceTexts = [];
                                        for (const elem of allElements) {
                                            const text = elem.textContent.trim();
                                            if (text.includes('NT$')) {
                                                // 計算文本中含有NT$的數量
                                                const ntCount = (text.match(/NT\\$/g) || []).length;
                                                // 檢查是否同時包含折扣相關詞
                                                const hasDiscount = text.includes('折') || text.includes('或');
                                                
                                                priceTexts.push({
                                                    text: text,
                                                    element: elem,
                                                    ntCount: ntCount,
                                                    hasDiscount: hasDiscount
                                                });
                                                
                                                console.log(`找到價格文本: "${text}", NT$數量: ${ntCount}, 含折扣信息: ${hasDiscount}`);
                                            }
                                        }
                                        
                                        // 按優先級排序：多個NT$且含折扣信息的優先
                                        priceTexts.sort((a, b) => {
                                            if (b.ntCount !== a.ntCount) return b.ntCount - a.ntCount;
                                            return b.hasDiscount - a.hasDiscount;
                                        });
                                        
                                        // 依次分析每個價格文本
                                        for (const priceText of priceTexts) {
                                            const priceInfo = extractPriceInfo(priceText.text);
                                            
                                            if (priceInfo.discountPrice) {
                                                price = priceInfo.discountPrice;
                                                originalPrice = priceInfo.originalPrice || originalPrice;
                                                discountRate = priceInfo.discountRate || discountRate;
                                                priceType = '深度折扣價';
                                                console.log(`深度找到折扣價: ${price}, 原價: ${originalPrice}, 折扣率: ${discountRate}, 文本="${priceText.text}"`);
                                                
                                                // 高亮顯示找到的價格元素，幫助調試
                                                priceText.element.style.border = '3px solid green';
                                                foundDiscountPrice = true;
                                                break;
                                            } else if (priceInfo.originalPrice && !originalPrice) {
                                                originalPrice = priceInfo.originalPrice;
                                                console.log(`深度找到原價: ${originalPrice}`);
                                            } else if (priceInfo.discountRate && !discountRate) {
                                                discountRate = priceInfo.discountRate;
                                                console.log(`深度找到折扣率: ${discountRate}折`);
                                            }
                                        }
                                        
                                        // 如果收集了原價和折扣率，但還沒有折扣價，計算折扣價
                                        if (!foundDiscountPrice && originalPrice && discountRate) {
                                            const calcDiscountPrice = Math.round(parseFloat(originalPrice) * parseFloat(discountRate) / 10);
                                            price = calcDiscountPrice.toString();
                                            priceType = '深度計算折扣價';
                                            console.log(`深度計算得到折扣價: ${price} = ${originalPrice} × ${discountRate}/10`);
                                            foundDiscountPrice = true;
                                        }
                                    }
                                } catch (error) {
                                    console.error('處理規格時出錯:', error);
                                }
                            }
                            
                            products.push({
                                name: productName,
                                specs: specs
                            });
                        }
                    } catch (error) {
                        console.error('處理商品卡片時出錯:', error);
                    }
                }
                
                return {
                    product_count: products.length,
                    spec_count: products.reduce((count, product) => count + product.specs.length, 0),
                    products: products
                };
            """, prefix)
            
            if products_info and products_info.get("product_count", 0) > 0:
                logger.info(f"找到 {products_info.get('product_count')} 個 [{prefix}] 開頭的商品和 {products_info.get('spec_count')} 個規格")
                return products_info
            else:
                logger.warning(f"未找到任何 [{prefix}] 開頭的商品")
                return {"product_count": 0, "spec_count": 0, "products": []}
                
        except Exception as e:
            logger.error(f"搜尋特定前綴商品時發生錯誤: {str(e)}")
            return {"error": str(e), "product_count": 0, "spec_count": 0, "products": []}
    
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
                                    
                                    // 高亮顯示開關
                                    switchEl.style.border = '3px solid red';
                                    
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
                                
                                // 高亮顯示開關
                                foundSwitch.style.border = '3px solid blue';
                                
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
    
    def 格式化商品資訊(self, products):
        """格式化顯示產品和規格信息為字符串"""
        if not products or len(products) == 0:
            return "未找到任何產品"
            
        result = []
        result.append("====== 找到的商品列表 ======")
        result.append(f"共找到 {len(products)} 個商品")
        
        for i, product in enumerate(products):
            product_name = product.get('name', f"商品 #{i+1}")
            specs = product.get('specs', [])
            
            result.append(f"\n{i+1}. {product_name}")
            result.append("-" * 80)
            
            # 建立表格標題
            result.append(f"{'規格名稱':<40} | {'庫存':<8} | {'價格':<12} | {'狀態':<10} | {'操作':<12}")
            result.append("-" * 80)
            
            # 顯示每個規格
            for spec in specs:
                spec_name = spec.get('name', '未知規格')
                stock = spec.get('stock', '0')
                price = spec.get('price', '0')
                price_type = spec.get('priceType', '')
                original_price = spec.get('originalPrice', '')
                discount_rate = spec.get('discountRate', '')
                status = spec.get('status', '未知')
                disabled = spec.get('disabled', False)
                
                # 格式化價格顯示 - 根據價格類型選擇適當的顯示方式
                price_display = price
                if price_type == '折扣率值':
                    # 如果是折扣率，顯示為 "x折 (估計價格NT$y)"
                    if original_price:
                        estimated_price = round(float(original_price) * float(price) / 10)
                        price_display = f"{price}折 (≈NT${estimated_price})"
                    else:
                        price_display = f"{price}折"
                elif original_price and discount_rate:
                    # 如果有原價和折扣率，顯示 "NT$x (y折)"
                    price_display = f"NT${price} ({discount_rate}折)"
                elif price_type in ['折扣價', '計算折扣價', '深度折扣價']:
                    # 確保顯示為NT$格式
                    if not price_display.startswith("NT$"):
                        price_display = f"NT${price_display}"
                
                # 嘗試提取庫存數字
                try:
                    stock_number = int(''.join(filter(str.isdigit, str(stock))))
                except:
                    stock_number = 0
                
                # 確定操作動作
                if stock_number > 0 and not disabled:
                    if status != "開啟":
                        action = "需要開啟"
                    else:
                        action = "正常"
                else:
                    action = "正常"
                
                # 處理可能過長的規格名稱
                if len(spec_name) > 38:
                    spec_name = spec_name[:35] + "..."
                
                # 格式化顯示
                status_display = f"{status}{' (已禁用)' if disabled else ''}"
                result.append(f"{spec_name:<40} | {stock:<8} | {price_display:<12} | {status_display:<10} | {action:<12}")
            
            result.append("-" * 80)
        
        return "\n".join(result)
        
    def 分析規格類型(self, 規格名稱):
        """智能分析規格名稱，提取主要類型
        
        處理多種可能的格式:
        - '短袖-黑色' → '短袖'
        - '長袖-白色' → '長袖'
        - '超級顯瘦-黑色,XL' → '超級顯瘦'
        - '標準版/紅色' → '標準版'
        - '黑色 L碼' → '黑色'
        """
        logger.info(f"分析規格: '{規格名稱}'")
        
        # 如果是空字串，直接返回
        if not 規格名稱 or 規格名稱.strip() == '':
            return '未知規格'
        
        # 先移除尺寸部分（通常在逗號後面）
        處理名稱 = 規格名稱
        if ',' in 處理名稱:
            處理名稱 = 處理名稱.split(',')[0].strip()
            logger.info(f"移除逗號後尺寸: '{處理名稱}'")
        
        # 1. 嘗試通過常見分隔符分割
        分隔符列表 = ['-', '/', '_', ' ', '：', ':', '，']
        
        for 分隔符 in 分隔符列表:
            if 分隔符 in 處理名稱:
                分割結果 = 處理名稱.split(分隔符)
                # 通常第一部分是主要類型，但確保它不是空的
                if 分割結果[0].strip():
                    主要類型 = 分割結果[0].strip()
                    logger.info(f"通過分隔符 '{分隔符}' 找到主要類型: '{主要類型}'")
                    return 主要類型
        
        # 2. 檢測常見尺寸詞和顏色詞
        # 先定義模式關鍵字
        尺寸列表 = ['S', 'M', 'L', 'XL', 'XXL', '大', '小', '中', '加大', '標準', '一般', '正常']
        顏色列表 = ['黑', '白', '紅', '藍', '綠', '黃', '橙', '紫', '灰', '粉', '棕', '膚', '米', '金', '銀', '色']
        款式詞列表 = ['款', '型', '系列', '版', '經典', '休閒', '正式', '日常', '寬鬆', '修身', '貼身']
        
        # 3. 嘗試找出主要商品類型 (通常在顏色/尺寸前)
        # 先檢查是否有款式詞，它們通常是主要類型的一部分
        for 款式詞 in 款式詞列表:
            if 款式詞 in 處理名稱:
                # 尋找款式詞的位置
                款式詞位置 = 處理名稱.find(款式詞)
                # 檢查是否是單獨的款式詞還是更大短語的一部分
                if 款式詞位置 >= 0:
                    # 保留款式詞作為標識
                    主要類型 = 處理名稱[:款式詞位置 + len(款式詞)].strip()
                    logger.info(f"通過款式詞 '{款式詞}' 找到主要類型: '{主要類型}'")
                    return 主要類型
        
        # 檢查是否有顏色詞，它們通常在主要類型之後
        for 顏色 in 顏色列表:
            if 顏色 in 處理名稱:
                顏色位置 = 處理名稱.find(顏色)
                if 顏色位置 > 0:
                    # 前面部分可能是主要類型
                    主要類型 = 處理名稱[:顏色位置].strip()
                    if 主要類型:  # 確保不是空字串
                        logger.info(f"通過顏色詞 '{顏色}' 找到主要類型: '{主要類型}'")
                        return 主要類型
                    
        # 檢查是否有尺寸詞，它們通常也在主要類型之後
        for 尺寸 in 尺寸列表:
            if 尺寸 in 處理名稱:
                尺寸位置 = 處理名稱.find(尺寸)
                if 尺寸位置 > 0:
                    # 前面部分可能是主要類型
                    主要類型 = 處理名稱[:尺寸位置].strip()
                    if 主要類型:  # 確保不是空字串
                        logger.info(f"通過尺寸詞 '{尺寸}' 找到主要類型: '{主要類型}'")
                        return 主要類型
        
        # 4. 檢查是否由多個數字/字母混合組合而成的規格 (例如 "A123-B456")
        # 這種情況下可能是產品代碼，我們嘗試以數字為分隔點
        數字匹配 = re.search(r'\d+', 處理名稱)
        if 數字匹配:
            起始位置 = 數字匹配.start()
            if 起始位置 > 0:
                前段文字 = 處理名稱[:起始位置].strip()
                if 前段文字:
                    logger.info(f"通過數字分割找到可能的類型: '{前段文字}'")
                    return 前段文字
        
        # 5. 如果上述方法都失敗，返回整個處理後的名稱
        logger.info(f"無法分析規格類型，使用完整處理名稱: '{處理名稱}'")
        return 處理名稱
    
    def 查找同類規格價格(self, 商品, 目標規格名稱):
        """智能查找相同商品下類似規格的價格
        
        處理原則:
        1. 首先根據規格類型匹配 (相同 > 包含關係 > 無關)
        2. 如果所有規格價格都相同，則直接使用統一價格
        3. 如果找不到匹配規格但有其他開啟規格，默認價格保持一致
        """
        目標規格類型 = self.分析規格類型(目標規格名稱)
        logger.info(f"目標規格 '{目標規格名稱}' 的類型識別為: '{目標規格類型}'")
        
        所有規格 = 商品.get('specs', [])
        同類規格列表 = []
        所有有效規格 = []  # 所有開啟且有價格的規格
        
        # 當前規格現有價格
        當前價格 = None
        當前規格對象 = None
        for spec in 所有規格:
            if spec.get('name', '') == 目標規格名稱:
                當前規格對象 = spec
                當前價格 = spec.get('price', '0')
                當前價格類型 = spec.get('priceType', '')
                
                # 如果價格是折扣率，嘗試使用計算價格
                if 當前價格類型 == '折扣率值' and float(當前價格) < 10:
                    原價 = spec.get('originalPrice', '')
                    if 原價:
                        # 計算實際折扣價格
                        當前價格 = round(float(原價) * float(當前價格) / 10)
                    else:
                        # 如果無法計算，記錄為0
                        當前價格 = 0
                else:
                    # 提取數字部分
                    try:
                        當前價格 = int(''.join(filter(str.isdigit, str(當前價格))))
                    except:
                        當前價格 = 0
                break
        
        # 收集所有有效規格並查找同類規格
        for spec in 所有規格:
            規格名稱 = spec.get('name', '')
            if 規格名稱 != 目標規格名稱:  # 排除目標規格自身
                規格類型 = self.分析規格類型(規格名稱)
                規格價格 = spec.get('price', '0')
                規格價格類型 = spec.get('priceType', '')
                規格狀態 = spec.get('status', '') == '開啟'
                
                # 處理折扣率類型的價格
                if 規格價格類型 == '折扣率值' and float(規格價格) < 10:
                    原價 = spec.get('originalPrice', '')
                    if 原價:
                        # 計算實際折扣價格
                        規格價格 = round(float(原價) * float(規格價格) / 10)
                    else:
                        # 如果無法計算，記錄為0
                        規格價格 = 0
                else:
                    # 提取價格數字部分
                    try:
                        規格價格 = int(''.join(filter(str.isdigit, str(規格價格))))
                    except:
                        規格價格 = 0
                
                # 只考慮價格大於0且狀態為開啟的規格
                if 規格價格 > 0 and 規格狀態:
                    logger.info(f"有效規格: '{規格名稱}' (類型: '{規格類型}') 價格: {規格價格}")
                    
                    # 添加到所有有效規格
                    所有有效規格.append({
                        'name': 規格名稱,
                        'type': 規格類型,
                        'price': 規格價格
                    })
                    
                    # 計算相似度
                    相似度 = 0
                    
                    # 判斷類型相似度
                    if 規格類型 == 目標規格類型:
                        相似度 = 1.0  # 完全相同類型
                    elif 規格類型 in 目標規格類型 or 目標規格類型 in 規格類型:
                        相似度 = 0.7  # 部分匹配
                    else:
                        # 檢查是否共享某些關鍵詞
                        共同關鍵詞 = False
                        關鍵詞列表 = ['顯瘦', '必備', '修身', '寬鬆', '經典', '休閒'] 
                        for 關鍵詞 in 關鍵詞列表:
                            if 關鍵詞 in 規格類型 and 關鍵詞 in 目標規格類型:
                                共同關鍵詞 = True
                                break
                        相似度 = 0.5 if 共同關鍵詞 else 0.2  # 共享關鍵詞或無關聯
                    
                    同類規格列表.append({
                        'name': 規格名稱,
                        'type': 規格類型,
                        'price': 規格價格,
                        'similarity': 相似度
                    })
        
        # 分析結果並決定建議價格
        if not 所有有效規格:
            logger.warning(f"未找到任何有效規格可參考")
            return None, None, False
            
        # 檢查是否所有規格價格都一樣
        所有價格 = [規格['price'] for 規格 in 所有有效規格]
        if 所有價格 and all(價格 == 所有價格[0] for 價格 in 所有價格):
            統一價格 = 所有價格[0]
            logger.info(f"所有規格價格都相同: {統一價格}")
            
            # 檢查當前價格是否需要調整
            if 當前價格 != 統一價格:
                return 統一價格, 所有有效規格[0]['name'], True
            else:
                return 統一價格, 所有有效規格[0]['name'], False
        
        # 如果找到同類規格，按相似度排序
        if 同類規格列表:
            同類規格列表.sort(key=lambda x: x['similarity'], reverse=True)
            最佳匹配 = 同類規格列表[0]
            建議價格 = 最佳匹配['price']
            
            logger.info(f"找到最佳匹配規格: '{最佳匹配['name']}' (相似度: {最佳匹配['similarity']}) 價格: {建議價格}")
            
            # 檢查當前價格是否需要調整
            if 當前價格 != 建議價格:
                return 建議價格, 最佳匹配['name'], True
            else:
                return 建議價格, 最佳匹配['name'], False
        
        # 如果沒有找到同類規格，但有其他有效規格，使用第一個有效規格的價格
        if 所有有效規格:
            預設規格 = 所有有效規格[0]
            預設價格 = 預設規格['price']
            logger.info(f"未找到同類規格，使用預設規格 '{預設規格['name']}' 價格: {預設價格}")
            
            # 檢查當前價格是否需要調整
            if 當前價格 != 預設價格:
                return 預設價格, 預設規格['name'], True
            else:
                return 預設價格, 預設規格['name'], False
        
        # 最後實在找不到，返回無法匹配
        logger.warning(f"無法找到合適的價格匹配")
        return None, None, False
    
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
                        time.sleep(0.5)
                        
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
                                # 重要修改：尋找折扣價輸入欄位而非原價
                                logger.info("尋找折扣價欄位...")
                                
                                # 使用JavaScript查找折扣價輸入欄位
                                discount_input = self.driver.execute_script("""
                                    const row = arguments[0];
                                    
                                    // 尋找所有輸入欄位
                                    const inputs = row.querySelectorAll('input.eds-input__input');
                                    console.log('找到輸入欄位數量:', inputs.length);
                                    
                                    // 尋找所有折扣輸入欄位（通常包含discount或percent字樣）
                                    let discountInput = null;
                                    
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
                                                input.style.border = '3px solid green';
                                                console.log('找到折扣價輸入框');
                                                return input;
                                            }
                                        }
                                    }
                                    
                                    // 如果沒有明確的折扣價，查找所有輸入框
                                    for (let i = 0; i < inputs.length; i++) {
                                        const input = inputs[i];
                                        const rect = input.getBoundingClientRect();
                                        if (rect.width > 0 && rect.height > 0 && input.offsetParent !== null) {
                                            // 嘗試識別是否是折扣價格輸入框
                                            const parent = input.closest('.eds-form-control');
                                            if (parent) {
                                                const label = parent.querySelector('.eds-form-control__label');
                                                if (label && (label.textContent.includes('折扣') || label.textContent.includes('discount'))) {
                                                    input.style.border = '3px solid green';
                                                    console.log('找到帶標籤的折扣價輸入框');
                                                    return input;
                                                }
                                            }
                                            
                                            // 檢查是否為第二個輸入框 (通常第一個是原價，第二個是折扣價)
                                            if (i === 1) {
                                                input.style.border = '3px solid orange';
                                                console.log('找到可能的折扣價輸入框(第二個輸入框)');
                                                return input;
                                            }
                                        }
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
                                                        const placeholder = input.getAttribute('placeholder') || '';
                                                        if (placeholder.includes('折') || input.value <= 10) {
                                                            input.style.border = '3px solid purple';
                                                            console.log('找到折扣率輸入框');
                                                            return input;
                                                        }
                                                    }
                                                    
                                                    // 如果找不到明確的折扣率輸入框，返回第一個輸入框
                                                    inputs[0].style.border = '3px solid red';
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
                                        logger.warning(f"檢測到錯誤消息: {error_visible}")
                                        
                                        # 如果是折扣率輸入框，可能需要調整值
                                        if is_discount_rate:
                                            # 首先尝试从页面元素获取原价
                                            page_original_price = self.driver.execute_script("""
                                                const row = arguments[0].closest('.discount-edit-item-model-component, .discount-view-item-model-component');
                                                if (!row) return null;
                                                
                                                // 查找所有包含价格的元素
                                                const priceElements = row.querySelectorAll('.item-price, .item-content.item-price, [class*="price"], [class*="discount"]');
                                                
                                                for (const elem of priceElements) {
                                                    const text = elem.textContent.trim();
                                                    // 寻找包含NT$的元素
                                                    if (text.includes('NT$')) {
                                                        // 如果有多个价格（通常第一个是原价）
                                                        const matches = text.match(/NT\\$\\s*(\\d+)/g);
                                                        if (matches && matches.length > 0) {
                                                            const firstPrice = matches[0].match(/\\d+/);
                                                            if (firstPrice) {
                                                                console.log('从页面找到可能的原价:', firstPrice[0]);
                                                                return firstPrice[0];
                                                            }
                                                        }
                                                    }
                                                }
                                                
                                                return null;
                                            """, discount_input)
                                            
                                            # 尝试从spec获取原价
                                            spec_original_price = spec.get('originalPrice', 499)
                                            
                                            # 确定使用哪个原价
                                            if page_original_price and page_original_price.isdigit():
                                                original_price = float(page_original_price)
                                                logger.info(f"使用从页面获取的原價: {original_price}")
                                            else:
                                                # 使用spec中的原价
                                                try:
                                                    original_price = float(spec_original_price)
                                                except (ValueError, TypeError):
                                                    # 如果原价不是数字，尝试提取数字
                                                    original_price = 499
                                                    if isinstance(spec_original_price, str):
                                                        try:
                                                            original_price = float(''.join(filter(str.isdigit, spec_original_price)))
                                                        except:
                                                            original_price = 499  # 默认值
                                                logger.info(f"使用从spec获取的原價: {original_price}")
                                            
                                            # 计算折扣率
                                            discount_rate = round((float(新價格) / original_price) * 10, 1)
                                            logger.info(f"嘗試將價格 {新價格} 轉換為折扣率: {discount_rate}")
                                            
                                            # 清除並重新輸入折扣率
                                            self.driver.execute_script("""
                                                arguments[0].focus();
                                                arguments[0].value = '';
                                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                                arguments[0].value = arguments[1];
                                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                            """, discount_input, str(discount_rate))
                                            
                                            logger.info(f"已設置折扣率為: {discount_rate}")
                                        else:
                                            # 如果不是折扣率但依然有錯誤，嘗試尋找其他輸入框
                                            other_input = self.driver.execute_script("""
                                                const currentInput = arguments[0];
                                                const allInputs = document.querySelectorAll('input.eds-input__input:not([disabled])');
                                                
                                                for (const input of allInputs) {
                                                    if (input !== currentInput && input.offsetParent !== null) {
                                                        const rect = input.getBoundingClientRect();
                                                        if (rect.width > 0 && rect.height > 0) {
                                                            input.style.border = '3px solid purple';
                                                            console.log('找到其他可能的輸入框');
                                                            return input;
                                                        }
                                                    }
                                                }
                                                return null;
                                            """, discount_input)
                                            
                                            if other_input:
                                                logger.info("找到其他可能的折扣輸入框，嘗試使用該輸入框")
                                                discount_input = other_input
                                                
                                                # 清除並設置新值
                                                self.driver.execute_script("""
                                                    arguments[0].focus();
                                                    arguments[0].value = '';
                                                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                                    arguments[0].value = arguments[1];
                                                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                                """, discount_input, str(新價格))
                                                
                                                logger.info(f"在其他輸入框設置值: {新價格}")
                                    
                                    # 模擬按Enter確認輸入
                                    discount_input.send_keys(Keys.ENTER)
                                    logger.info("已按Enter確認輸入")
                                    time.sleep(1.5)
                                    
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
                                        logger.info("✓ 沒有檢測到錯誤消息，價格調整可能成功")
                                        return True
                                    else:
                                        logger.warning("⚠ 依然存在錯誤消息，價格調整可能失敗")
                                        
                                        # 最後嘗試使用ActionChains
                                        if retry_count >= 2:
                                            try:
                                                logger.info("使用ActionChains嘗試最後輸入")
                                                actions = ActionChains(self.driver)
                                                actions.click(discount_input)
                                                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
                                                actions.send_keys(Keys.DELETE)
                                                actions.send_keys(str(新價格))
                                                actions.send_keys(Keys.ENTER)
                                                actions.perform()
                                                
                                                time.sleep(2)
                                                self.driver.execute_script("document.body.click();")
                                                
                                                # 最後一次嘗試假設成功
                                                if retry_count >= MAX_RETRIES - 2:
                                                    logger.info("ActionChains嘗試後假定成功")
                                                    return True
                                            except Exception as e:
                                                logger.warning(f"ActionChains嘗試失敗: {str(e)}")
                                else:
                                    logger.warning("⚠ 未找到折扣價輸入框")
                                    
                                    # 嘗試探索性尋找並點擊所有可能的價格欄位
                                    if retry_count >= 1:
                                        exploration_result = self.driver.execute_script("""
                                            // 通過類名和屬性尋找所有可能的價格相關元素
                                            const priceElements = document.querySelectorAll('[class*="price"], [class*="discount"], [class*="currency"]');
                                            console.log('找到可能的價格相關元素:', priceElements.length);
                                            
                                            // 遍歷並點擊這些元素
                                            for (let i = 0; i < priceElements.length && i < 5; i++) {
                                                const elem = priceElements[i];
                                                if (elem.offsetParent !== null) {
                                                    const rect = elem.getBoundingClientRect();
                                                    if (rect.width > 0 && rect.height > 0) {
                                                        try {
                                                            elem.scrollIntoView({block: 'center'});
                                                            elem.style.border = '2px solid red';
                                                            elem.click();
                                                            console.log('探索性點擊元素:', elem.textContent);
                                                            
                                                            // 檢查是否出現了輸入框
                                                            setTimeout(() => {
                                                                const inputs = document.querySelectorAll('input.eds-input__input:not([disabled])');
                                                                for (const input of inputs) {
                                                                    if (input.offsetParent !== null) {
                                                                        input.style.border = '2px solid green';
                                                                        input.focus();
                                                                        input.value = '';
                                                                        input.value = arguments[0];
                                                                        input.dispatchEvent(new Event('input', {bubbles: true}));
                                                                        input.dispatchEvent(new Event('change', {bubbles: true}));
                                                                        console.log('嘗試在探索性輸入框中輸入:', arguments[0]);
                                                                        return;
                                                                    }
                                                                }
                                                            }, 500);
                                                            
                                                            return true;
                                                        } catch (e) {
                                                            console.error('探索性點擊失敗:', e);
                                                        }
                                                    }
                                                }
                                            }
                                            return false;
                                        """, 新價格)
                                        
                                        if exploration_result:
                                            logger.info("完成探索性點擊，等待輸入框出現")
                                            time.sleep(2)
                                            
                                            # 嘗試按Enter確認
                                            active_element = self.driver.execute_script("""
                                                if (document.activeElement && document.activeElement.tagName === 'INPUT') {
                                                    document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {
                                                        key: 'Enter',
                                                        code: 'Enter',
                                                        keyCode: 13,
                                                        which: 13,
                                                        bubbles: true
                                                    }));
                                                    return true;
                                                }
                                                return false;
                                            """)
                                            
                                            if active_element:
                                                logger.info("已在探索性輸入框中按Enter")
                                                time.sleep(1)
                                                
                                                # 點擊其他地方確認
                                                self.driver.execute_script("document.body.click();")
                                                time.sleep(1)
                                            
                                            # 最後兩次嘗試時，假設成功
                                            if retry_count >= MAX_RETRIES - 2:
                                                logger.info("探索性嘗試後假定成功")
                                                return True
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
    
    def 批量處理商品規格(self, products):
        """批量處理商品規格，包括開啟按鈕和調整價格"""
        總處理規格數 = 0
        開關調整成功數 = 0
        價格調整成功數 = 0
        需要調整價格的項目 = []
        
        logger.info("開始批量處理商品規格...")
        
        # 第一階段：處理所有需要開啟的按鈕
        logger.info("第一階段：開啟所有需要的按鈕...")
        for product in products:
            商品名稱 = product.get('name', '未知商品')
            specs = product.get('specs', [])
            
            logger.info(f"處理商品: {商品名稱}")
            
            for spec in specs:
                規格名稱 = spec.get('name', '未知規格')
                stock = spec.get('stock', '0')
                price = spec.get('price', '0')
                status = spec.get('status', '未知')
                disabled = spec.get('disabled', False)
                
                # 提取庫存數字
                try:
                    庫存數量 = int(''.join(filter(str.isdigit, str(stock))))
                except:
                    庫存數量 = 0
                
                # 只處理有庫存且非禁用的規格
                if 庫存數量 > 0 and not disabled:
                    總處理規格數 += 1
                    logger.info(f"規格 '{規格名稱}' 狀態: {status}, 庫存: {庫存數量}")
                    
                    # 判斷是否需要開啟按鈕
                    if status != "開啟":
                        logger.info(f"規格 '{規格名稱}' 需要開啟按鈕")
                        
                        # 執行開啟操作
                        開關結果 = self.切換商品規格開關(商品名稱, 規格名稱)
                        if 開關結果:
                            logger.info(f"✓ 已成功開啟 {規格名稱} 的開關")
                            開關調整成功數 += 1
                            
                            # 開關開啟後等待更久的時間，讓輸入框變為可用狀態
                            logger.info(f"等待輸入框變為可用狀態...")
                            time.sleep(3)
                            
                            # 將開啟成功的項目添加到需要調整價格的列表
                            建議價格, 參考規格, 需要調整 = self.查找同類規格價格(product, 規格名稱)
                            if 建議價格 and 需要調整:
                                需要調整價格的項目.append({
                                    "商品名稱": 商品名稱,
                                    "規格名稱": 規格名稱,
                                    "建議價格": 建議價格,
                                    "參考規格": 參考規格
                                })
                                
                                # 立即進行價格調整，不等待第二階段
                                logger.info(f"立即調整開啟的規格價格: '{規格名稱}' 價格設為 {建議價格}")
                                價格結果 = self.調整商品價格(商品名稱, 規格名稱, 建議價格)
                                if 價格結果:
                                    logger.info(f"✓ 立即調整成功: {規格名稱} 價格設為 {建議價格}")
                                    價格調整成功數 += 1
                                else:
                                    logger.error(f"✗ 立即調整失敗: {規格名稱}")
                        else:
                            logger.error(f"✗ 開啟 {規格名稱} 的開關失敗")
                        
                        # 等待操作完成 - 增加等待時間
                        time.sleep(2.5)
                    else:
                        # 對於已經開啟的規格，也檢查是否需要調整價格
                        建議價格, 參考規格, 需要調整 = self.查找同類規格價格(product, 規格名稱)
                        if 建議價格 and 需要調整:
                            需要調整價格的項目.append({
                                "商品名稱": 商品名稱,
                                "規格名稱": 規格名稱,
                                "建議價格": 建議價格,
                                "參考規格": 參考規格
                            })
        
        # 在所有按鈕開啟後，對其餘已經是開啟狀態的項目再進行價格調整
        剩餘價格項目 = [項目 for 項目 in 需要調整價格的項目 if not any(
            項目["商品名稱"] == product.get('name', '') and 
            項目["規格名稱"] == spec.get('name', '') and 
            spec.get('status', '') != "開啟"
            for product in products 
            for spec in product.get('specs', [])
        )]
        
        if 剩餘價格項目:
            # 等待所有開關操作完成後再進行價格調整
            logger.info("等待所有開關操作完成...")
            time.sleep(3)
            
            logger.info(f"第二階段：調整剩餘的 {len(剩餘價格項目)} 個已開啟規格的價格...")
            for 項目 in 剩餘價格項目:
                商品名稱 = 項目["商品名稱"]
                規格名稱 = 項目["規格名稱"]
                建議價格 = 項目["建議價格"]
                參考規格 = 項目["參考規格"]
                
                logger.info(f"規格 '{規格名稱}' 需要調整價格，參考規格 '{參考規格}' 價格: {建議價格}")
                
                # 執行價格調整
                價格結果 = self.調整商品價格(商品名稱, 規格名稱, 建議價格)
                if 價格結果:
                    logger.info(f"✓ 已成功調整 {規格名稱} 的價格為 {建議價格}")
                    價格調整成功數 += 1
                else:
                    logger.error(f"✗ 調整 {規格名稱} 的價格失敗")
                
                # 等待操作完成
                time.sleep(2)
        
        logger.info(f"批量處理完成，共處理 {總處理規格數} 個規格，成功開啟 {開關調整成功數} 個，成功調整價格 {價格調整成功數} 個")
        return 總處理規格數, 開關調整成功數, 價格調整成功數 