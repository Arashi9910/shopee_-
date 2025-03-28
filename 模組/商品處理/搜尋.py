"""
搜尋模組

包含與商品搜索相關的功能：
- 搜尋商品
- 搜尋特定前綴商品
"""

import time
import logging
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 設置日誌
logger = logging.getLogger(__name__)

class 商品搜尋:
    """處理商品搜尋相關功能的類"""
    
    def __init__(self, driver):
        """初始化商品搜尋類
        
        Args:
            driver: Selenium WebDriver實例
        """
        self.driver = driver
    
    def 搜尋商品(self):
        """搜尋頁面上的商品和規格

        Returns:
            list: 商品列表
        """
        logger.info("開始尋找頁面上的商品...")
        
        # 檢查當前URL
        current_url = self.driver.current_url
        logger.info(f"當前頁面URL: {current_url}")
        
        # 等待頁面加載
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.discount-item-component, div.discount-edit-item"))
            )
        except:
            logger.warning("等待商品元素超時，嘗試繼續執行...")
        
        # 使用JavaScript獲取商品
        products_js = """
        function extractProducts() {
            // 尋找商品卡片
            const productCards = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
            
            if (!productCards || productCards.length === 0) {
                console.log("無法找到商品卡片");
                return [];
            }
            
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
            
            const products = [];
            
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
                                const ntMatches = priceText.match(/NT\$\s*(\d+)/g);
                                if (ntMatches && ntMatches.length > 0) {
                                    // 如果有多個NT$價格，第一個通常是原價，第二個通常是折扣價
                                    if (ntMatches.length >= 2) {
                                        const origMatch = ntMatches[0].match(/\d+/);
                                        const discMatch = ntMatches[1].match(/\d+/);
                                        
                                        if (origMatch) result.originalPrice = origMatch[0];
                                        if (discMatch) result.discountPrice = discMatch[0];
                                    } else {
                                        // 只有一個價格
                                        const match = ntMatches[0].match(/\d+/);
                                        if (match) result.discountPrice = match[0];
                                    }
                                }
                                
                                // 提取折扣率，通常是x.x折格式
                                const rateMatch = priceText.match(/(\d+(\.\d+)?)\s*折/);
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
                                    const ntCount = (priceText.match(/NT\$/g) || []).length;
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
            
            return products;
        }
        
        return extractProducts();
        """
        
        products = self.driver.execute_script(products_js)
        
        if not products:
            logger.warning("找不到任何商品，頁面可能結構不同或尚未載入")
            
            # 診斷頁面結構
            page_diagnostic = self.driver.execute_script("""
            return {
                productCardExists: document.querySelectorAll('div.discount-item-component, div.discount-edit-item').length > 0,
                bodyContent: document.body.textContent.substring(0, 1000),
                visibleElements: Array.from(document.querySelectorAll('div, span, h1, h2, h3, table')).slice(0, 20).map(el => el.tagName + (el.className ? '.' + el.className.replace(/ /g, '.') : '')),
                url: window.location.href
            }
            """)
            
            logger.info(f"頁面診斷: 商品卡片存在={page_diagnostic.get('productCardExists')}, URL={page_diagnostic.get('url')}")
            logger.info(f"頁面可見元素: {page_diagnostic.get('visibleElements')}")
            
            # 嘗試保存截圖
            try:
                screenshot_path = "page_diagnosis.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"已保存頁面截圖到 {screenshot_path}")
            except Exception as e:
                logger.error(f"無法保存截圖: {str(e)}")
            
            # 建立一個空商品列表
            products = []
            
        # 統計並返回
        total_specs = sum(len(product.get('specs', [])) for product in products)
        logger.info(f"找到 {len(products)} 個商品和 {total_specs} 個規格")
        
        return products
    
    def 搜尋特定前綴商品(self, prefix="Fee"):
        """搜尋特定前綴的商品
        
        Args:
            prefix (str): 商品名稱前綴
            
        Returns:
            dict: 包含符合前綴的商品信息
        """
        logger.info(f"開始搜尋前綴為 '{prefix}' 的商品")
        
        try:
            # 使用JavaScript搜尋特定前綴的商品
            products_info = self.driver.execute_script(r"""
                // 函數: 找到最近的標籤
                function findNearestLabel(input) {
                    // 檢查兄弟元素
                    let sibling = input.previousElementSibling;
                    while (sibling) {
                        if (sibling.tagName === 'LABEL' || sibling.querySelector('label')) {
                            return sibling.textContent.trim();
                        }
                        sibling = sibling.previousElementSibling;
                    }
                    
                    // 檢查父元素中的標籤
                    let parent = input.parentElement;
                    for (let i = 0; i < 3; i++) {
                        if (!parent) break;
                        
                        // 檢查父元素是否是標籤或包含標籤
                        if (parent.tagName === 'LABEL') {
                            return parent.textContent.trim();
                        }
                        
                        const label = parent.querySelector('label');
                        if (label) {
                            return label.textContent.trim();
                        }
                        
                        parent = parent.parentElement;
                    }
                    
                    return null;
                }
                
                const prefix = arguments[0];
                
                // 找到所有商品卡片
                const productCards = document.querySelectorAll('.item-card, .product-item, [class*="item-card"], [class*="product-card"]');
                console.log('找到商品卡片數量:', productCards.length);
                
                const matchedProducts = [];
                let totalMatchedSpecs = 0;
                
                // 篩選符合前綴的商品
                for (const card of productCards) {
                    try {
                        // 獲取商品名稱
                        const nameElement = card.querySelector('.item-card-header, .item-name, [class*="name"], h3, h4');
                        const name = nameElement ? nameElement.textContent.trim() : '';
                        
                        // 檢查商品名稱是否符合前綴
                        if (name && name.startsWith(prefix)) {
                            // 獲取規格元素
                            const specElems = card.querySelectorAll('.item-model, .spec-item, [class*="spec"], [class*="model"]');
                            const specs = [];
                            
                            // 提取每個規格信息
                            for (const specElem of specElems) {
                                try {
                                    // 獲取規格名稱
                                    const specNameElem = specElem.querySelector('.model-name, [class*="name"], div:first-child');
                                    const specName = specNameElem ? specNameElem.textContent.trim() : '未知規格';
                                    
                                    // 獲取庫存信息
                                    const stockElem = specElem.querySelector('.model-stock, [class*="stock"], div:nth-child(2)');
                                    const stock = stockElem ? stockElem.textContent.trim() : '0';
                                    
                                    // 獲取價格信息
                                    const priceElems = specElem.querySelectorAll('.item-price, [class*="price"], div:nth-child(3)');
                                    let priceTexts = [];
                                    
                                    // 收集所有價格相關文字
                                    for (const priceElem of priceElems) {
                                        const priceText = priceElem.textContent.trim();
                                        if (priceText && !priceTexts.includes(priceText)) {
                                            priceTexts.push(priceText);
                                        }
                                    }
                                    
                                    // 尋找輸入欄位以獲取原價和折扣價
                                    const inputs = specElem.querySelectorAll('input');
                                    let originalPrice = '';
                                    let discountPrice = '';
                                    let discountRate = '';
                                    
                                    // 嘗試從輸入欄位中獲取價格信息
                                    for (const input of inputs) {
                                        const label = findNearestLabel(input);
                                        const value = input.value;
                                        
                                        if (label) {
                                            if (label.includes('原價') || label.includes('original')) {
                                                originalPrice = value;
                                            } else if (label.includes('折扣') || label.includes('discount')) {
                                                // 判斷是折扣率還是折扣價
                                                if (parseFloat(value) < 10) {
                                                    discountRate = value;
                                                } else {
                                                    discountPrice = value;
                                                }
                                            }
                                        }
                                    }
                                    
                                    // 獲取開關狀態
                                    const switchElem = specElem.querySelector('.eds-switch, [class*="switch"]');
                                    const status = switchElem && switchElem.classList.contains('eds-switch--open') ? '開啟' : '關閉';
                                    
                                    // 檢查是否被禁用
                                    const disabled = 
                                        specElem.classList.contains('disabled') || 
                                        specElem.getAttribute('disabled') !== null ||
                                        specElem.style.opacity < 0.5;
                                    
                                    // 使用最複雜的價格文字作為顯示價格
                                    const priceDisplay = priceTexts.sort((a, b) => b.length - a.length)[0] || '';
                                    
                                    // 提取價格數字和類型
                                    let price = '';
                                    let priceType = '';
                                    
                                    // 處理價格文字
                                    if (priceDisplay) {
                                        // 檢查是否包含折扣信息
                                        if (priceDisplay.includes('折')) {
                                            const match = priceDisplay.match(/([0-9.]+)折/);
                                            if (match) {
                                                price = match[1];
                                                priceType = '折扣率值';
                                                discountRate = match[1];
                                            }
                                        } 
                                        // 檢查是否包含價格信息
                                        else if (priceDisplay.includes('NT$') || priceDisplay.includes('$')) {
                                            const match = priceDisplay.match(/NT\$([0-9,]+)|$([0-9,]+)/);
                                            if (match) {
                                                price = match[1] || match[2];
                                                priceType = '折扣價';
                                                discountPrice = price;
                                            }
                                        }
                                    }
                                    
                                    // 如果沒有從顯示中獲取到價格，則使用輸入欄位中的值
                                    if (!price) {
                                        if (discountPrice) {
                                            price = discountPrice;
                                            priceType = '折扣價';
                                        } else if (discountRate) {
                                            price = discountRate;
                                            priceType = '折扣率值';
                                        } else if (originalPrice) {
                                            price = originalPrice;
                                            priceType = '原價';
                                        }
                                    }
                                    
                                    // 添加規格信息
                                    specs.push({
                                        name: specName,
                                        stock: stock,
                                        price: price,
                                        priceType: priceType,
                                        priceDisplay: priceDisplay,
                                        originalPrice: originalPrice,
                                        discountPrice: discountPrice,
                                        discountRate: discountRate,
                                        status: status,
                                        disabled: disabled
                                    });
                                    
                                    totalMatchedSpecs++;
                                } catch (specError) {
                                    console.error('處理規格時出錯:', specError);
                                }
                            }
                            
                            // 添加符合前綴的商品信息
                            matchedProducts.push({
                                name: name,
                                specs: specs
                            });
                        }
                        
                    } catch (cardError) {
                        console.error('處理商品卡片時出錯:', cardError);
                    }
                }
                
                return {
                    product_count: matchedProducts.length,
                    spec_count: totalMatchedSpecs,
                    products: matchedProducts
                };
            """, prefix)
            
            logger.info(f"找到 {products_info.get('product_count', 0)} 個符合前綴 '{prefix}' 的商品")
            return products_info
            
        except Exception as e:
            logger.error(f"搜尋特定前綴商品時發生錯誤: {str(e)}")
            return {"product_count": 0, "spec_count": 0, "products": []} 

    def 檢查是否編輯模式(self):
        """檢查當前頁面是否處於編輯模式
        
        Returns:
            bool: 是否處於編輯模式
        """
        try:
            logger.info("檢查是否處於編輯模式...")
            
            # 使用JavaScript檢查頁面上的編輯模式指示元素
            is_edit_mode = self.driver.execute_script("""
                // 檢查URL是否包含編輯相關的字段
                const url = window.location.href;
                if (url.includes('editor') || url.includes('edit') || url.includes('modify')) {
                    console.log('URL顯示可能處於編輯模式');
                    return true;
                }
                
                // 檢查是否有編輯模式特有的元素
                const editElements = document.querySelectorAll('.eds-switch, .eds-button, .edit-button, button[class*="edit"]');
                if (editElements.length > 0) {
                    console.log('找到編輯模式特有元素');
                    return true;
                }
                
                // 檢查頁面標題或內容
                const titleElement = document.querySelector('title, h1, .page-title');
                if (titleElement && (titleElement.textContent.includes('編輯') || titleElement.textContent.includes('Edit'))) {
                    console.log('頁面標題包含編輯字樣');
                    return true;
                }
                
                console.log('未檢測到編輯模式特徵');
                return false;
            """)
            
            if is_edit_mode:
                logger.info("✓ 檢測到編輯模式元素: .eds-switch")
            else:
                logger.info("⚠ 未檢測到編輯模式元素")
            
            return is_edit_mode
            
        except Exception as e:
            logger.error(f"檢查編輯模式時發生錯誤: {str(e)}")
            return False
    
    def 進入編輯模式(self):
        """嘗試進入編輯模式
        
        Returns:
            bool: 是否成功進入編輯模式
        """
        MAX_RETRIES = 3
        
        if self.檢查是否編輯模式():
            logger.info("已處於編輯模式，無需操作")
            return True
        
        logger.info("嘗試進入編輯模式...")
        
        for retry in range(MAX_RETRIES):
            try:
                logger.info(f"第 {retry + 1}/{MAX_RETRIES} 次嘗試尋找編輯按鈕...")
                
                # 尋找編輯按鈕
                edit_button = self.driver.execute_script("""
                    // 查找可能的編輯按鈕
                    const editButtons = [
                        ...document.querySelectorAll('button[class*="edit"], a[class*="edit"], [class*="button"][class*="edit"]'),
                        ...document.querySelectorAll('button:contains("編輯"), a:contains("編輯"), [role="button"]:contains("編輯")'),
                        ...document.querySelectorAll('button:contains("Edit"), a:contains("Edit"), [role="button"]:contains("Edit")')
                    ];
                    
                    if (editButtons.length === 0) {
                        console.log('未找到編輯按鈕');
                        return null;
                    }
                    
                    console.log(`找到 ${editButtons.length} 個可能的編輯按鈕`);
                    
                    // 優先選擇文本包含「編輯」的按鈕
                    for (const button of editButtons) {
                        if (button.textContent.includes('編輯') || button.textContent.includes('Edit')) {
                            button.style.border = '3px solid red';
                            console.log('找到確定的編輯按鈕:', button.textContent);
                            return button;
                        }
                    }
                    
                    // 選擇第一個可能的編輯按鈕
                    editButtons[0].style.border = '3px solid yellow';
                    console.log('使用可能的編輯按鈕:', editButtons[0].textContent);
                    return editButtons[0];
                """)
                
                if not edit_button:
                    logger.warning("未找到編輯按鈕")
                    time.sleep(1)
                    continue
                
                # 點擊按鈕
                logger.info("點擊編輯按鈕...")
                self.driver.execute_script("arguments[0].click();", edit_button)
                time.sleep(3)  # 等待頁面加載
                
                # 檢查是否成功進入編輯模式
                if self.檢查是否編輯模式():
                    logger.info("✓ 已成功進入編輯模式")
                    return True
                
                logger.warning("點擊編輯按鈕後未進入編輯模式，重試...")
                
            except Exception as e:
                logger.error(f"嘗試進入編輯模式時發生錯誤: {str(e)}")
            
            time.sleep(2)
        
        logger.error("⚠ 無法進入編輯模式，已達最大重試次數")
        return False 