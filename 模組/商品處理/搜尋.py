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
                            
                            // 方法2: 如果沒有從文本中找到折扣價格，優先檢查輸入框
                            // 在編輯模式下，輸入框通常包含實際價格值
                            if (!foundDiscountPrice) {
                                console.log("從文本中未找到折扣價格，檢查輸入框...");
                                // 查找輸入框
                                const inputs = specElem.querySelectorAll('input[type="text"], input:not([type]), input.eds-input__input, input[class*="price"], input[class*="discount"]');
                                console.log(`找到 ${inputs.length} 個輸入框`);
                                
                                if (inputs.length > 0) {
                                    // 第一遍：尋找帶有折扣相關標籤的輸入框
                                    for (let i = 0; i < inputs.length; i++) {
                                        const input = inputs[i];
                                        // 記錄輸入框的信息
                                        console.log(`輸入框${i+1}: placeholder="${input.placeholder}", value="${input.value}"`);
                                        
                                        // 獲取相關的標籤文本
                                        const nearestLabel = findNearestLabel(input);
                                        if (nearestLabel) {
                                            console.log(`輸入框${i+1}相關標籤: "${nearestLabel}"`);
                                            
                                            // 檢查是否是折扣價相關的輸入框
                                            const isDiscountInput = 
                                                nearestLabel.includes('優惠') || 
                                                nearestLabel.includes('折扣') || 
                                                nearestLabel.includes('特價') ||
                                                nearestLabel.includes('促銷') ||
                                                input.name && (
                                                    input.name.includes('discount') ||
                                                    input.name.includes('sale') ||
                                                    input.name.includes('special')
                                                );
                                                
                                            // 檢查是否是原價相關的輸入框
                                            const isOriginalInput = 
                                                nearestLabel.includes('原價') || 
                                                nearestLabel.includes('定價') ||
                                                input.name && (
                                                    input.name.includes('original') ||
                                                    input.name.includes('regular')
                                                );
                                            
                                            // 優先處理折扣價輸入框
                                            if (isDiscountInput && input.value && !isNaN(parseFloat(input.value)) && parseFloat(input.value) > 0) {
                                                // 檢查是否是折扣率（小於10通常是折扣率如7折）或折扣價
                                                if (parseFloat(input.value) < 10 && !nearestLabel.includes('特價') && !nearestLabel.includes('優惠價')) {
                                                    discountRate = input.value;
                                                    console.log(`找到折扣率: ${discountRate}`);
                                                    
                                                    // 如果有原價，計算折扣價
                                                    if (originalPrice) {
                                                        price = Math.round(parseFloat(originalPrice) * parseFloat(discountRate) / 10).toString();
                                                        priceType = '折扣率計算價';
                                                        console.log(`從折扣率計算折扣價: ${price} = ${originalPrice} × ${discountRate}/10`);
                                                        foundDiscountPrice = true;
                                                    }
                                                } else {
                                                    price = input.value;
                                                    priceType = '輸入框折扣價';
                                                    console.log(`從折扣輸入框獲取價格: ${price}`);
                                                    // 高亮這個輸入框幫助診斷
                                                    input.style.border = '3px solid blue';
                                                    foundDiscountPrice = true;
                                                }
                                            } 
                                            // 保存原價信息
                                            else if (isOriginalInput && input.value && !isNaN(parseFloat(input.value))) {
                                                originalPrice = input.value;
                                                console.log(`從輸入框獲取原價: ${originalPrice}`);
                                            }
                                        }
                                    }
                                    
                                    // 第二遍：如果仍未找到折扣價，根據輸入框位置進行猜測
                                    // 在蝦皮的編輯界面中，通常第二個輸入框是折扣價，第一個是原價
                                    if (!foundDiscountPrice && inputs.length >= 2) {
                                        // 檢查第二個輸入框是否有值
                                        if (inputs[1].value && !isNaN(parseFloat(inputs[1].value)) && parseFloat(inputs[1].value) > 0) {
                                            price = inputs[1].value;
                                            priceType = '第二輸入框折扣價';
                                            console.log(`從第二輸入框獲取折扣價: ${price}`);
                                            // 高亮這個輸入框
                                            inputs[1].style.border = '3px solid purple';
                                            foundDiscountPrice = true;
                                            
                                            // 如果第一個輸入框有值，可能是原價
                                            if (!originalPrice && inputs[0].value && !isNaN(parseFloat(inputs[0].value))) {
                                                originalPrice = inputs[0].value;
                                                console.log(`從第一輸入框獲取原價: ${originalPrice}`);
                                            }
                                        }
                                    }
                                    
                                    // 如果只有一個輸入框且還沒找到折扣價，使用它的值
                                    if (!foundDiscountPrice && inputs.length == 1 && inputs[0].value && !isNaN(parseFloat(inputs[0].value))) {
                                        price = inputs[0].value;
                                        priceType = '單一輸入框';
                                        console.log(`從唯一輸入框獲取價格: ${price}`);
                                        // 高亮這個輸入框
                                        inputs[0].style.border = '3px solid orange';
                                        foundDiscountPrice = true;
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
            
            # 檢查URL是否包含特定的編輯標識
            current_url = self.driver.current_url
            logger.info(f"當前URL: {current_url}")
            
            # 檢查URL是否明確指示編輯模式
            if '/edit' in current_url:
                logger.info("✓ URL顯示處於編輯模式")
                return True
            
            # 使用JavaScript檢查頁面上的編輯模式指示元素和URL
            is_edit_mode = self.driver.execute_script("""
                // 檢查URL是否包含編輯相關的字段
                const url = window.location.href;
                if (url.includes('/edit')) {
                    console.log('URL顯示處於編輯模式');
                    return true;
                }
                
                // 檢查是否有確認按鈕，確認按鈕通常只在編輯模式出現
                const confirmButtons = document.querySelectorAll('.eds-button--confirm, .btn-confirm, button[type="submit"]');
                if (confirmButtons.length > 0) {
                    for (const btn of confirmButtons) {
                        if (btn.offsetParent !== null && 
                            (btn.textContent.includes('確認') || 
                             btn.textContent.includes('保存') || 
                             btn.textContent.includes('提交'))) {
                            console.log('找到確認按鈕，處於編輯模式');
                            return true;
                        }
                    }
                }
                
                // 檢查是否可以編輯商品狀態
                const switches = document.querySelectorAll('.eds-switch');
                if (switches.length > 0) {
                    // 檢查開關是否可以互動，即是否有點擊事件或非禁用狀態
                    for (const switchEl of switches) {
                        if (!switchEl.classList.contains('eds-switch--disabled') && 
                            switchEl.offsetParent !== null) {
                            console.log('找到可互動的開關元素，處於編輯模式');
                            return true;
                        }
                    }
                }
                
                // 檢查是否有輸入框可以編輯，通常編輯模式會有可編輯的輸入框
                const inputs = document.querySelectorAll('input:not([type="hidden"]), textarea');
                if (inputs.length > 0) {
                    for (const input of inputs) {
                        if (!input.disabled && !input.readOnly && 
                            input.offsetParent !== null &&
                            getComputedStyle(input).display !== 'none') {
                            console.log('找到可編輯的輸入框，處於編輯模式');
                            return true;
                        }
                    }
                }
                
                // 檢查頁面標題或內容是否明確包含編輯字樣
                const editIndicators = document.querySelectorAll('[class*="edit"], [id*="edit"]');
                for (const indicator of editIndicators) {
                    if (indicator.classList.contains('discount-edit-item') || 
                        indicator.classList.contains('edit-mode') ||
                        indicator.id.includes('edit-mode')) {
                        console.log('找到明確的編輯模式標識元素');
                        return true;
                    }
                }
                
                console.log('未檢測到編輯模式特徵');
                return false;
            """)
            
            if is_edit_mode:
                logger.info("✓ 檢測到編輯模式元素")
                return True
            
            # 額外檢查: 嘗試判斷頁面是否有"編輯"按鈕
            edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '編輯')]")
            if edit_buttons and any(btn.is_displayed() for btn in edit_buttons):
                logger.info("⚠ 找到「編輯」按鈕，表示頁面未處於編輯模式")
                return False
            
            logger.info("⚠ 未檢測到編輯模式元素")
            return False
            
        except Exception as e:
            logger.error(f"檢查編輯模式時發生錯誤: {str(e)}")
            return False
    
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