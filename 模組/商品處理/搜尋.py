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
from selenium.webdriver.common.action_chains import ActionChains

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
            dict: 包含商品列表的字典，格式為 {"product_count": int, "spec_count": int, "products": list}
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
        
        # 使用JavaScript抓取頁面上的商品信息
        products_js = """
        // 尋找所有商品卡片
        const productCards = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
        console.log('找到商品卡片數量:', productCards.length);
        
        // 初始化結果陣列
        const products = [];
        
        for (const card of productCards) {
            try {
                // 獲取商品名稱
                const nameElem = card.querySelector('div.ellipsis-content.single');
                if (!nameElem) continue;
                
                const productName = nameElem.textContent.trim();
                console.log('找到商品:', productName);
                
                // 獲取該商品的所有規格
                const specElements = card.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                console.log(`商品 "${productName}" 的規格數量:`, specElements.length);
                
                const specs = [];
                
                for (const specElem of specElements) {
                    try {
                        // 獲取規格名稱
                        const specNameElem = specElem.querySelector('div.ellipsis-content.single');
                        if (!specNameElem) continue;
                        
                        const specName = specNameElem.textContent.trim();
                        console.log('找到規格:', specName);
                        
                        // 獲取庫存
                        const stockElem = specElem.querySelector('div.item-content.item-stock');
                        const stock = stockElem ? stockElem.textContent.trim() : '0';
                        
                        // 重新實現價格獲取邏輯，專注於蝦皮折扣價
                        let price = '0';
                        let priceType = '未知';
                        let discountRate = '';  // 記錄折扣率
                        let originalPrice = ''; // 記錄原價
                        let foundDiscountPrice = false;
                        
                        // 1. 最優先: 查找含有明確顯示NT$折扣價的元素
                        const allVisibleText = [];
                        specElem.querySelectorAll('*').forEach(el => {
                            if (el.offsetParent !== null && el.textContent && el.textContent.includes('NT$')) {
                                allVisibleText.push({
                                    element: el,
                                    text: el.textContent.trim()
                                });
                            }
                        });
                        
                        // 優先處理包含折扣價的文本
                        for (const item of allVisibleText) {
                            // 優先查找包含折扣或特價標記的元素
                            if (item.text.includes('折扣') || item.text.includes('特價') || 
                                item.text.includes('優惠') || item.text.includes('NT$') && 
                               (item.element.classList.contains('discount') || 
                                item.element.className.includes('discount'))) {
                                
                                const ntMatch = item.text.match(/NT\$\s*(\d+)/);
                                if (ntMatch) {
                                    price = ntMatch[1];
                                    priceType = '折扣價標記';
                                    console.log(`從折扣標記找到價格: ${price}, 文本="${item.text}"`);
                                    foundDiscountPrice = true;
                                    break;
                                }
                            }
                        }
                        
                        // 2. 檢查蝦皮特有的價格輸入框
                        if (!foundDiscountPrice) {
                            // 找到所有輸入框，特別是帶有NT$標記的價格輸入框
                            const priceInputs = specElem.querySelectorAll('input.eds-input__input[data-v-7fcfdf7e], input[class*="discount"], input[class*="price"]');
                            console.log(`找到 ${priceInputs.length} 個價格相關輸入框`);
                            
                            // 查找前綴為NT$的輸入框（通常是折扣價格框）
                            const ntPrefixedInputs = [];
                            
                            for (let i = 0; i < priceInputs.length; i++) {
                                const input = priceInputs[i];
                                console.log(`輸入框 ${i+1}: value="${input.value}", placeholder="${input.placeholder}"`);
                                
                                // 查找NT$前綴元素
                                const parentElement = input.parentElement;
                                if (parentElement) {
                                    const prefixElement = parentElement.querySelector('span, div, label');
                                    if (prefixElement && prefixElement.textContent.trim() === 'NT$') {
                                        console.log(`找到前綴為NT$的輸入框 ${i+1}, 值=${input.value}`);
                                        ntPrefixedInputs.push({
                                            input: input,
                                            index: i
                                        });
                                    }
                                }
                                
                                // 查看輸入框之前的元素是否包含NT$
                                const prevSibling = input.previousElementSibling;
                                if (prevSibling && prevSibling.textContent.includes('NT$')) {
                                    console.log(`找到前面元素包含NT$的輸入框 ${i+1}, 值=${input.value}`);
                                    ntPrefixedInputs.push({
                                        input: input,
                                        index: i
                                    });
                                }
                            }
                            
                            // 優先使用NT$前綴的輸入框值（特價輸入框）
                            if (ntPrefixedInputs.length > 0) {
                                // 按照索引排序，通常第一個NT$輸入框是特價
                                ntPrefixedInputs.sort((a, b) => a.index - b.index);
                                const firstNtInput = ntPrefixedInputs[0].input;
                                
                                if (firstNtInput.value && !isNaN(parseFloat(firstNtInput.value))) {
                                    price = firstNtInput.value;
                                    priceType = 'NT$特價輸入框';
                                    console.log(`從NT$特價輸入框獲取價格: ${price}`);
                                    foundDiscountPrice = true;
                                }
                            }
                            // 如果沒有找到NT$前綴的輸入框，嘗試使用位置判斷
                            else if (priceInputs.length >= 2) {
                                // 在蝦皮的折扣編輯頁面，通常第一個輸入框是特價，第二個是折扣率
                                const firstInput = priceInputs[0];
                                const secondInput = priceInputs[1];
                                
                                // 檢查哪個輸入框的值更可能是特價（通常特價大於10，折扣率小於10）
                                if (firstInput.value && !isNaN(parseFloat(firstInput.value))) {
                                    const firstValue = parseFloat(firstInput.value);
                                    const secondValue = secondInput.value && !isNaN(parseFloat(secondInput.value)) ? parseFloat(secondInput.value) : 0;
                                    
                                    // 如果第一個值大於10且第二個值小於10，則第一個很可能是特價
                                    if (firstValue > 10 && secondValue < 10) {
                                        price = firstInput.value;
                                        priceType = '第一輸入框特價';
                                        console.log(`從第一輸入框獲取特價: ${price} (第二輸入框可能是折扣率: ${secondValue})`);
                                        foundDiscountPrice = true;
                                    }
                                    // 如果第一個值小於10且第二個值大於10，則第二個可能是特價
                                    else if (firstValue < 10 && secondValue > 10) {
                                        price = secondInput.value;
                                        priceType = '第二輸入框特價';
                                        console.log(`從第二輸入框獲取特價: ${price} (第一輸入框可能是折扣率: ${firstValue})`);
                                        foundDiscountPrice = true;
                                    }
                                    // 如果兩個值都大於10，優先使用第一個值
                                    else if (firstValue > 10) {
                                        price = firstInput.value;
                                        priceType = '預設特價輸入框';
                                        console.log(`使用第一輸入框值作為特價: ${price}`);
                                        foundDiscountPrice = true;
                                    }
                                }
                            }
                            // 如果只有一個輸入框，且值大於10，可能是特價
                            else if (priceInputs.length === 1 && priceInputs[0].value && !isNaN(parseFloat(priceInputs[0].value)) && parseFloat(priceInputs[0].value) > 10) {
                                price = priceInputs[0].value;
                                priceType = '單一特價輸入框';
                                console.log(`從單一輸入框獲取特價: ${price}`);
                                foundDiscountPrice = true;
                            }
                        }
                        
                        // 3. 查找所有可能的折扣價格文本
                        if (!foundDiscountPrice) {
                            // 對所有包含NT$的文本按長度排序（較短的可能是單一價格，優先選擇）
                            allVisibleText.sort((a, b) => a.text.length - b.text.length);
                            
                            for (const item of allVisibleText) {
                                const ntMatch = item.text.match(/NT\$\s*(\d+)/);
                                if (ntMatch) {
                                    // 檢查是單一價格還是多個價格
                                    const allPrices = item.text.match(/NT\$\s*\d+/g);
                                    
                                    if (allPrices && allPrices.length === 1) {
                                        // 單一價格，很可能是折扣價
                                        price = ntMatch[1];
                                        priceType = '單一價格文本';
                                        console.log(`從單一價格文本找到價格: ${price}, 文本="${item.text}"`);
                                        foundDiscountPrice = true;
                                        break;
                                    } else if (allPrices && allPrices.length > 1) {
                                        // 多個價格，最後一個通常是折扣價
                                        const lastPrice = allPrices[allPrices.length-1].match(/\d+/)[0];
                                        price = lastPrice;
                                        priceType = '多價格文本';
                                        console.log(`從多價格文本找到價格: ${price}, 文本="${item.text}"`);
                                        foundDiscountPrice = true;
                                        break;
                                    }
                                }
                            }
                        }
                        
                        // 4. 尋找帶有折扣率的文本，計算折扣價
                        if (!foundDiscountPrice) {
                            // 尋找折扣率
                            for (const item of allVisibleText) {
                                const rateMatch = item.text.match(/([0-9.]+)\s*折/);
                                if (rateMatch) {
                                    discountRate = rateMatch[1];
                                    console.log(`找到折扣率: ${discountRate}, 文本="${item.text}"`);
                                    
                                    // 尋找原價
                                    for (const priceItem of allVisibleText) {
                                        if (priceItem.text.includes('原價') || priceItem.text.includes('定價')) {
                                            const origMatch = priceItem.text.match(/NT\$\s*(\d+)/);
                                            if (origMatch) {
                                                originalPrice = origMatch[1];
                                                console.log(`找到原價: ${originalPrice}, 文本="${priceItem.text}"`);
                                                
                                                // 計算折扣價
                                                if (originalPrice && discountRate) {
                                                    price = Math.round(parseFloat(originalPrice) * parseFloat(discountRate) / 10).toString();
                                                    priceType = '折扣率計算價';
                                                    console.log(`計算得到折扣價: ${price} = ${originalPrice} × ${discountRate}/10`);
                                                    foundDiscountPrice = true;
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    
                                    if (foundDiscountPrice) break;
                                }
                            }
                        }
                        
                        // 5. 最後手段：嘗試從任何包含NT$的文本中提取價格
                        if (!foundDiscountPrice && allVisibleText.length > 0) {
                            for (const item of allVisibleText) {
                                const ntMatch = item.text.match(/NT\$\s*(\d+)/);
                                if (ntMatch) {
                                    price = ntMatch[1];
                                    priceType = '通用價格文本';
                                    console.log(`從通用文本找到價格: ${price}, 文本="${item.text}"`);
                                    foundDiscountPrice = true;
                                    break;
                                }
                            }
                        }
                        
                        // 檢查獲取到的價格
                        let priceDisplay = '';
                        if (foundDiscountPrice) {
                            priceDisplay = `NT$${price}`;
                            if (discountRate) priceDisplay += ` (${discountRate}折)`;
                        } else {
                            priceDisplay = '未知價格';
                        }
                        
                        // 獲取狀態 (開啟/關閉)
                        const switchElem = specElem.querySelector('div.eds-switch');
                        const status = switchElem && switchElem.classList.contains('eds-switch--open') ? '開啟' : '關閉';
                        
                        // 檢查是否禁用
                        const disabled = switchElem && switchElem.classList.contains('eds-switch--disabled');
                        
                        // 添加規格信息
                        specs.push({
                            name: specName,
                            stock: stock,
                            price: price,
                            priceType: priceType,
                            priceDisplay: priceDisplay,
                            originalPrice: originalPrice,
                            discountRate: discountRate,
                            status: status,
                            disabled: disabled
                        });
                    } catch (specError) {
                        console.error('處理規格時出錯:', specError);
                    }
                }
                
                // 將商品添加到結果中
                if (specs.length > 0) {
                    products.push({
                        name: productName,
                        specs: specs
                    });
                }
            } catch (cardError) {
                console.error('處理商品卡片時出錯:', cardError);
            }
        }
        
        console.log('總共找到商品數量:', products.length);
        return products;
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
            
        # 統計並返回結果字典 (而非直接返回商品列表)
        total_specs = sum(len(product.get('specs', [])) for product in products)
        logger.info(f"找到 {len(products)} 個商品和 {total_specs} 個規格")
        
        return {
            "product_count": len(products),
            "spec_count": total_specs,
            "products": products
        }
    
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
        """檢查當前是否處於編輯模式"""
        try:
            logger.info("檢查是否處於編輯模式...")
            
            # 檢查當前URL
            current_url = self.driver.current_url
            logger.info(f"當前URL: {current_url}")
            
            # 檢查URL是否包含編輯相關的參數
            if 'edit' in current_url.lower() or 'discount/edit' in current_url.lower():
                logger.info("URL包含編輯相關參數")
                return True
            
            # 使用JavaScript檢查頁面元素
            is_edit_mode = self.driver.execute_script("""
                // 檢查是否存在編輯模式特有的元素
                const editElements = document.querySelectorAll('.eds-switch, .discount-edit-item, .discount-edit-item-model-component');
                if (editElements.length > 0) {
                    return true;
                }
                
                // 檢查是否存在編輯按鈕
                const editButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
                    btn.textContent.includes('編輯') || 
                    btn.textContent.includes('編輯活動') || 
                    btn.textContent.includes('編輯折扣')
                );
                if (editButtons.length > 0) {
                    return false;
                }
                
                return false;
            """)
            
            if is_edit_mode:
                logger.info("✓ 檢測到編輯模式元素")
                return True
            else:
                logger.info("✗ 未檢測到編輯模式元素")
                return False
                
        except Exception as e:
            logger.error(f"檢查編輯模式時發生錯誤: {str(e)}")
            return False
    
    def 點擊編輯按鈕(self):
        """尋找並點擊折扣活動編輯按鈕"""
        try:
            logger.info("尋找頁面上的編輯按鈕...")
            
            # 方法1: 優先嘗試使用更精確的XPath查找「編輯活動」按鈕
            edit_activity_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '編輯活動')]")
            if edit_activity_buttons:
                for button in edit_activity_buttons:
                    if button.is_displayed():
                        logger.info(f"找到「編輯活動」按鈕: {button.text}")
                        
                        # 滾動到按鈕可見
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # 不再高亮顯示按鈕
                        logger.info("嘗試點擊「編輯活動」按鈕...")
                        try:
                            # 嘗試多種點擊方式
                            try:
                                button.click()
                                logger.info("已使用WebDriver原生點擊方法")
                            except:
                                # 如果直接點擊失敗，使用JavaScript點擊
                                self.driver.execute_script("arguments[0].click();", button)
                                logger.info("已使用JavaScript點擊方法")
                        except Exception as click_err:
                            logger.warning(f"點擊按鈕時出錯: {str(click_err)}")
                        
                        logger.info("✓ 已嘗試點擊「編輯活動」按鈕")
                        time.sleep(5)  # 延長等待時間，確保頁面加載
                        return True
            
            # 方法2: 使用XPath查找包含「編輯」文字的按鈕
            edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '編輯')]")
            
            # 方法3: 使用多個可能的選擇器
            if not edit_buttons:
                selectors = [
                    ".edit-button",
                    "button.eds-button--primary",
                    "button.activity-edit-btn",
                    ".activity-operation-btn button",
                    ".activity-operation__edit-btn",
                    ".page-action-buttons button",  # 蝦皮常用的操作按鈕區域
                    ".action-buttons button",
                    ".operation-btn"
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
                        
                        # 點擊按鈕
                        try:
                            button.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", button)
                            
                        logger.info("✓ 成功點擊編輯按鈕")
                        
                        # 等待頁面加載
                        time.sleep(3)
                        return True
            
            # 方法4: 直接使用JavaScript在頁面上定位和點擊「編輯活動」按鈕
            logger.info("嘗試使用JavaScript主動搜尋和點擊「編輯活動」按鈕...")
            js_result = self.driver.execute_script("""
                // 查找所有可能的按鈕
                const textOptions = ['編輯活動', '編輯', '編輯折扣', 'Edit', '編集'];
                const allElements = document.querySelectorAll('button, a, [role="button"], .btn, .button, [class*="edit"], [class*="btn"]');
                
                // 遍歷所有元素，優先查找包含「編輯活動」文字的按鈕
                for (const text of textOptions) {
                    for (const elem of allElements) {
                        // 檢查元素及其子元素的文本
                        const elemText = elem.textContent.trim();
                        if (elemText.includes(text) && elem.offsetParent !== null) {
                            console.log(`找到符合文字「${text}」的按鈕: ${elemText}`);
                            
                            // 記錄按鈕信息，但不改變按鈕樣式
                            
                            try {
                                // 嘗試各種方式激活按鈕
                                elem.scrollIntoView({block: 'center', behavior: 'smooth'});
                                
                                // 記錄按鈕信息，幫助診斷
                                console.log({
                                    text: elemText,
                                    tagName: elem.tagName,
                                    className: elem.className,
                                    id: elem.id,
                                    href: elem.href,
                                    isDisabled: elem.disabled,
                                    style: elem.style.cssText
                                });
                                
                                // 移除可能的disabled屬性
                                elem.disabled = false;
                                elem.removeAttribute('disabled');
                                
                                // 模擬鼠標懸停
                                const mouseoverEvent = new MouseEvent('mouseover', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                elem.dispatchEvent(mouseoverEvent);
                                
                                // 延遲後點擊
                                setTimeout(() => {
                                    // 嘗試多種點擊方式
                                    elem.click();
                                    
                                    // 如果是連結，可能需要直接跳轉
                                    if (elem.href) {
                                        window.location.href = elem.href;
                                    }
                                }, 300);
                                
                                return true;
                            } catch (e) {
                                console.error('點擊按鈕時出錯:', e);
                            }
                        }
                    }
                }
                
                // 特別處理：尋找帶有特定類名的編輯按鈕
                const specialButtons = document.querySelectorAll('.edit-button, .activity-edit-btn, .page-action-button, [class*="edit-activity"]');
                for (const btn of specialButtons) {
                    if (btn.offsetParent !== null) {
                        console.log('找到具有特定類名的編輯按鈕:', btn);
                        
                        // 嘗試點擊
                        try {
                            btn.scrollIntoView({block: 'center'});
                            setTimeout(() => btn.click(), 200);
                            return true;
                        } catch (e) {
                            console.error('點擊具有特定類名的按鈕時出錯:', e);
                        }
                    }
                }
                
                // 未找到任何合適的按鈕
                return false;
            """)
            
            if js_result:
                logger.info("✓ JavaScript成功找到並點擊了編輯按鈕")
                time.sleep(5)  # 等待較長時間
                return True
            
            # 方法5: 可能是頁面有遮擋層或需要先點擊其他元素
            logger.info("嘗試找出並點擊可能的遮擋層或需點擊的元素...")
            overlay_result = self.driver.execute_script("""
                // 嘗試關閉可能的彈窗或遮擋層
                const closeButtons = document.querySelectorAll('.close-btn, .modal-close, [class*="close"], button:contains("關閉"), button:contains("取消"), button:contains("Cancel")');
                for (const btn of closeButtons) {
                    if (btn.offsetParent !== null) {
                        console.log('找到可能的關閉按鈕:', btn);
                        btn.click();
                    }
                }
                
                // 嘗試點擊可能需要先點擊的頁面區域
                const actionAreas = document.querySelectorAll('.card-header, .activity-title, .discount-title, [class*="header"]');
                for (const area of actionAreas) {
                    if (area.offsetParent !== null) {
                        area.click();
                        console.log('點擊了可能的操作區域:', area);
                    }
                }
                
                return document.querySelector('button:contains("編輯")') !== null;
            """)
            
            if overlay_result:
                logger.info("處理了可能的遮擋層，現在嘗試再次點擊編輯按鈕")
                return self.點擊編輯按鈕()  # 遞迴調用，重新嘗試
            
            logger.warning("✗ 未找到編輯按鈕，所有嘗試方法均失敗")
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
    
    def 前往下一頁(self):
        """點擊下一頁按鈕，進入下一頁商品列表"""
        logger.info("嘗試前往下一頁...")
        
        try:
            # 嘗試找到下一頁按鈕
            next_button = self.driver.execute_script("""
                // 尋找下一頁按鈕
                const nextButtons = document.querySelectorAll('.eds-pager__button-next, button[class*="next"], button:has(i.eds-icon svg path[d*="9.18933983,8 L5.21966991,11.9696699"])');
                
                if (nextButtons.length > 0) {
                    for (const btn of nextButtons) {
                        // 檢查按鈕是否可見
                        if (btn.offsetParent !== null) {
                            const rect = btn.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                // 僅在控制台標記找到的按鈕，不改變頁面顯示
                                console.log('找到下一頁按鈕', btn);
                                return btn;
                            }
                        }
                    }
                }
                return null;
            """)
            
            if next_button:
                logger.info("找到下一頁按鈕")
                
                # 確保按鈕在視野內，滾動行為更像人類操作
                self.driver.execute_script("""
                    // 緩慢滾動到按鈕位置
                    let button = arguments[0];
                    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    let targetPosition = button.getBoundingClientRect().top + scrollTop - 200;
                    
                    // 使用平滑滾動效果
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                """, next_button)
                
                # 等待滾動完成
                time.sleep(1.5)
                
                # 模擬滑鼠移動到按鈕上
                self.driver.execute_script("""
                    // 模擬滑鼠懸停操作
                    const button = arguments[0];
                    const mouseoverEvent = new MouseEvent('mouseover', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    button.dispatchEvent(mouseoverEvent);
                """, next_button)
                
                # 等待滑鼠事件生效
                time.sleep(0.5)
                
                # 使用原生的WebDriver點擊
                try:
                    # 首先嘗試使用原生點擊
                    actions = ActionChains(self.driver)
                    actions.move_to_element(next_button).pause(0.3).click().perform()
                    logger.info("已使用ActionChains點擊下一頁按鈕")
                except Exception as e:
                    logger.warning(f"ActionChains點擊失敗: {str(e)}，嘗試使用JavaScript點擊")
                    # 在原生點擊失敗的情況下，使用更溫和的JavaScript點擊
                    self.driver.execute_script("""
                        // 先發送mousedown事件
                        const button = arguments[0];
                        const mousedownEvent = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        button.dispatchEvent(mousedownEvent);
                        
                        // 短暫等待後發送click事件
                        setTimeout(() => {
                            const clickEvent = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            button.dispatchEvent(clickEvent);
                        }, 100);
                    """, next_button)
                    logger.info("已使用JavaScript模擬點擊下一頁按鈕")
                
                # 等待頁面加載，時間更長以確保加載完成
                time.sleep(5)
                
                # 確認是否成功翻頁
                current_url = self.driver.current_url
                logger.info(f"翻頁後的URL: {current_url}")
                
                # 檢查URL是否變成404頁面
                if "404" in current_url or "error" in current_url:
                    logger.error("點擊後跳轉到錯誤頁面")
                    return False
                
                # 等待頁面上的新商品加載出來
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.discount-item-component, div.discount-edit-item"))
                    )
                    logger.info("成功載入下一頁商品")
                except TimeoutException:
                    logger.warning("等待新頁面商品元素超時")
                
                return True
            else:
                logger.warning("未找到下一頁按鈕，可能已是最後一頁")
                return False
        
        except Exception as e:
            logger.error(f"前往下一頁時發生錯誤: {str(e)}")
            return False
    
    def 批量處理多頁商品(self, 頁數):
        """批量處理多頁商品的規格
        
        Args:
            頁數 (int): 要處理的頁數
            
        Returns:
            tuple: (是否成功, 已處理頁數, 處理結果摘要, 調整記錄列表)
        """
        # 導入依賴模組
        from .批量處理 import 批量處理
        
        已處理頁數 = 0
        總處理規格數 = 0
        總開關成功數 = 0
        總價格成功數 = 0
        所有調整記錄 = []  # 收集所有頁面的調整記錄
        
        try:
            # 獲取目前頁數和當前頁面
            當前頁 = 1
            
            # 循環處理多個頁面
            for 頁數索引 in range(頁數):
                logger.info(f"處理第 {當前頁}/{頁數} 頁")
                
                # 獲取當前頁的商品數據
                搜尋結果 = self.搜尋商品()
                
                # 確保搜尋結果有效
                if not 搜尋結果 or not isinstance(搜尋結果, dict):
                    logger.warning(f"⚠ 第 {當前頁} 頁搜尋結果無效，可能頁面結構發生變化")
                    當前頁 += 1
                    continue
                
                # 確保搜尋結果包含必要的鍵
                if not all(key in 搜尋結果 for key in ["product_count", "spec_count", "products"]):
                    logger.warning(f"⚠ 第 {當前頁} 頁搜尋結果缺少必要的鍵")
                    missing_keys = [key for key in ["product_count", "spec_count", "products"] if key not in 搜尋結果]
                    logger.warning(f"缺少的鍵: {missing_keys}")
                    
                    # 嘗試修復結果字典
                    if "products" not in 搜尋結果:
                        logger.error("搜尋結果缺少 'products' 鍵，無法繼續")
                        continue
                    
                    if "product_count" not in 搜尋結果:
                        搜尋結果["product_count"] = len(搜尋結果["products"])
                        logger.info(f"已添加缺少的 'product_count' 鍵: {搜尋結果['product_count']}")
                        
                    if "spec_count" not in 搜尋結果:
                        搜尋結果["spec_count"] = sum(len(product.get('specs', [])) for product in 搜尋結果["products"])
                        logger.info(f"已添加缺少的 'spec_count' 鍵: {搜尋結果['spec_count']}")
                
                商品列表 = 搜尋結果.get("products", [])
                
                if not 商品列表:
                    logger.warning(f"⚠ 第 {當前頁} 頁未找到任何商品")
                    
                    # 診斷頁面結構
                    try:
                        page_diagnostic = self.driver.execute_script("""
                        return {
                            html: document.documentElement.outerHTML.substring(0, 1000),
                            productElements: document.querySelectorAll('div.discount-item-component, div.discount-edit-item').length,
                            url: window.location.href,
                            title: document.title
                        }
                        """)
                        logger.info(f"頁面診斷: URL={page_diagnostic.get('url')}, 標題={page_diagnostic.get('title')}")
                        logger.info(f"產品元素數量: {page_diagnostic.get('productElements')}")
                        
                        # 嘗試保存截圖
                        screenshot_path = f"page_diagnosis_page{當前頁}.png"
                        self.driver.save_screenshot(screenshot_path)
                        logger.info(f"已保存第 {當前頁} 頁截圖到 {screenshot_path}")
                    except Exception as diag_error:
                        logger.error(f"頁面診斷時發生錯誤: {str(diag_error)}")
                    
                    當前頁 += 1
                    continue
                    
                logger.info(f"第 {當前頁} 頁找到 {len(商品列表)} 個商品")
                
                # 針對當前頁進行處理 - 創建批量處理對象
                try:
                    批量處理器 = 批量處理(self.driver)
                    
                    # 處理當前頁商品
                    處理結果 = 批量處理器.批量處理商品規格(商品列表)
                    
                    # 檢查處理結果
                    if isinstance(處理結果, tuple):
                        # 新格式，預期包含四個值：處理數, 開關成功數, 價格成功數, 調整記錄列表
                        if len(處理結果) >= 4 and isinstance(處理結果[3], list):
                            處理數, 開關成功數, 價格成功數, 當頁調整記錄 = 處理結果[:4]
                            所有調整記錄.extend(當頁調整記錄)
                            logger.info(f"收集到 {len(當頁調整記錄)} 條調整記錄")
                        # 舊格式，只包含三個值
                        elif len(處理結果) >= 3:
                            處理數, 開關成功數, 價格成功數 = 處理結果[:3]
                        
                        總處理規格數 += 處理數
                        總開關成功數 += 開關成功數
                        總價格成功數 += 價格成功數
                        
                        logger.info(f"第 {當前頁} 頁處理完成: 處理 {處理數} 個規格，成功開關 {開關成功數} 個，成功調價 {價格成功數} 個")
                    else:
                        logger.warning(f"⚠ 第 {當前頁} 頁處理結果格式不正確: {處理結果}")
                        # 嘗試提取數據，提高容錯性
                        if isinstance(處理結果, tuple):
                            logger.info(f"處理結果是元組，長度為 {len(處理結果)}")
                            # 嘗試提取可用的數據
                            for i, val in enumerate(處理結果):
                                if i == 0 and isinstance(val, int):
                                    總處理規格數 += val
                                    logger.info(f"已提取處理數: {val}")
                                elif i == 1 and isinstance(val, int):
                                    總開關成功數 += val
                                    logger.info(f"已提取開關成功數: {val}")
                                elif i == 2 and isinstance(val, int):
                                    總價格成功數 += val
                                    logger.info(f"已提取價格成功數: {val}")
                                elif i == 3 and isinstance(val, list):
                                    所有調整記錄.extend(val)
                                    logger.info(f"已提取調整記錄: {len(val)} 條")
                        elif isinstance(處理結果, dict):
                            logger.info("處理結果是字典，嘗試提取數據")
                            總處理規格數 += 處理結果.get("處理數", 0) 
                            總開關成功數 += 處理結果.get("開關成功數", 0)
                            總價格成功數 += 處理結果.get("價格成功數", 0)
                            調整記錄 = 處理結果.get("調整記錄", [])
                            if isinstance(調整記錄, list):
                                所有調整記錄.extend(調整記錄)
                                logger.info(f"從字典中提取調整記錄: {len(調整記錄)} 條")
                
                except Exception as batch_error:
                    logger.error(f"處理第 {當前頁} 頁時發生錯誤: {str(batch_error)}")
                    # 繼續處理下一頁，提高程序的穩定性
                
                已處理頁數 += 1
                
                # 如果還有下一頁要處理
                if 頁數索引 < 頁數 - 1:
                    logger.info(f"準備前往第 {當前頁 + 1} 頁...")
                    
                    # 前往下一頁
                    if not self.前往下一頁():
                        logger.warning(f"⚠ 無法前往第 {當前頁 + 1} 頁，提前結束")
                        break
                    
                    # 在新頁面等待加載
                    time.sleep(5)
                    
                    # 確保在編輯模式(頁面跳轉可能會退出編輯模式)
                    if not self.檢查是否編輯模式():
                        logger.warning(f"前往第 {當前頁 + 1} 頁後未處於編輯模式，嘗試重新進入")
                        if not self.進入編輯模式():
                            logger.error(f"⚠ 無法在第 {當前頁 + 1} 頁進入編輯模式，跳過該頁")
                            當前頁 += 1
                            continue
                    
                    當前頁 += 1
            
            # 處理完成，顯示總結果
            if 已處理頁數 > 0:
                logger.info(f"多頁處理完成: 共處理 {已處理頁數}/{頁數} 頁，{總處理規格數} 個規格")
                logger.info(f"成功開關: {總開關成功數} 個，成功調價: {總價格成功數} 個")
                logger.info(f"收集到 {len(所有調整記錄)} 條調整記錄")
                
                # 創建處理結果摘要
                處理結果摘要 = {
                    "總處理規格數": 總處理規格數,
                    "總開關成功數": 總開關成功數,
                    "總價格成功數": 總價格成功數
                }
                
                return True, 已處理頁數, 處理結果摘要, 所有調整記錄
            else:
                logger.warning("⚠ 未能成功處理任何頁面")
                return False, 0, {"總處理規格數": 0, "總開關成功數": 0, "總價格成功數": 0}, []
        
        except Exception as e:
            logger.error(f"⚠ 多頁批量處理過程中發生錯誤: {str(e)}")
            # 嘗試捕獲錯誤堆疊以便診斷
            import traceback
            logger.error(f"詳細錯誤堆疊:\n{traceback.format_exc()}")
            
            # 即使發生錯誤，也返回已處理的結果
            處理結果摘要 = {
                "總處理規格數": 總處理規格數,
                "總開關成功數": 總開關成功數,
                "總價格成功數": 總價格成功數
            }
            
            return False, 已處理頁數, 處理結果摘要, 所有調整記錄
