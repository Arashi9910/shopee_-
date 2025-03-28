import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ShopeePageAnalyzer:
    def __init__(self, driver):
        """初始化分析器，接收一個已連接的Selenium WebDriver實例"""
        self.driver = driver
        
    def get_page_structure(self):
        """獲取頁面的基本結構，返回JSON格式的結果"""
        try:
            # 嘗試提取元素結構
            structure = self.driver.execute_script("""
                function getElementInfo(element, depth = 0, maxDepth = 3) {
                    if (!element || depth > maxDepth) return null;
                    
                    // 基本元素信息
                    let info = {
                        tagName: element.tagName,
                        id: element.id || '',
                        className: element.className || '',
                        text: element.innerText ? element.innerText.slice(0, 100) : '',
                        attributes: {},
                        children: []
                    };
                    
                    // 只分析特定元素的屬性和子元素
                    if (['DIV', 'BUTTON', 'A', 'SPAN', 'INPUT'].includes(element.tagName)) {
                        // 收集重要屬性
                        for (let attr of element.attributes) {
                            info.attributes[attr.name] = attr.value;
                        }
                        
                        // 遞歸分析子元素 (限制數量以避免過大)
                        if (depth < maxDepth) {
                            let childrenCount = Math.min(element.children.length, 20);
                            for (let i = 0; i < childrenCount; i++) {
                                let childInfo = getElementInfo(element.children[i], depth + 1, maxDepth);
                                if (childInfo) {
                                    info.children.push(childInfo);
                                }
                            }
                        }
                    }
                    
                    return info;
                }
                
                // 從頁面根元素開始分析
                let rootElements = [];
                let importantContainers = document.querySelectorAll('.discount-edit-item, .item-content, .content-box');
                
                if (importantContainers.length > 0) {
                    // 如果找到特定容器，就分析這些容器
                    for (let i = 0; i < Math.min(importantContainers.length, 20); i++) {
                        rootElements.push(getElementInfo(importantContainers[i], 0, 2));
                    }
                } else {
                    // 否則分析整個body的直接子元素
                    let bodyChildren = document.body.children;
                    for (let i = 0; i < Math.min(bodyChildren.length, 20); i++) {
                        rootElements.push(getElementInfo(bodyChildren[i], 0, 2));
                    }
                }
                
                return rootElements;
            """)
            
            return structure
        except Exception as e:
            return {"error": str(e)}
    
    def find_product_elements(self):
        """尋找並返回商品相關元素"""
        try:
            # 嘗試不同的選擇器來找到商品元素
            selectors = [
                "div.discount-edit-item",       # 原始選擇器
                ".product-item",                # 可能的替代選擇器
                "[data-product-id]",            # 通過屬性查找
                ".product-list > div",          # 通過父元素查找
                "div.item-card",                # 常見的商品卡片類名
                "div.product-card",             # 常見的商品卡片類名
                "div.item-container",           # 通用商品容器
                "div.product",                  # 簡單產品選擇器
                "div[data-item]",               # 使用data屬性
                "tr.product-row",               # 表格行方式呈現的商品
                "div.discount-item",            # 可能的折扣項目
                "div.model-item",               # 商品型號項目
                "li.product-item",              # 列表中的商品
                "div.merchant-product-item",    # 商家產品項目
                "article.product"               # 使用article標籤的商品
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0:
                    return {
                        "selector": selector,
                        "count": len(elements),
                        "sample": self._extract_element_info(elements[0]) if elements else {}
                    }
            
            # 如果標準選擇器找不到，嘗試使用JavaScript進行更靈活的搜索
            return self._find_elements_with_js()
        
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_element_info(self, element):
        """從元素中提取基本信息"""
        try:
            return {
                "tag": element.tag_name,
                "text": element.text[:100] if element.text else "",
                "class": element.get_attribute("class"),
                "id": element.get_attribute("id")
            }
        except:
            return {"error": "無法提取元素信息"}
    
    def _find_elements_with_js(self):
        """使用JavaScript找出可能的商品元素"""
        return self.driver.execute_script("""
            // 尋找可能的商品元素特徵
            function findPossibleProductElements() {
                let candidates = [];
                
                // 方法1: 尋找包含特定文字的元素
                document.querySelectorAll('div').forEach(div => {
                    let text = div.innerText.toLowerCase();
                    if ((text.includes('商品') || text.includes('product') || 
                         text.includes('item') || text.includes('庫存')) && 
                        div.children.length > 0) {
                        candidates.push({
                            element: div,
                            reason: '文字匹配',
                            text: div.innerText.substring(0, 50)
                        });
                    }
                });
                
                // 方法2: 尋找有特定屬性的元素
                document.querySelectorAll('[data-product], [data-item], [product-id]').forEach(el => {
                    candidates.push({
                        element: el,
                        reason: '屬性匹配',
                        text: el.innerText.substring(0, 50)
                    });
                });
                
                // 方法3: 尋找重複結構的元素群組
                const groups = {};
                document.querySelectorAll('div').forEach(div => {
                    const className = div.className;
                    if (className && div.children.length > 0) {
                        if (!groups[className]) groups[className] = [];
                        groups[className].push(div);
                    }
                });
                
                // 檢查重複結構的元素群組是否可能是商品列表
                for (let className in groups) {
                    if (groups[className].length > 1 && groups[className].length < 100) {
                        // 多個相同結構，可能是商品列表
                        candidates.push({
                            element: groups[className][0],
                            reason: `群組匹配 (${groups[className].length} 個相同結構)`,
                            text: groups[className][0].innerText.substring(0, 50),
                            count: groups[className].length
                        });
                    }
                }
                
                return candidates; // 返回所有候選項，不限制數量
            }
            
            return findPossibleProductElements();
        """)
    
    def extract_all_products(self):
        """嘗試提取所有商品的詳細信息"""
        try:
            # 使用JavaScript提取商品信息
            products = self.driver.execute_script("""
                function extractProductDetails() {
                    // 嘗試各種可能的商品容器選擇器
                    const selectors = [
                        'div.discount-edit-item',
                        '.product-item',
                        '[data-product-id]',
                        '.product-list > div'
                    ];
                    
                    let products = [];
                    let productElements = [];
                    
                    // 嘗試每個選擇器
                    for (let selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            productElements = elements;
                            break;
                        }
                    }
                    
                    // 如果還是找不到，嘗試更進階的檢測
                    if (productElements.length === 0) {
                        // 尋找可能的列表項目
                        const divs = document.querySelectorAll('div');
                        const candidates = [];
                        
                        divs.forEach(div => {
                            // 如果元素包含庫存、價格等相關文字，可能是商品項目
                            if (div.innerText.includes('庫存') || 
                                div.innerText.includes('價格') || 
                                div.innerText.includes('規格')) {
                                candidates.push(div);
                            }
                        });
                        
                        // 使用所有找到的候選項，不再限制數量
                        productElements = candidates;
                    }
                    
                    // 處理找到的元素
                    for (let i = 0; i < productElements.length; i++) {
                        const el = productElements[i];
                        
                        // 提取商品信息
                        let product = {
                            index: i,
                            text: el.innerText,
                            specs: []
                        };
                        
                        // 尋找商品名稱
                        const nameEl = el.querySelector('.ellipsis-content.single, h3, .product-name');
                        if (nameEl) {
                            product.name = nameEl.innerText;
                        } else {
                            // 如果找不到明確的商品名稱元素，使用第一行文字
                            const text = el.innerText.split('\\n')[0];
                            product.name = text ? text.trim() : `商品 #${i+1}`;
                        }
                        
                        // 尋找規格信息
                        const specElements = el.querySelectorAll('.discount-edit-item-model-component, .spec-item, .variant-item');
                        
                        if (specElements.length > 0) {
                            // 有找到規格元素
                            for (let j = 0; j < specElements.length; j++) {
                                const spec = specElements[j];
                                
                                // 提取規格信息
                                let specInfo = {
                                    index: j
                                };
                                
                                // 尋找規格名稱
                                const specNameEl = spec.querySelector('.ellipsis-content.single, .spec-name, .variant-name');
                                if (specNameEl) {
                                    specInfo.name = specNameEl.innerText;
                                } else {
                                    specInfo.name = `規格 #${j+1}`;
                                }
                                
                                // 尋找庫存信息
                                const stockEl = spec.querySelector('.item-stock, .stock, [data-stock]');
                                if (stockEl) {
                                    specInfo.stock = stockEl.innerText;
                                    // 嘗試提取數字
                                    const stockMatch = stockEl.innerText.match(/\\d+/);
                                    if (stockMatch) {
                                        specInfo.stockNumber = parseInt(stockMatch[0], 10);
                                    }
                                }
                                
                                // 尋找價格信息
                                const priceEl = spec.querySelector('.item-price, .price, [data-price]');
                                if (priceEl) {
                                    specInfo.price = priceEl.innerText;
                                }
                                
                                // 尋找開關按鈕
                                const switchEl = spec.querySelector('.eds-switch, .switch, [role="switch"]');
                                if (switchEl) {
                                    specInfo.hasSwitch = true;
                                    specInfo.isOpen = switchEl.classList.contains('eds-switch--open') || 
                                                     switchEl.getAttribute('aria-checked') === 'true';
                                    specInfo.isDisabled = switchEl.classList.contains('eds-switch--disabled') || 
                                                         switchEl.getAttribute('disabled') === 'true';
                                    // 保存開關元素的引用路徑
                                    specInfo.switchPath = getElementPath(switchEl);
                                }
                                
                                product.specs.push(specInfo);
                            }
                        } else {
                            // 如果找不到規格元素，嘗試直接從商品元素中提取信息
                            let specInfo = {
                                index: 0,
                                name: '默認規格'
                            };
                            
                            // 尋找庫存信息
                            const stockEl = el.querySelector('[data-stock], .stock, *:contains("庫存")');
                            if (stockEl) {
                                specInfo.stock = stockEl.innerText;
                                const stockMatch = stockEl.innerText.match(/\\d+/);
                                if (stockMatch) {
                                    specInfo.stockNumber = parseInt(stockMatch[0], 10);
                                }
                            }
                            
                            // 尋找價格信息
                            const priceEl = el.querySelector('[data-price], .price, *:contains("$")');
                            if (priceEl) {
                                specInfo.price = priceEl.innerText;
                            }
                            
                            // 尋找開關按鈕
                            const switchEl = el.querySelector('.eds-switch, .switch, [role="switch"]');
                            if (switchEl) {
                                specInfo.hasSwitch = true;
                                specInfo.isOpen = switchEl.classList.contains('eds-switch--open') || 
                                                 switchEl.getAttribute('aria-checked') === 'true';
                                specInfo.isDisabled = switchEl.classList.contains('eds-switch--disabled') || 
                                                     switchEl.getAttribute('disabled') === 'true';
                                // 保存開關元素的引用路徑
                                specInfo.switchPath = getElementPath(switchEl);
                            }
                            
                            product.specs.push(specInfo);
                        }
                        
                        products.push(product);
                    }
                    
                    return products;
                }
                
                // 輔助函數：獲取元素的唯一路徑，以便後續查找
                function getElementPath(element) {
                    if (!element) return '';
                    
                    // 嘗試生成一個CSS選擇器路徑
                    let path = '';
                    let current = element;
                    
                    while (current && current !== document.body) {
                        let selector = current.tagName.toLowerCase();
                        
                        if (current.id) {
                            selector += '#' + current.id;
                            path = selector + (path ? ' > ' + path : '');
                            break; // ID是唯一的，不需要繼續向上
                        } else {
                            if (current.className) {
                                const classes = current.className.split(/\\s+/).filter(c => c);
                                selector += '.' + classes.join('.');
                            }
                            
                            // 添加索引
                            const siblings = current.parentNode ? Array.from(current.parentNode.children) : [];
                            const index = siblings.indexOf(current);
                            if (index > -1) {
                                selector += ':nth-child(' + (index + 1) + ')';
                            }
                        }
                        
                        path = selector + (path ? ' > ' + path : '');
                        current = current.parentNode;
                    }
                    
                    return path;
                }
                
                return extractProductDetails();
            """)
            
            return products
        except Exception as e:
            return {"error": str(e)}
    
    def toggle_product_switch(self, switch_path):
        """根據提供的路徑切換商品按鈕"""
        try:
            result = self.driver.execute_script("""
                const path = arguments[0];
                try {
                    // 嘗試使用提供的路徑找到元素
                    const element = document.querySelector(path);
                    if (!element) {
                        return { success: false, error: '找不到開關元素' };
                    }
                    
                    // 檢查是否被禁用
                    const isDisabled = element.classList.contains('eds-switch--disabled') || 
                                      element.getAttribute('disabled') === 'true';
                    if (isDisabled) {
                        return { success: false, error: '開關已被禁用' };
                    }
                    
                    // 點擊開關
                    element.click();
                    
                    // 檢查點擊後的狀態
                    const isOpen = element.classList.contains('eds-switch--open') || 
                                  element.getAttribute('aria-checked') === 'true';
                    
                    return { 
                        success: true, 
                        newState: isOpen ? '開啟' : '關閉'
                    };
                    
                } catch (e) {
                    return { success: false, error: e.toString() };
                }
            """, switch_path)
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_all_products(self, auto_enable=True):
        """自動處理所有商品，根據庫存狀態切換開關"""
        products = self.extract_all_products()
        
        results = []
        for product in products:
            product_result = {
                "name": product.get("name", f"商品 #{product['index']+1}"),
                "specs": []
            }
            
            for spec in product.get("specs", []):
                spec_result = {
                    "name": spec.get("name", f"規格 #{spec['index']+1}"),
                    "stock": spec.get("stock", "未知"),
                    "price": spec.get("price", "未知"),
                    "action": "無需操作"
                }
                
                # 檢查是否需要啟用
                if auto_enable and spec.get("hasSwitch"):
                    stock_number = spec.get("stockNumber", 0)
                    is_open = spec.get("isOpen", False)
                    is_disabled = spec.get("isDisabled", False)
                    
                    if stock_number > 0 and not is_disabled and not is_open:
                        # 需要啟用
                        switch_path = spec.get("switchPath")
                        if switch_path:
                            toggle_result = self.toggle_product_switch(switch_path)
                            spec_result["action"] = "已啟用" if toggle_result.get("success") else f"啟用失敗: {toggle_result.get('error')}"
                        else:
                            spec_result["action"] = "無法啟用：找不到開關路徑"
                
                product_result["specs"].append(spec_result)
            
            results.append(product_result)
            
        return results

    def find_pagination(self):
        """尋找頁面中的分頁控制元素"""
        try:
            pagination_info = self.driver.execute_script("""
                function findPaginationElements() {
                    // 尋找可能的分頁元素
                    const selectors = [
                        '.pagination',
                        '.pager',
                        '.page-navigation',
                        'nav.pagination',
                        'ul.pager',
                        'div[role="navigation"]',
                        '.page-numbers',
                        '.shopee-page-controller'
                    ];
                    
                    let paginationElement = null;
                    
                    // 嘗試每個選擇器
                    for (let selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            paginationElement = element;
                            break;
                        }
                    }
                    
                    if (!paginationElement) {
                        // 如果找不到分頁元素，嘗試找含有頁碼的元素
                        const pageElements = Array.from(document.querySelectorAll('a, button, span'))
                            .filter(el => {
                                // 檢查元素是否包含頁碼
                                const text = el.innerText || el.textContent;
                                if (!text) return false;
                                
                                // 檢查是否包含數字和特定的分頁文字
                                return (
                                    (text.match(/\\d+/) && (
                                        el.classList.contains('page') || 
                                        el.parentElement.classList.contains('page') ||
                                        /page|頁/.test(el.className.toLowerCase())
                                    )) ||
                                    text === '>' || 
                                    text === '<' || 
                                    text === '下一頁' || 
                                    text === '上一頁' ||
                                    text === '第一頁' ||
                                    text === '最末頁'
                                );
                            });
                            
                        if (pageElements.length > 0) {
                            // 找到疑似頁碼元素，尋找其父容器
                            const parent = pageElements[0].parentElement;
                            paginationElement = parent;
                        }
                    }
                    
                    if (paginationElement) {
                        // 找到分頁元素，提取頁碼信息
                        const pageLinks = Array.from(paginationElement.querySelectorAll('a, button, span'))
                            .filter(el => {
                                const text = el.innerText || el.textContent;
                                return text && text.match(/\\d+/);
                            })
                            .map(el => {
                                return {
                                    text: el.innerText || el.textContent,
                                    isActive: el.classList.contains('active') || 
                                             el.classList.contains('current') ||
                                             el.getAttribute('aria-current') === 'page',
                                    isDisabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
                                    element: el
                                };
                            });
                            
                        // 尋找下一頁按鈕
                        const nextPageButton = Array.from(paginationElement.querySelectorAll('a, button, span'))
                            .find(el => {
                                const text = el.innerText || el.textContent;
                                return text && (
                                    text === '>' || 
                                    text === '下一頁' || 
                                    text.includes('Next') ||
                                    el.classList.contains('next') ||
                                    el.getAttribute('aria-label') === '下一頁' ||
                                    el.getAttribute('aria-label') === 'Next Page'
                                );
                            });
                            
                        return {
                            found: true,
                            element: paginationElement,
                            pageLinks: pageLinks,
                            currentPage: pageLinks.find(p => p.isActive)?.text || '1',
                            totalPages: pageLinks.length > 0 ? Math.max(...pageLinks.map(p => parseInt(p.text.match(/\\d+/)[0]))) : 1,
                            hasNextPage: nextPageButton ? !nextPageButton.disabled && !nextPageButton.classList.contains('disabled') : false,
                            nextPagePath: nextPageButton ? getElementPath(nextPageButton) : null
                        };
                    }
                    
                    return { found: false };
                }
                
                // 輔助函數：獲取元素的唯一路徑
                function getElementPath(element) {
                    if (!element) return '';
                    
                    let path = '';
                    let current = element;
                    
                    while (current && current !== document.body) {
                        let selector = current.tagName.toLowerCase();
                        
                        if (current.id) {
                            selector += '#' + current.id;
                            path = selector + (path ? ' > ' + path : '');
                            break;
                        } else {
                            if (current.className) {
                                const classes = current.className.split(/\\s+/).filter(c => c);
                                selector += '.' + classes.join('.');
                            }
                            
                            const siblings = current.parentNode ? Array.from(current.parentNode.children) : [];
                            const index = siblings.indexOf(current);
                            if (index > -1) {
                                selector += ':nth-child(' + (index + 1) + ')';
                            }
                        }
                        
                        path = selector + (path ? ' > ' + path : '');
                        current = current.parentNode;
                    }
                    
                    return path;
                }
                
                return findPaginationElements();
            """)
            
            return pagination_info
        except Exception as e:
            return {"found": False, "error": str(e)}
            
    def navigate_to_next_page(self):
        """嘗試導航到下一頁"""
        try:
            pagination = self.find_pagination()
            
            if not pagination.get("found", False):
                return {"success": False, "error": "找不到分頁元素"}
                
            if not pagination.get("hasNextPage", False):
                return {"success": False, "error": "沒有下一頁"}
                
            next_page_path = pagination.get("nextPagePath")
            if not next_page_path:
                return {"success": False, "error": "找不到下一頁按鈕路徑"}
                
            # 點擊下一頁按鈕
            result = self.driver.execute_script("""
                const path = arguments[0];
                try {
                    const nextPageButton = document.querySelector(path);
                    if (!nextPageButton) {
                        return { success: false, error: '找不到下一頁按鈕' };
                    }
                    
                    // 滾動到按鈕位置
                    nextPageButton.scrollIntoView({behavior: 'smooth', block: 'center'});
                    
                    // 等待短暫時間
                    setTimeout(() => {
                        // 點擊按鈕
                        nextPageButton.click();
                    }, 500);
                    
                    return { success: true };
                } catch (e) {
                    return { success: false, error: e.toString() };
                }
            """, next_page_path)
            
            # 等待頁面載入
            if result.get("success", False):
                time.sleep(3)  # 給頁面加載的時間
                
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def process_all_pages(self, max_pages=5):
        """處理所有頁面的商品"""
        all_results = []
        current_page = 1
        
        while current_page <= max_pages:
            # 處理當前頁面的商品
            page_results = self.process_all_products(auto_enable=True)
            
            if isinstance(page_results, list):
                all_results.extend(page_results)
                
                # 查找分頁信息
                pagination = self.find_pagination()
                
                if pagination.get("found", False):
                    if pagination.get("hasNextPage", False):
                        # 導航到下一頁
                        navigation_result = self.navigate_to_next_page()
                        
                        if not navigation_result.get("success", False):
                            break  # 導航失敗，停止處理
                            
                        current_page += 1
                        time.sleep(3)  # 等待下一頁加載
                    else:
                        break  # 沒有下一頁
                else:
                    break  # 找不到分頁
            else:
                break  # 處理失敗
                
        return all_results

    def check_infinite_scroll(self):
        """檢查頁面是否使用無限滾動載入更多商品"""
        try:
            scroll_info = self.driver.execute_script("""
                function checkInfiniteScroll() {
                    // 保存當前頁面高度
                    const initialHeight = document.body.scrollHeight;
                    
                    // 向下滾動
                    window.scrollTo(0, document.body.scrollHeight * 0.8);
                    
                    // 等待短暫時間
                    return new Promise((resolve) => {
                        setTimeout(() => {
                            // 檢查滾動後高度是否變化
                            const newHeight = document.body.scrollHeight;
                            const heightChanged = newHeight > initialHeight;
                            
                            // 檢查是否有懶加載圖片或加載中指示器
                            const hasLazyLoadIndicators = !!document.querySelector('.loading, .loader, [data-loading]');
                            
                            resolve({
                                initialHeight: initialHeight,
                                newHeight: newHeight,
                                heightChanged: heightChanged,
                                hasLazyLoadIndicators: hasLazyLoadIndicators,
                                mayUseInfiniteScroll: heightChanged || hasLazyLoadIndicators
                            });
                        }, 2000); // 等待2秒觀察變化
                    });
                }
                
                return checkInfiniteScroll();
            """)
            
            return scroll_info
        except Exception as e:
            return {"mayUseInfiniteScroll": False, "error": str(e)}
            
    def load_more_with_scroll(self, max_scrolls=5):
        """通過滾動加載更多商品"""
        try:
            all_products = []
            scroll_count = 0
            last_product_count = 0
            
            while scroll_count < max_scrolls:
                # 獲取當前商品
                current_products = self.extract_all_products()
                
                if isinstance(current_products, list):
                    all_products = current_products
                    current_count = len(current_products)
                    
                    # 如果沒有新商品加載，停止滾動
                    if current_count <= last_product_count and scroll_count > 0:
                        break
                    
                    last_product_count = current_count
                
                # 滾動到頁面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.9);")
                
                # 等待內容載入
                time.sleep(3)
                scroll_count += 1
            
            return all_products
        except Exception as e:
            return {"error": str(e)}
            
    def process_with_optimal_strategy(self):
        """使用最佳策略處理頁面商品（分頁或滾動）"""
        try:
            # 先檢查分頁
            pagination = self.find_pagination()
            has_pagination = pagination.get("found", False)
            
            if has_pagination and pagination.get("totalPages", 1) > 1:
                # 使用分頁策略
                return {"strategy": "pagination", "results": self.process_all_pages()}
            
            # 檢查無限滾動
            scroll_info = self.check_infinite_scroll()
            may_use_infinite_scroll = scroll_info.get("mayUseInfiniteScroll", False)
            
            if may_use_infinite_scroll:
                # 使用滾動策略
                products = self.load_more_with_scroll()
                if isinstance(products, list):
                    results = []
                    
                    for product in products:
                        product_result = {
                            "name": product.get("name", f"商品 #{product['index']+1}"),
                            "specs": []
                        }
                        
                        for spec in product.get("specs", []):
                            spec_result = {
                                "name": spec.get("name", f"規格 #{spec['index']+1}"),
                                "stock": spec.get("stock", "未知"),
                                "price": spec.get("price", "未知"),
                                "action": "無需操作"
                            }
                            
                            # 檢查是否需要啟用
                            if spec.get("hasSwitch"):
                                stock_number = spec.get("stockNumber", 0)
                                is_open = spec.get("isOpen", False)
                                is_disabled = spec.get("isDisabled", False)
                                
                                if stock_number > 0 and not is_disabled and not is_open:
                                    # 需要啟用
                                    switch_path = spec.get("switchPath")
                                    if switch_path:
                                        toggle_result = self.toggle_product_switch(switch_path)
                                        spec_result["action"] = "已啟用" if toggle_result.get("success") else f"啟用失敗: {toggle_result.get('error')}"
                                    else:
                                        spec_result["action"] = "無法啟用：找不到開關路徑"
                            
                            product_result["specs"].append(spec_result)
                        
                        results.append(product_result)
                    
                    return {"strategy": "infinite_scroll", "results": results}
            
            # 如果上述策略都不適用，使用單頁處理
            return {"strategy": "single_page", "results": self.process_all_products()}
            
        except Exception as e:
            return {"strategy": "error", "error": str(e)}

    def analyze_page_structure(self):
        """分析當前頁面結構"""
        try:
            # 創建分析器
            analyzer = ShopeePageAnalyzer(self.driver)
            
            # 分析頁面URL
            self.log_status(f"當前URL: {self.driver.current_url}")
            
            # 尋找商品元素
            self.log_status("\n1. 嘗試尋找商品元素...")
            product_elements = analyzer.find_product_elements()
            
            if isinstance(product_elements, dict) and "error" in product_elements:
                self.log_status(f"  錯誤: {product_elements['error']}")
            elif isinstance(product_elements, dict) and "count" in product_elements:
                self.log_status(f"  找到 {product_elements['count']} 個商品，使用選擇器: {product_elements.get('selector', '未知')}")
                self.log_status(f"  範例元素: {json.dumps(product_elements.get('sample', {}), ensure_ascii=False, indent=2)}")
            else:
                self.log_status(f"  找到可能的商品元素: {len(product_elements) if isinstance(product_elements, list) else 0} 個")
            
            # 檢查頁面導航方式
            self.log_status("\n2. 檢查頁面導航方式...")
            
            # 檢查分頁
            pagination = analyzer.find_pagination()
            if pagination.get("found", False):
                self.log_status(f"  檢測到分頁控制，當前第 {pagination.get('currentPage', '1')} 頁，共 {pagination.get('totalPages', '1')} 頁")
                has_next = pagination.get("hasNextPage", False)
                self.log_status(f"  是否有下一頁: {'是' if has_next else '否'}")
            else:
                self.log_status("  未檢測到標準分頁控制")
            
            # 檢查無限滾動
            scroll_info = analyzer.check_infinite_scroll()
            if scroll_info.get("mayUseInfiniteScroll", False):
                self.log_status("  檢測到頁面可能使用無限滾動加載")
                if scroll_info.get("heightChanged", False):
                    before = scroll_info.get("initialHeight", 0)
                    after = scroll_info.get("newHeight", 0)
                    self.log_status(f"  滾動前頁面高度: {before}，滾動後: {after}，增加: {after - before}")
                
                if scroll_info.get("hasLazyLoadIndicators", False):
                    self.log_status("  檢測到懶加載指示器元素")
            else:
                self.log_status("  未檢測到無限滾動特徵")
            
            # 提取商品詳細信息
            self.log_status("\n3. 提取商品詳細信息...")
            products = analyzer.extract_all_products()
            
            if isinstance(products, dict) and "error" in products:
                self.log_status(f"  錯誤: {products['error']}")
            elif isinstance(products, list):
                self.log_status(f"  成功提取 {len(products)} 個商品")
                
                # 顯示前3個商品的摘要
                for i, product in enumerate(products[:3]):
                    self.log_status(f"\n  商品 #{i+1}: {product.get('name', '未知名稱')}")
                    self.log_status(f"  規格數量: {len(product.get('specs', []))}")
                    
                    # 顯示第一個規格的詳細信息
                    if product.get('specs') and len(product.get('specs')) > 0:
                        spec = product['specs'][0]
                        self.log_status(f"  首個規格: {spec.get('name', '未知規格')}")
                        self.log_status(f"  庫存: {spec.get('stock', '未知')}")
                        self.log_status(f"  價格: {spec.get('price', '未知')}")
                        self.log_status(f"  開關狀態: {'開啟' if spec.get('isOpen') else '關閉'}{' (已禁用)' if spec.get('isDisabled') else ''}")
            
            # 分析頁面結構
            self.log_status("\n4. 分析頁面DOM結構...")
            structure = analyzer.get_page_structure()
            
            if isinstance(structure, dict) and "error" in structure:
                self.log_status(f"  錯誤: {structure['error']}")
            else:
                self.log_status(f"  成功提取頁面結構，包含 {len(structure)} 個主要元素")
                
                # 顯示頁面中重要的HTML結構
                self.log_status("\n5. 頁面中的重要元素:")
                
                # 使用JavaScript查找頁面中的關鍵元素
                important_elements = self.driver.execute_script("""
                    let result = {
                        buttons: [],
                        forms: [],
                        tables: [],
                        productContainers: []
                    };
                    
                    // 找出所有按鈕
                    document.querySelectorAll('button').forEach(btn => {
                        if (btn.innerText) {
                            result.buttons.push({
                                text: btn.innerText.slice(0, 30),
                                className: btn.className,
                                disabled: btn.disabled
                            });
                        }
                    });
                    
                    // 找出所有表單
                    document.querySelectorAll('form').forEach(form => {
                        result.forms.push({
                            id: form.id,
                            action: form.action,
                            method: form.method,
                            elements: form.elements.length
                        });
                    });
                    
                    // 找出所有表格
                    document.querySelectorAll('table').forEach(table => {
                        result.tables.push({
                            rows: table.rows.length,
                            className: table.className
                        });
                    });
                    
                    // 找出可能的商品容器
                    document.querySelectorAll('div').forEach(div => {
                        if (div.innerText.includes('商品') || 
                            div.innerText.includes('庫存') || 
                            div.innerText.includes('價格')) {
                            if (result.productContainers.length < 5) {
                                result.productContainers.push({
                                    className: div.className,
                                    textPreview: div.innerText.slice(0, 50),
                                    childNodes: div.childNodes.length
                                });
                            }
                        }
                    });
                    
                    return result;
                """)
                
                # 顯示按鈕
                self.log_status(f"  找到 {len(important_elements.get('buttons', []))} 個按鈕")
                for i, btn in enumerate(important_elements.get('buttons', [])[:5]):
                    self.log_status(f"    按鈕 #{i+1}: {btn.get('text')} | 狀態: {'禁用' if btn.get('disabled') else '啟用'}")
                
                # 顯示表單
                self.log_status(f"  找到 {len(important_elements.get('forms', []))} 個表單")
                
                # 顯示可能的商品容器
                self.log_status(f"  找到 {len(important_elements.get('productContainers', []))} 個可能的商品容器")
                for i, container in enumerate(important_elements.get('productContainers', [])):
                    self.log_status(f"    容器 #{i+1}: {container.get('textPreview')}...")
            
            # 顯示推薦處理策略
            self.log_status("\n6. 推薦處理策略:")
            if pagination.get("found", False) and pagination.get("totalPages", 1) > 1:
                self.log_status("  推薦使用分頁策略，逐頁處理商品")
            elif scroll_info.get("mayUseInfiniteScroll", False):
                self.log_status("  推薦使用無限滾動策略，邊滾動邊收集商品")
            else:
                self.log_status("  推薦使用單頁處理策略")
                
            self.log_status("\n===== 頁面分析完成 =====")
            
        except Exception as e:
            self.log_status(f"分析頁面結構時發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"分析頁面結構時發生錯誤: {str(e)}")

    def find_products_by_xpath(self):
        """使用特定的XPath選擇器尋找商品名稱和規格"""
        try:
            # 更靈活的XPath模式 - 商品名稱
            product_xpaths = [
                "//div[contains(@class, 'discount-edit-item')]//div[contains(@class, 'ellipsis-content')]",  # 基於類名的XPath
                "/html/body/div[1]/div[2]/div/div/div/div/div[2]/form[2]/div/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div",  # 原始XPath
                "//div[contains(@class, 'product-name')]",  # 常見的商品名稱類
                "//div[contains(@class, 'discount-edit-item')]",  # 整個商品容器
                "//div[contains(@class, 'item')]/div[contains(@class, 'name')]",  # 組合類名
                "//div[contains(@class, 'discount')]//div[contains(@class, 'name')]",  # 折扣項目中的名稱
                "//h3[contains(@class, 'product-title')]",  # 標題元素
                "//div[contains(text(), '商品名稱')]/following-sibling::div",  # 基於文本的XPath
                "//div[contains(@class, 'product-item')]"  # 另一個常見的商品容器類
            ]
            
            # 更靈活的XPath模式 - 規格
            spec_xpaths = [
                "//div[contains(@class, 'discount-edit-item-model-component')]",  # 基於類名的XPath
                "/html/body/div[1]/div[2]/div/div/div/div/div[2]/form[2]/div/div[2]/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/div",  # 原始XPath
                "//div[contains(@class, 'variant')]",  # 變體/規格通用類
                "//div[contains(@class, 'spec')]",  # 規格通用類
                "//div[contains(@class, 'model')]",  # 型號/規格類
                "//div[contains(@class, 'item-model')]",  # 商品型號類
                "//div[contains(@class, 'option')]",  # 選項類
                "//div[contains(@class, 'discount-edit-item')]/following-sibling::div",  # 折扣項目的下一個元素
                "//div[contains(@class, 'product-variant')]"  # 產品變體類
            ]
            
            # 使用JavaScript查找所有可能的商品和規格，特別是像【Fee現貨X色】開頭的商品
            js_result = self.driver.execute_script("""
                // 尋找所有可能的商品和規格
                function findAllProductsAndSpecs() {
                    const results = {
                        products: [],
                        specs: []
                    };
                    
                    // 定義一個函數來檢查是否是商品標題
                    function isProductTitle(text) {
                        // 檢查是否以【Fee開頭
                        if (text && (text.includes('【Fee') || text.includes('【'))) {
                            return true;
                        }
                        return false;
                    }
                    
                    // 方法1: 查找標題文本
                    const allElements = document.querySelectorAll('div');
                    const productElements = [];
                    
                    // 先找到所有可能的商品標題
                    allElements.forEach(element => {
                        const text = element.innerText || '';
                        if (isProductTitle(text)) {
                            productElements.push({
                                element: element,
                                text: text,
                                isDirectMatch: true
                            });
                        }
                    });
                    
                    // 如果找到直接匹配的商品，使用它們
                    if (productElements.length > 0) {
                        // 排序，確保直接匹配的在前面
                        productElements.sort((a, b) => {
                            if (a.isDirectMatch && !b.isDirectMatch) return -1;
                            if (!a.isDirectMatch && b.isDirectMatch) return 1;
                            return 0;
                        });
                        
                        // 處理每個商品
                        productElements.forEach((productInfo, index) => {
                            const element = productInfo.element;
                            
                            // 查找包含此商品的容器
                            let productContainer = element;
                            // 向上查找4層，尋找更大的容器
                            for (let i = 0; i < 4 && productContainer.parentElement; i++) {
                                productContainer = productContainer.parentElement;
                                // 如果找到discount-edit-item類，就停止
                                if (productContainer.classList.contains('discount-edit-item')) {
                                    break;
                                }
                            }
                            
                            // 提取商品信息
                            const product = {
                                index: index,
                                element: productContainer,
                                name: productInfo.text,
                                specs: []
                            };
                            
                            // 從商品容器中查找規格，先嘗試找含discount-edit-item-model-component類的元素
                            const specContainers = productContainer.querySelectorAll('.discount-edit-item-model-component');
                            
                            if (specContainers.length > 0) {
                                specContainers.forEach((spec, specIndex) => {
                                    // 提取規格信息
                                    let specName = '';
                                    let specStock = '';
                                    let specPrice = '';
                                    let switchStatus = null;
                                    
                                    // 查找規格名稱
                                    const nameElement = spec.querySelector('.ellipsis-content');
                                    if (nameElement) {
                                        specName = nameElement.innerText;
                                    }
                                    
                                    // 查找庫存
                                    const stockElement = spec.querySelector('.item-stock');
                                    if (stockElement) {
                                        specStock = stockElement.innerText;
                                    }
                                    
                                    // 查找價格
                                    const priceElement = spec.querySelector('.item-price');
                                    if (priceElement) {
                                        specPrice = priceElement.innerText;
                                    }
                                    
                                    // 查找開關
                                    const switchElement = spec.querySelector('.eds-switch');
                                    if (switchElement) {
                                        switchStatus = {
                                            isOpen: switchElement.classList.contains('eds-switch--open'),
                                            isDisabled: switchElement.classList.contains('eds-switch--disabled')
                                        };
                                    }
                                    
                                    // 建立規格對象
                                    const specInfo = {
                                        index: specIndex,
                                        element: spec,
                                        name: specName || `規格 #${specIndex+1}`,
                                        stock: specStock,
                                        price: specPrice,
                                        isOpen: switchStatus ? switchStatus.isOpen : false,
                                        isDisabled: switchStatus ? switchStatus.isDisabled : false
                                    };
                                    
                                    product.specs.push(specInfo);
                                    results.specs.push(specInfo);
                                });
                            } else {
                                // 如果沒有找到明確的規格容器，嘗試其他方法
                                // 查找包含stock或price類的元素
                                const stockElements = productContainer.querySelectorAll('.item-stock, [data-stock], .stock');
                                const priceElements = productContainer.querySelectorAll('.item-price, [data-price], .price');
                                const switchElements = productContainer.querySelectorAll('.eds-switch, [role="switch"]');
                                
                                if (stockElements.length > 0 || priceElements.length > 0 || switchElements.length > 0) {
                                    // 查找可能的規格名稱容器
                                    let specNameElements = productContainer.querySelectorAll('.ellipsis-content:not(:first-child)');
                                    
                                    if (specNameElements.length === 0) {
                                        // 如果沒有找到，可能規格名稱在其他元素中
                                        specNameElements = productContainer.querySelectorAll('div:not(.item-stock):not(.item-price)');
                                    }
                                    
                                    // 如果找到的規格名稱元素和庫存/價格元素數量相似，可能是成對的
                                    if (specNameElements.length > 0 && 
                                        (specNameElements.length === stockElements.length || 
                                         specNameElements.length === priceElements.length)) {
                                        
                                        for (let i = 0; i < specNameElements.length; i++) {
                                            const specInfo = {
                                                index: i,
                                                element: null,
                                                name: specNameElements[i] ? specNameElements[i].innerText : `規格 #${i+1}`,
                                                stock: stockElements[i] ? stockElements[i].innerText : '',
                                                price: priceElements[i] ? priceElements[i].innerText : '',
                                                isOpen: false,
                                                isDisabled: false
                                            };
                                            
                                            // 如果有對應的開關
                                            if (switchElements.length > i) {
                                                specInfo.isOpen = switchElements[i].classList.contains('eds-switch--open');
                                                specInfo.isDisabled = switchElements[i].classList.contains('eds-switch--disabled');
                                            }
                                            
                                            product.specs.push(specInfo);
                                            results.specs.push(specInfo);
                                        }
                                    }
                                }
                            }
                            
                            results.products.push(product);
                        });
                        
                        return results;
                    }
                    
                    // 方法2: 如果沒有找到【Fee開頭的商品，使用更通用的方法
                    // 查找可能的商品容器
                    const productContainers = [];
                    
                    // 查找含商品相關文字的容器
                    document.querySelectorAll('div').forEach(div => {
                        const text = div.innerText || '';
                        if (text.includes('商品名稱') || text.includes('Product') || 
                            (text.includes('商品') && text.length < 100)) {
                            // 使用容器或者其上層節點
                            let container = div;
                            // 向上查找較大的容器
                            for (let i = 0; i < 3; i++) {
                                if (container.parentElement) {
                                    container = container.parentElement;
                                }
                            }
                            productContainers.push(container);
                        }
                    });
                    
                    // 查找包含多個子元素的容器
                    document.querySelectorAll('div.discount-edit-item, div.product-item, div.item, div[data-product-id]').forEach(div => {
                        productContainers.push(div);
                    });
                    
                    // 查找包含庫存、開關等元素的容器
                    document.querySelectorAll('div').forEach(div => {
                        if ((div.querySelector('.eds-switch') || div.querySelector('[role="switch"]')) && 
                            (div.querySelector('.item-stock') || div.querySelector('.stock') || 
                             div.innerText.includes('庫存'))) {
                            let container = div;
                            // 向上查找較大的容器
                            for (let i = 0; i < 2; i++) {
                                if (container.parentElement) {
                                    container = container.parentElement;
                                }
                            }
                            if (!productContainers.includes(container)) {
                                productContainers.push(container);
                            }
                        }
                    });
                    
                    // 去重並提取商品信息
                    const uniqueContainers = [...new Set(productContainers)];
                    
                    uniqueContainers.forEach((container, index) => {
                        // 提取商品名稱
                        let productName = '';
                        const nameElement = container.querySelector('.ellipsis-content, .name, .title, h3, [data-name]');
                        if (nameElement) {
                            productName = nameElement.innerText;
                        } else {
                            // 如果找不到明確的名稱元素，使用容器的前幾個詞
                            const text = container.innerText.split('\\n')[0];
                            productName = text ? text.trim().substring(0, 50) : `商品 #${index+1}`;
                        }
                        
                        // 尋找規格元素
                        const specContainers = container.querySelectorAll('.discount-edit-item-model-component, .variant, .model, .spec, .option');
                        
                        const productInfo = {
                            index: index,
                            element: container,
                            name: productName,
                            specs: []
                        };
                        
                        // 如果找到規格元素
                        if (specContainers.length > 0) {
                            specContainers.forEach((spec, specIndex) => {
                                // 提取規格信息
                                const specNameElement = spec.querySelector('.ellipsis-content, .name, .title');
                                const specStockElement = spec.querySelector('.item-stock, .stock, [data-stock]');
                                const specPriceElement = spec.querySelector('.item-price, .price, [data-price]');
                                const specSwitchElement = spec.querySelector('.eds-switch, [role="switch"]');
                                
                                const specInfo = {
                                    index: specIndex,
                                    element: spec,
                                    name: specNameElement ? specNameElement.innerText : `規格 #${specIndex+1}`,
                                    stock: specStockElement ? specStockElement.innerText : '',
                                    price: specPriceElement ? specPriceElement.innerText : '',
                                    hasSwitch: !!specSwitchElement,
                                    isOpen: specSwitchElement ? specSwitchElement.classList.contains('eds-switch--open') : false,
                                    isDisabled: specSwitchElement ? specSwitchElement.classList.contains('eds-switch--disabled') : false
                                };
                                
                                productInfo.specs.push(specInfo);
                                results.specs.push(specInfo);
                            });
                        }
                        
                        results.products.push(productInfo);
                    });
                    
                    return results;
                }
                
                return findAllProductsAndSpecs();
            """)
            
            # 尋找商品元素 - 使用XPath
            product_elements = []
            for xpath in product_xpaths:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements and len(elements) > 0:
                    product_elements = elements
                    break
            
            # 尋找規格元素 - 使用XPath
            spec_elements = []
            for xpath in spec_xpaths:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements and len(elements) > 0:
                    spec_elements = elements
                    break
            
            # 合併JavaScript結果與Selenium結果
            all_products = []
            all_specs = []
            
            # 處理JavaScript查找的元素 - 優先使用
            if js_result and isinstance(js_result, dict) and "products" in js_result:
                for jp in js_result["products"]:
                    # 優先選擇明確開頭為【Fee的商品名稱
                    if "name" in jp and isinstance(jp["name"], str) and ("【Fee" in jp["name"] or jp["name"].startswith("【")):
                        product_info = {
                            "index": jp.get("index", 0),
                            "name": jp.get("name", f"商品 #{jp.get('index', 0)+1}"),
                            "js_found": True,
                            "specs": []
                        }
                        
                        # 處理規格
                        if "specs" in jp and jp["specs"]:
                            for js_spec in jp["specs"]:
                                spec_info = {
                                    "index": js_spec.get("index", 0),
                                    "name": js_spec.get("name", f"規格 #{js_spec.get('index', 0)+1}"),
                                    "stock": js_spec.get("stock", ""),
                                    "price": js_spec.get("price", ""),
                                    "status": "開啟" if js_spec.get("isOpen", False) else "關閉",
                                    "disabled": js_spec.get("isDisabled", False),
                                    "js_found": True
                                }
                                product_info["specs"].append(spec_info)
                        
                        all_products.append(product_info)
            
            # 如果JavaScript沒有找到或找到的不夠，再處理Selenium的結果
            if len(all_products) < 5:  # 如果JS找到的不夠
                # 處理Selenium查找的元素
                for i, product_element in enumerate(product_elements):
                    product_text = product_element.text
                    
                    # 尋找已經存在於all_products中的商品
                    product_exists = False
                    for p in all_products:
                        if p["name"] == product_text:
                            product_exists = True
                            break
                    
                    if not product_exists:
                        product_info = {
                            "index": i,
                            "name": product_text,
                            "selenium_found": True,
                            "specs": []
                        }
                        
                        # 如果商品名稱為空，嘗試其他方法提取
                        if not product_info["name"]:
                            try:
                                name_element = product_element.find_element(By.XPATH, ".//div[contains(@class, 'ellipsis-content')]")
                                product_info["name"] = name_element.text
                            except:
                                product_info["name"] = f"商品 #{i+1}"
                        
                        all_products.append(product_info)
            
            # 處理規格 - 將規格分配給適當的商品
            # 首先，收集來自JavaScript的所有規格
            js_specs = []
            if js_result and isinstance(js_result, dict) and "specs" in js_result:
                js_specs = js_result["specs"]
            
            # 然後，處理Selenium查找的規格
            selenium_specs = []
            for i, spec_element in enumerate(spec_elements):
                spec_info = {
                    "index": i,
                    "element": spec_element,
                    "name": spec_element.text.split("\n")[0] if spec_element.text else f"規格 #{i+1}",
                    "selenium_found": True
                }
                
                # 嘗試查找規格名稱、價格和庫存
                try:
                    # 查找規格名稱
                    name_element = spec_element.find_element(By.XPATH, ".//div[contains(@class, 'ellipsis-content')]")
                    if name_element and name_element.text:
                        spec_info["name"] = name_element.text
                    
                    # 查找庫存
                    stock_element = spec_element.find_element(By.XPATH, ".//div[contains(@class, 'item-stock')]")
                    if stock_element:
                        spec_info["stock"] = stock_element.text
                    
                    # 查找價格
                    price_element = spec_element.find_element(By.XPATH, ".//div[contains(@class, 'item-price')]")
                    if price_element:
                        spec_info["price"] = price_element.text
                    
                    # 查找開關狀態
                    switch_element = spec_element.find_element(By.XPATH, ".//div[contains(@class, 'eds-switch')]")
                    if switch_element:
                        is_open = "eds-switch--open" in switch_element.get_attribute("class")
                        is_disabled = "eds-switch--disabled" in switch_element.get_attribute("class")
                        spec_info["status"] = "開啟" if is_open else "關閉"
                        spec_info["disabled"] = is_disabled
                except Exception as e:
                    spec_info["error"] = str(e)
                
                selenium_specs.append(spec_info)
            
            # 返回結果
            return {
                "product_count": len(all_products),
                "spec_count": len(all_specs),
                "selenium_product_count": len(product_elements),
                "selenium_spec_count": len(spec_elements),
                "js_product_count": len(js_result.get("products", [])) if js_result and isinstance(js_result, dict) else 0,
                "js_spec_count": len(js_result.get("specs", [])) if js_result and isinstance(js_result, dict) else 0,
                "products": all_products
            }
        except Exception as e:
            return {"error": str(e), "product_count": 0, "spec_count": 0, "products": []}
    
    def process_with_xpath_strategy(self):
        """使用XPath選擇器策略處理頁面上的商品"""
        try:
            # 獲取商品信息
            products_info = self.find_products_by_xpath()
            
            if "error" in products_info and products_info["product_count"] == 0:
                return {"strategy": "error", "error": products_info["error"]}
            
            # 處理找到的商品
            product_results = []
            
            for product in products_info.get("products", []):
                product_result = {
                    "name": product.get("name", "未知商品"),
                    "specs": []
                }
                
                # 處理規格
                for spec in product.get("specs", []):
                    spec_name = spec.get("name", "未知規格")
                    stock = spec.get("stock", "0")
                    price = spec.get("price", "0")
                    status = spec.get("status", "未知")
                    disabled = spec.get("disabled", False)
                    
                    # 嘗試提取庫存數字
                    try:
                        stock_number = int(''.join(filter(str.isdigit, stock)))
                    except:
                        stock_number = 0
                    
                    # 確定操作動作
                    action = "無需操作"
                    if stock_number > 0 and not disabled:
                        if status != "開啟":
                            action = "需要開啟"
                    
                    # 添加規格結果
                    product_result["specs"].append({
                        "name": spec_name,
                        "stock": stock,
                        "price": price,
                        "status": status,
                        "disabled": disabled,
                        "action": action
                    })
                
                product_results.append(product_result)
            
            return {
                "strategy": "xpath",
                "results": product_results
            }
        except Exception as e:
            return {"strategy": "error", "error": str(e)}

    def find_fee_products(self):
        """尋找Fee開頭的商品及其規格"""
        try:
            results = {
                "product_count": 0,
                "spec_count": 0,
                "products": []
            }
            
            # 使用JavaScript尋找商品元素
            js_products = self.driver.execute_script("""
                function findFeeProducts() {
                    // 尋找所有商品容器 - 這些是蝦皮規格容器的典型結構
                    const productContainers = document.querySelectorAll('div.discount-item-component');
                    
                    // 用於存放結果
                    const products = [];
                    let processedNames = new Set(); // 用於避免重複
                    
                    for (let container of productContainers) {
                        try {
                            // 尋找商品名稱
                            const nameElement = container.querySelector('div.ellipsis-content.single');
                            if (!nameElement) continue;
                            
                            const productName = nameElement.innerText.trim();
                            
                            // 檢查是否是Fee商品，或是否處理過
                            if (!productName.startsWith('Fee') && !productName.includes('Fee')) continue;
                            if (processedNames.has(productName)) continue;
                            
                            processedNames.add(productName);
                            
                            // 尋找規格列表
                            const specsContainer = container.querySelector('div.discount-view-item-model-list');
                            if (!specsContainer) continue;
                            
                            const specElements = specsContainer.querySelectorAll('div.discount-view-item-model-component');
                            
                            const specs = [];
                            
                            for (let specElement of specElements) {
                                try {
                                    // 尋找規格名稱
                                    const specNameEl = specElement.querySelector('div.ellipsis-content.single');
                                    if (!specNameEl) continue;
                                    
                                    const specName = specNameEl.innerText.trim();
                                    
                                    // 尋找庫存
                                    const stockEl = specElement.querySelector('div.item-content.item-stock');
                                    const stock = stockEl ? stockEl.innerText.trim() : "0";
                                    
                                    // 尋找價格
                                    const priceEl = specElement.querySelector('div.item-content.item-discounted-price');
                                    const price = priceEl ? priceEl.innerText.trim() : "";
                                    
                                    // 檢查開關狀態 - 在編輯模式中，會有eds-switch元素
                                    const switchEls = document.querySelectorAll(`div.eds-switch`);
                                    let status = "未知";
                                    let isDisabled = false;
                                    
                                    // 找到對應規格的開關
                                    for (let switchEl of switchEls) {
                                        const switchContainingDiv = switchEl.closest('div.discount-edit-item-model-component');
                                        if (switchContainingDiv) {
                                            const nameInSwitch = switchContainingDiv.querySelector('div.ellipsis-content.single');
                                            if (nameInSwitch && nameInSwitch.innerText.trim() === specName) {
                                                status = switchEl.classList.contains('eds-switch--open') ? "開啟" : "關閉";
                                                isDisabled = switchEl.classList.contains('eds-switch--disabled');
                                                break;
                                            }
                                        }
                                    }
                                    
                                    specs.push({
                                        name: specName,
                                        stock: stock,
                                        price: price,
                                        status: status,
                                        disabled: isDisabled
                                    });
                                } catch (e) {
                                    console.error("處理規格時發生錯誤:", e);
                                }
                            }
                            
                            if (specs.length > 0) {
                                products.push({
                                    name: productName,
                                    specs: specs
                                });
                            }
                        } catch (e) {
                            console.error("處理商品時發生錯誤:", e);
                        }
                    }
                    
                    return {
                        products: products,
                        productCount: products.length,
                        specCount: products.reduce((total, product) => total + product.specs.length, 0)
                    };
                }
                
                return findFeeProducts();
            """)
            
            if js_products and "products" in js_products:
                products = js_products["products"]
                spec_count = js_products.get("specCount", 0)
                
                results["products"] = products
                results["product_count"] = len(products)
                results["spec_count"] = spec_count
                
                # 如果找不到產品或規格，嘗試使用更通用的方法
                if len(products) == 0 or spec_count == 0:
                    # 回退到其他尋找方法
                    return self._find_products_fallback()
                    
                return results
            else:
                return self._find_products_fallback()
                
        except Exception as e:
            return {"error": str(e), "product_count": 0, "spec_count": 0, "products": []}
    
    def _find_products_fallback(self):
        """尋找商品的備用方法"""
        try:
            # 通用的JavaScript方法尋找商品
            js_products = self.driver.execute_script("""
                function findAllProducts() {
                    // 嘗試各種可能的商品容器選擇器
                    const selectors = [
                        'div.discount-item-component',
                        'div.discount-edit-item',
                        'div.item-component',
                        'div[class*="item"][class*="component"]'
                    ];
                    
                    let productElements = [];
                    
                    // 嘗試每個選擇器
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            productElements = Array.from(elements);
                            console.log(`找到 ${elements.length} 個商品，使用選擇器: ${selector}`);
                            break;
                        }
                    }
                    
                    // 如果還是找不到，嘗試更廣泛的搜索
                    if (productElements.length === 0) {
                        // 尋找可能包含商品名稱的元素
                        const possibleNameElements = document.querySelectorAll('div.ellipsis-content.single');
                        for (const nameEl of possibleNameElements) {
                            const parent = findParentWithClass(nameEl, 'component');
                            if (parent && !productElements.includes(parent)) {
                                productElements.push(parent);
                            }
                        }
                    }
                    
                    // 如果還是找不到，最後的嘗試
                    if (productElements.length === 0) {
                        const allDivs = document.querySelectorAll('div');
                        for (const div of allDivs) {
                            if (div.innerText.includes('Fee') && div.childElementCount > 0) {
                                productElements.push(div);
                            }
                        }
                    }
                    
                    // 用於存放結果
                    const products = [];
                    let processedNames = new Set(); // 用於避免重複
                    
                    // 處理每個找到的商品元素
                    for (let container of productElements) {
                        try {
                            // 尋找商品名稱
                            let nameElement = container.querySelector('div.ellipsis-content.single') || 
                                              container.querySelector('div[class*="product-name"]') ||
                                              container.querySelector('div[class*="name"]');
                            
                            if (!nameElement) {
                                // 嘗試尋找任何含有文字的元素
                                const textElements = Array.from(container.querySelectorAll('div')).filter(el => el.innerText.trim().length > 0);
                                if (textElements.length > 0) {
                                    nameElement = textElements[0];
                                }
                            }
                            
                            if (!nameElement) continue;
                            
                            const productName = nameElement.innerText.trim();
                            
                            // 檢查是否處理過
                            if (processedNames.has(productName)) continue;
                            processedNames.add(productName);
                            
                            // 尋找規格容器
                            let specsContainer = container.querySelector('div.discount-view-item-model-list') || 
                                                container.querySelector('div.discount-edit-item-model-list') ||
                                                container.querySelector('div[class*="model-list"]');
                            
                            // 如果找不到，嘗試在子元素中找
                            if (!specsContainer) {
                                const childDivs = container.querySelectorAll('div > div');
                                for (const div of childDivs) {
                                    if (div.childElementCount > 2) { // 假設規格容器有多個子元素
                                        specsContainer = div;
                                        break;
                                    }
                                }
                            }
                            
                            const specs = [];
                            
                            if (specsContainer) {
                                // 嘗試找到規格元素
                                let specElements = specsContainer.querySelectorAll('div.discount-view-item-model-component') ||
                                                  specsContainer.querySelectorAll('div.discount-edit-item-model-component') ||
                                                  specsContainer.querySelectorAll('div[class*="model-component"]');
                                
                                if (!specElements || specElements.length === 0) {
                                    // 嘗試找到包含內容的子元素
                                    specElements = Array.from(specsContainer.children).filter(el => el.innerText.trim().length > 0);
                                }
                                
                                for (let specElement of specElements) {
                                    try {
                                        // 尋找規格名稱
                                        let specNameEl = specElement.querySelector('div.ellipsis-content.single') ||
                                                        specElement.querySelector('div[class*="variation"]') ||
                                                        specElement.querySelector('div:first-child');
                                        
                                        if (!specNameEl) continue;
                                        
                                        const specName = specNameEl.innerText.trim();
                                        
                                        // 尋找庫存
                                        let stockEl = specElement.querySelector('div.item-content.item-stock') ||
                                                     specElement.querySelector('div[class*="stock"]');
                                        
                                        const stock = stockEl ? stockEl.innerText.trim() : "0";
                                        
                                        // 尋找價格
                                        let priceEl = specElement.querySelector('div.item-content.item-discounted-price') ||
                                                     specElement.querySelector('div.item-content.item-price') ||
                                                     specElement.querySelector('div[class*="price"]');
                                        
                                        const price = priceEl ? priceEl.innerText.trim() : "";
                                        
                                        // 檢查開關狀態
                                        let switchEl = specElement.querySelector('div.eds-switch');
                                        let status = "未知";
                                        let isDisabled = false;
                                        
                                        if (switchEl) {
                                            status = switchEl.classList.contains('eds-switch--open') ? "開啟" : "關閉";
                                            isDisabled = switchEl.classList.contains('eds-switch--disabled');
                                        }
                                        
                                        specs.push({
                                            name: specName,
                                            stock: stock,
                                            price: price,
                                            status: status,
                                            disabled: isDisabled
                                        });
                                    } catch (e) {
                                        console.error("處理規格時發生錯誤:", e);
                                    }
                                }
                            }
                            
                            products.push({
                                name: productName,
                                specs: specs
                            });
                        } catch (e) {
                            console.error("處理商品時發生錯誤:", e);
                        }
                    }
                    
                    return {
                        products: products,
                        productCount: products.length,
                        specCount: products.reduce((total, product) => total + product.specs.length, 0)
                    };
                }
                
                // 尋找具有特定class的父元素
                function findParentWithClass(element, className) {
                    let current = element;
                    while (current) {
                        if (current.className && current.className.includes(className)) {
                            return current;
                        }
                        current = current.parentElement;
                    }
                    return null;
                }
                
                return findAllProducts();
            """)
            
            results = {
                "product_count": 0,
                "spec_count": 0,
                "products": []
            }
            
            if js_products and "products" in js_products:
                products = js_products["products"]
                spec_count = js_products.get("specCount", 0)
                
                # 過濾只選擇Fee開頭的商品
                fee_products = [p for p in products if p.get("name", "").startswith("Fee") or "Fee" in p.get("name", "")]
                
                results["products"] = fee_products if fee_products else products
                results["product_count"] = len(results["products"])
                
                # 計算規格總數
                total_specs = 0
                for product in results["products"]:
                    total_specs += len(product.get("specs", []))
                
                results["spec_count"] = total_specs
                
                return results
            else:
                return {"error": "找不到商品", "product_count": 0, "spec_count": 0, "products": []}
                
        except Exception as e:
            return {"error": str(e), "product_count": 0, "spec_count": 0, "products": []}

def create_mock_data():
    """創建模擬數據用於測試"""
    return [
        {
            "name": "測試商品 1",
            "index": 0,
            "specs": [
                {
                    "name": "規格 1-1",
                    "index": 0,
                    "stock": "10",
                    "stockNumber": 10,
                    "price": "$199",
                    "hasSwitch": True,
                    "isOpen": False,
                    "isDisabled": False,
                    "switchPath": "div.test > button.switch"
                },
                {
                    "name": "規格 1-2",
                    "index": 1,
                    "stock": "0",
                    "stockNumber": 0,
                    "price": "$299",
                    "hasSwitch": True,
                    "isOpen": False,
                    "isDisabled": True,
                    "switchPath": "div.test > button.switch"
                }
            ]
        },
        {
            "name": "測試商品 2",
            "index": 1,
            "specs": [
                {
                    "name": "規格 2-1",
                    "index": 0,
                    "stock": "5",
                    "stockNumber": 5,
                    "price": "$399",
                    "hasSwitch": True,
                    "isOpen": True,
                    "isDisabled": False,
                    "switchPath": "div.test > button.switch"
                }
            ]
        }
    ]

class MockDriver:
    """模擬Selenium WebDriver用於測試"""
    def __init__(self):
        self.current_url = "https://example.com/test"
        
    def execute_script(self, script, *args):
        """模擬JavaScript執行"""
        if "extractProductDetails" in script:
            return create_mock_data()
        elif "getElementInfo" in script:
            return [{"tagName": "DIV", "className": "test-class", "children": []}]
        elif "findPossibleProductElements" in script:
            return [{"element": None, "reason": "測試", "text": "測試商品"}]
        elif "buttons" in script:
            return {
                "buttons": [
                    {"text": "測試按鈕", "disabled": False},
                    {"text": "禁用按鈕", "disabled": True}
                ],
                "forms": [],
                "tables": [],
                "productContainers": [
                    {"className": "test-container", "textPreview": "測試商品容器", "childNodes": 5}
                ]
            }
        else:
            return {"success": True, "newState": "開啟"}
        
    def find_elements(self, by, selector):
        """模擬元素查找"""
        return []

class TestPageAnalyzer:
    """用於測試頁面分析器功能"""
    @staticmethod
    def run_tests():
        """執行所有測試"""
        print("開始測試頁面分析器...")
        
        # 創建模擬驅動
        mock_driver = MockDriver()
        
        # 創建分析器實例
        analyzer = ShopeePageAnalyzer(mock_driver)
        
        # 測試獲取頁面結構
        structure = analyzer.get_page_structure()
        print(f"頁面結構測試: {'成功' if structure else '失敗'}")
        
        # 測試查找產品元素
        product_elements = analyzer.find_product_elements()
        print(f"產品元素查找測試: {'成功' if product_elements else '失敗'}")
        
        # 測試提取所有產品信息
        products = analyzer.extract_all_products()
        print(f"產品提取測試: {'成功' if isinstance(products, list) and len(products) > 0 else '失敗'}")
        print(f"提取到 {len(products)} 個產品")
        
        # 測試處理所有產品
        results = analyzer.process_all_products()
        print(f"產品處理測試: {'成功' if isinstance(results, list) and len(results) > 0 else '失敗'}")
        print(f"處理了 {len(results)} 個產品")
        
        print("測試完成!")
        return True

if __name__ == "__main__":
    # 在直接運行此文件時執行測試
    TestPageAnalyzer.run_tests() 