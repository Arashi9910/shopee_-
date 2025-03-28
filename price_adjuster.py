import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import subprocess
import json
from page_analyzer import ShopeePageAnalyzer
from selenium.webdriver.common.keys import Keys

class PriceAdjusterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("蝦皮價格調整器")
        self.root.geometry("1000x800")  # 更大的視窗尺寸
        
        # 建立主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL輸入區域
        ttk.Label(main_frame, text="請輸入蝦皮活動網址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=90)  # 更寬的輸入框
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 按鈕區域框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        # 啟動Chrome按鈕
        self.start_chrome_button = ttk.Button(button_frame, text="啟動Chrome", command=self.start_chrome_browser)
        self.start_chrome_button.grid(row=0, column=0, padx=10)
        
        # 開始調整按鈕
        self.start_button = ttk.Button(button_frame, text="開始調整", command=self.start_adjustment)
        self.start_button.grid(row=0, column=1, padx=10)
        
        # 頁面分析按鈕
        self.analyze_button = ttk.Button(button_frame, text="分析頁面結構", command=self.analyze_page_structure)
        self.analyze_button.grid(row=0, column=2, padx=10)
        
        # 狀態顯示區域
        self.status_text = tk.Text(main_frame, height=35, width=90, font=('微軟正黑體', 12))  # 更大的文字區域和字體
        self.status_text.grid(row=2, column=0, columnspan=3, pady=5)
        
        # 捲動條
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.status_text['yscrollcommand'] = scrollbar.set
        
        self.driver = None
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
        # 添加確認變量
        self.confirmation_var = tk.IntVar()
        self.confirmation_result = None
        
    def log_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        
    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            self.log_status(f"等待元素 {value} 超時: {str(e)}")
            return None
            
    def start_chrome_browser(self):
        """啟動Chrome瀏覽器"""
        try:
            url = self.url_entry.get().strip()
            if not url:
                messagebox.showerror("錯誤", "請先輸入網址")
                return
                
            self.log_status("正在啟動Chrome...")
            
            # 設定Chrome命令
            chrome_cmd = [
                self.chrome_path,
                '--remote-debugging-port=9222',
                '--remote-allow-origins=*',
                url
            ]
            
            # 執行Chrome
            subprocess.Popen(chrome_cmd)
            self.log_status("Chrome已啟動，請在瀏覽器中完成登入")
            self.log_status("登入完成後請點擊「開始調整」按鈕")
            
            # 禁用啟動Chrome按鈕
            self.start_chrome_button.config(state='disabled')
            
        except Exception as e:
            self.log_status(f"啟動Chrome時發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"啟動Chrome失敗: {str(e)}")
            
    def start_chrome(self):
        """連接到已開啟的Chrome瀏覽器"""
        try:
            self.log_status("正在連接到Chrome...")
            
            # 設定Chrome選項
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            # 直接使用ChromeDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            self.log_status("成功連接到Chrome瀏覽器")
            
        except Exception as e:
            self.log_status(f"連接Chrome時發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"連接Chrome失敗: {str(e)}\n請確保已使用正確的參數啟動Chrome")
            if self.driver:
                self.driver.quit()
                self.driver = None
            
    def log_formatted_products(self, products):
        """格式化顯示產品和規格信息"""
        if not products or len(products) == 0:
            self.log_status("未找到任何產品")
            return
            
        self.log_status("\n====== 找到的商品列表 ======")
        self.log_status(f"共找到 {len(products)} 個商品")
        
        for i, product in enumerate(products):
            product_name = product.get('name', f"商品 #{i+1}")
            specs = product.get('specs', [])
            
            self.log_status(f"\n{i+1}. {product_name}")
            self.log_status("-" * 80)
            
            # 建立表格標題
            self.log_status(f"{'規格名稱':<40} | {'庫存':<8} | {'價格':<12} | {'狀態':<10} | {'操作':<12}")
            self.log_status("-" * 80)
            
            # 顯示每個規格
            for spec in specs:
                spec_name = spec.get('name', '未知規格')
                stock = spec.get('stock', '0')
                price = spec.get('price', '0')
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
                self.log_status(f"{spec_name:<40} | {stock:<8} | {price:<12} | {status_display:<10} | {action:<12}")
            
            self.log_status("-" * 80)
            
            # 更新界面
            self.root.update_idletasks()
    
    def check_and_process_items(self):
        """檢查並處理所有商品項目"""
        try:
            # 使用頁面分析器
            self.log_status("開始分析頁面...")
            analyzer = ShopeePageAnalyzer(self.driver)
            
            # 清空狀態文字區域
            self.status_text.delete(1.0, tk.END)
            self.log_status("開始尋找商品... 請稍候...")
            
            # 嘗試尋找Fee開頭的商品
            self.log_status("尋找【Fee】開頭的商品...")
            fee_products_info = analyzer.find_fee_products()
            
            if "error" not in fee_products_info and fee_products_info.get("product_count", 0) > 0:
                products = fee_products_info.get("products", [])
                self.log_status(f"成功找到 {len(products)} 個【Fee】商品和 {fee_products_info.get('spec_count', 0)} 個規格")
            else:
                # 如果專門方法失敗，嘗試一般的方法
                self.log_status("未找到【Fee】商品，嘗試使用一般方法...")
                products_info = analyzer.find_products_by_xpath()
                products = products_info.get("products", [])
                self.log_status(f"找到 {len(products)} 個商品和 {products_info.get('spec_count', 0)} 個規格")
            
            if not products or len(products) == 0:
                self.log_status("未找到任何商品，請檢查頁面是否正確")
                return
            
            # 顯示找到的商品
            self.log_status("\n===== 找到的商品列表 =====")
            
            # 處理每個商品
            for i, product in enumerate(products):
                product_name = product.get('name', f"商品 #{i+1}")
                specs = product.get('specs', [])
                
                self.log_status(f"\n{i+1}. {product_name}")
                self.log_status("-" * 50)
                
                if not specs:
                    self.log_status("  此商品沒有規格")
                    continue
                
                # 建立表格標題
                self.log_status(f"{'規格名稱':<30} | {'庫存':<8} | {'狀態':<10} | {'操作'}")
                self.log_status("-" * 70)
                
                # 處理每個規格
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
                            action = "需要開啟"
                        else:
                            action = "正常"
                    else:
                        action = "正常"
                    
                    # 處理可能過長的規格名稱
                    if len(spec_name) > 28:
                        spec_name = spec_name[:25] + "..."
                    
                    # 顯示規格資訊
                    self.log_status(f"{spec_name:<30} | {stock:<8} | {status:<10} | {action}")
                    
                    # 如果需要開啟，執行開啟操作
                    if action == "需要開啟":
                        self.log_status(f"正在處理: {spec_name}...")
                        result = self._toggle_product_switch(product_name, spec_name)
                        if result:
                            self.log_status(f"✓ 已成功開啟 {spec_name} 的開關")
                        else:
                            self.log_status(f"✗ 開啟 {spec_name} 的開關失敗")
                    
                    # 更新界面
                    self.root.update_idletasks()
                
                self.log_status("-" * 50)
            
            self.log_status("\n所有商品處理完成！")
            
        except Exception as e:
            self.log_status(f"處理商品時發生錯誤: {str(e)}")
            import traceback
            self.log_status(traceback.format_exc())
    
    def _toggle_product_switch(self, product_name, spec_name):
        """切換特定商品規格的開關"""
        try:
            self.log_status(f"尋找規格 '{spec_name}' 的開關...")
            
            # 使用JavaScript直接找到並操作開關
            js_result = self.driver.execute_script("""
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
                    
                    // 最後嘗試找到所有未開啟、未禁用的開關
                    console.log('通過規格名找不到，嘗試找到任何可用的開關');
                    const allSwitches = Array.from(document.querySelectorAll('div.eds-switch'))
                        .filter(sw => {
                            const isOpen = sw.classList.contains('eds-switch--open');
                            const isDisabled = sw.classList.contains('eds-switch--disabled');
                            return !isOpen && !isDisabled;
                        });
                    
                    if (allSwitches.length > 0) {
                        // 找到第一個可用的開關
                        const firstSwitch = allSwitches[0];
                        console.log('找到可用的開關');
                        
                        // 滾動到開關位置並點擊
                        firstSwitch.scrollIntoView({block: 'center'});
                        setTimeout(() => {
                            try {
                                firstSwitch.click();
                                console.log('開關已點擊');
                            } catch(e) {
                                console.error('點擊開關失敗: ' + e);
                            }
                        }, 300);
                        
                        return { success: true, message: "已點擊找到的第一個開關" };
                    }
                    
                    return { success: false, message: "找不到對應的開關" };
                }
                
                return findAndToggleSwitch(arguments[0], arguments[1]);
            """, product_name, spec_name)
            
            # 等待JavaScript操作完成
            time.sleep(1)
            
            # 處理JavaScript結果
            if js_result and js_result.get("success", False):
                self.log_status(f"✓ {js_result.get('message', '開關操作成功')}")
                return True
            else:
                error_message = js_result.get("message", "未知錯誤") if js_result else "JavaScript執行失敗"
                self.log_status(f"✗ {error_message}")
                
                # 如果JavaScript方法失敗，嘗試使用XPath直接定位開關
                self.log_status("嘗試使用XPath方法尋找開關...")
                try:
                    # 嘗試多種XPath模式
                    xpath_patterns = [
                        f"//div[contains(@class, 'ellipsis-content') and text()='{spec_name}']/ancestor::div[contains(@class, 'model-component')]//div[contains(@class, 'eds-switch')]",
                        f"//div[text()='{spec_name}']/../..//div[contains(@class, 'eds-switch')]",
                        "//div[contains(@class, 'eds-switch') and not(contains(@class, 'eds-switch--open')) and not(contains(@class, 'eds-switch--disabled'))]"
                    ]
                    
                    for xpath in xpath_patterns:
                        switches = self.driver.find_elements(By.XPATH, xpath)
                        if switches:
                            switch = switches[0]
                            # 檢查開關狀態
                            is_open = "eds-switch--open" in switch.get_attribute("class")
                            is_disabled = "eds-switch--disabled" in switch.get_attribute("class")
                            
                            if not is_disabled and not is_open:
                                # 滾動到元素位置
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch)
                                time.sleep(0.5)
                                
                                # 點擊開關
                                self.driver.execute_script("arguments[0].click();", switch)
                                self.log_status("✓ 已通過XPath點擊開關")
                                time.sleep(0.5)
                                return True
                            elif is_open:
                                self.log_status("✓ 開關已經是開啟狀態")
                                return True
                            elif is_disabled:
                                self.log_status("✗ 開關已被禁用，無法操作")
                                return False
                    
                    self.log_status("✗ 無法找到對應的開關")
                    return False
                except Exception as e:
                    self.log_status(f"✗ XPath查找開關失敗: {str(e)}")
                    return False
                
                return False
                
        except Exception as e:
            self.log_status(f"切換開關時發生錯誤: {str(e)}")
            return False
    
    def _original_check_and_process_items(self):
        """原始的商品處理方法，作為備用"""
        try:
            # 等待商品列表載入
            self.log_status("等待商品列表載入...")
            time.sleep(3)
            
            # 找到所有商品卡片
            product_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.discount-edit-item")
            self.log_status(f"找到 {len(product_cards)} 個商品")
            
            # 處理每個商品卡片
            for card_index, card in enumerate(product_cards):
                try:
                    # 獲取商品名稱
                    product_name_elem = card.find_element(By.CSS_SELECTOR, "div.ellipsis-content.single")
                    product_name = product_name_elem.text
                    
                    self.log_status(f"\n商品名稱: {product_name}")
                    self.log_status("=" * 80)
                    
                    # 找到該商品下的所有規格項目
                    specs = card.find_elements(By.CSS_SELECTOR, "div.discount-edit-item-model-component")
                    self.log_status(f"找到 {len(specs)} 個規格項目\n")
                    
                    # 處理每個規格
                    for spec in specs:
                        try:
                            # 獲取規格名稱
                            spec_name = spec.find_element(By.CSS_SELECTOR, "div.ellipsis-content.single").text
                            
                            # 檢查庫存
                            stock = spec.find_element(By.CSS_SELECTOR, "div.item-content.item-stock").text
                            stock = int(stock.strip())
                            
                            # 獲取價格
                            price = spec.find_element(By.CSS_SELECTOR, "div.item-content.item-price").text
                            
                            # 檢查按鈕狀態
                            switch = spec.find_element(By.CSS_SELECTOR, "div.eds-switch")
                            is_open = "eds-switch--open" in switch.get_attribute("class")
                            is_disabled = "eds-switch--disabled" in switch.get_attribute("class")
                            
                            # 格式化顯示資訊 - 橫向顯示
                            status_text = f"{spec_name} | 庫存: {stock} | {price} | 按鈕: {'開啟' if is_open else '關閉'}{' (已禁用)' if is_disabled else ''}"
                            self.log_status(status_text)
                            
                            if stock > 0 and not is_disabled:
                                if not is_open:
                                    self.log_status("需要操作: 開啟按鈕")
                                    # 點擊開關按鈕
                                    self.driver.execute_script("arguments[0].click();", switch)
                                    time.sleep(1)
                                    self.log_status("✓ 已完成")
                                else:
                                    self.log_status("狀態正常")
                            self.log_status("-" * 80)  # 分隔線
                            
                        except Exception as e:
                            self.log_status(f"處理規格時發生錯誤: {str(e)}")
                            continue
                
                except Exception as e:
                    self.log_status(f"處理商品 #{card_index+1} 時發生錯誤: {str(e)}")
                    continue
                
        except Exception as e:
            self.log_status(f"檢查商品時發生錯誤: {str(e)}")
            
    def start_adjustment(self):
        try:
            # 連接到Chrome
            self.start_chrome()
            
            if not self.driver:
                raise Exception("Chrome驅動程式初始化失敗")
            
            # 獲取當前URL，以便後續檢查是否跳回
            initial_url = self.driver.current_url
            self.log_status(f"當前URL: {initial_url}")
            
            # 等待頁面載入
            self.log_status("等待頁面載入...")
            time.sleep(3)
            
            # 檢查是否需要登入
            if "login" in self.driver.current_url.lower():
                self.log_status("需要登入，請在瀏覽器中手動登入...")
                messagebox.showinfo("登入提示", "請在瀏覽器中手動完成登入，然後點擊確定繼續")
            
            # 確保在正確的網頁
            target_url = self.url_entry.get().strip()
            if target_url not in self.driver.current_url:
                self.log_status(f"正在切換到目標網頁: {target_url}")
                self.driver.get(target_url)
                time.sleep(3)
            
            # 儲存當前URL，避免後續跳回
            current_url = self.driver.current_url
            self.log_status(f"目標頁面URL: {current_url}")
            
            # 檢查是否已在編輯模式
            already_in_edit_mode = False
            try:
                edit_mode_check = self.driver.execute_script("""
                    return {
                        hasEditElements: document.querySelectorAll('div.eds-switch').length > 0,
                        isEditUrl: window.location.href.includes('edit')
                    };
                """)
                
                if edit_mode_check and (edit_mode_check.get('hasEditElements', False) or edit_mode_check.get('isEditUrl', False)):
                    self.log_status("已在編輯模式，直接處理商品")
                    already_in_edit_mode = True
            except Exception as e:
                self.log_status(f"檢查編輯模式時發生錯誤: {str(e)}")
            
            # 如果不在編輯模式，點擊編輯按鈕
            if not already_in_edit_mode:
                self.log_status("正在查找「編輯折扣活動」按鈕...")
                
                # 找到按鈕元素
                edit_button = None
                try:
                    # 使用多種方法嘗試找到按鈕
                    selectors = [
                        "button[data-v-2e4150da][data-v-212c4d7f].edit-button",
                        "button.edit-button",
                        "//button[contains(text(), '編輯折扣活動')]",
                        "//button[contains(@class, 'edit-button')]"
                    ]
                    
                    for selector in selectors:
                        try:
                            if selector.startswith("//"):
                                # XPath選擇器
                                elements = self.driver.find_elements(By.XPATH, selector)
                            else:
                                # CSS選擇器
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                
                            if elements:
                                # 過濾出可見且包含正確文字的按鈕
                                for el in elements:
                                    if "編輯折扣活動" in el.text and el.is_displayed():
                                        edit_button = el
                                        self.log_status(f"✓ 找到「編輯折扣活動」按鈕: {el.text}")
                                        break
                                
                                if edit_button:
                                    break
                        except:
                            continue
                        
                    if not edit_button:
                        # 如果找不到編輯按鈕，使用更寬鬆的方法
                        self.log_status("嘗試使用更寬鬆的方法查找按鈕...")
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            try:
                                if "編輯" in button.text and button.is_displayed():
                                    edit_button = button
                                    self.log_status(f"找到可能的編輯按鈕: {button.text}")
                                    break
                            except:
                                continue
                    
                    if edit_button:
                        # 高亮顯示找到的按鈕
                        self.driver.execute_script("arguments[0].style.border='3px solid red';", edit_button)
                        
                        # 滾動到按鈕位置
                        self.log_status("滾動到按鈕位置...")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", edit_button)
                        time.sleep(1)  # 等待滾動完成
                        
                        # 使用操作鏈模擬更真實的滑鼠行為
                        self.log_status("模擬真實滑鼠點擊...")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(edit_button)  # 移動滑鼠到元素上
                        actions.pause(0.5)  # 暫停片刻，模擬人類行為
                        actions.click()     # 點擊元素
                        actions.perform()   # 執行這些動作
                        
                        self.log_status("✓ 已點擊「編輯折扣活動」按鈕")
                        
                        # 等待彈出視窗出現
                        self.log_status("等待可能出現的彈出視窗...")
                        time.sleep(2)
                        
                        # 檢查是否有彈出視窗
                        modal_found = False
                        modal_selectors = ['.eds-modal__content', '.shopee-modal__container', '[role="dialog"]', '.eds-modal__box']
                        
                        for selector in modal_selectors:
                            modal_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if modal_elements and len(modal_elements) > 0 and modal_elements[0].is_displayed():
                                modal = modal_elements[0]
                                modal_found = True
                                self.log_status(f"找到彈出視窗: {selector}")
                                
                                # 獲取彈窗文字
                                modal_text = modal.text
                                self.log_status(f"彈出視窗內容: {modal_text[:100]}")
                                
                                # 特殊處理「注意」彈窗
                                is_notice_modal = False
                                try:
                                    modal_title = modal.find_element(By.CSS_SELECTOR, ".eds-modal__title")
                                    if modal_title and "注意" in modal_title.text:
                                        is_notice_modal = True
                                        self.log_status("檢測到「注意」彈窗，使用特殊處理方式")
                                except:
                                    pass
                                
                                # 如果是"注意"彈窗，使用專用方法處理
                                if is_notice_modal:
                                    self.log_status("🔍 使用專用方法處理「注意」彈窗...")
                                    if self.handle_notice_modal(modal):
                                        self.log_status("✅ 注意彈窗已成功處理")
                                        time.sleep(3)  # 等待操作完成後的頁面加載
                                        continue
                                    else:
                                        self.log_status("❌ 注意彈窗處理失敗，嘗試其他方法")

                                # 尋找確認按鈕 - 先檢查特定類型
                                confirm_button = None
                                
                                if is_notice_modal:
                                    # 直接使用JavaScript查找並點擊按鈕
                                    self.log_status("使用直接JavaScript方法處理「注意」彈窗")
                                    
                                    js_result = self.driver.execute_script("""
                                        // 方法1: 使用精確的CSS選擇器
                                        let btn = document.querySelector('.eds-modal__footer-buttons .eds-button--primary');
                                        console.log('方法1找到按鈕:', btn);
                                        
                                        // 方法2: 查找所有主要按鈕，選擇確認按鈕
                                        if (!btn) {
                                            const primaryButtons = document.querySelectorAll('button.eds-button--primary');
                                            for (const button of primaryButtons) {
                                                if (button.innerText.includes('確認')) {
                                                    btn = button;
                                                    console.log('方法2找到按鈕:', btn);
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        // 方法3: 查找所有彈窗中的按鈕
                                        if (!btn) {
                                            const modalButtons = document.querySelectorAll('.eds-modal__box button');
                                            for (const button of modalButtons) {
                                                if (button.innerText.includes('確認')) {
                                                    btn = button;
                                                    console.log('方法3找到按鈕:', btn);
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        // 方法4: 最寬鬆的方法，查找所有按鈕
                                        if (!btn) {
                                            const allButtons = document.querySelectorAll('button');
                                            for (const button of allButtons) {
                                                if (button.innerText.includes('確認')) {
                                                    btn = button;
                                                    console.log('方法4找到按鈕:', btn);
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        if (btn) {
                                            // 記錄按鈕信息
                                            console.log('找到確認按鈕:', btn);
                                            console.log('按鈕文字:', btn.innerText);
                                            console.log('按鈕類名:', btn.className);
                                            console.log('按鈕HTML:', btn.outerHTML);
                                            
                                            // 標記按鈕
                                            btn.style.border = '5px solid red';
                                            
                                            // 嘗試點擊按鈕的多種方法
                                            try {
                                                // 方法1: 直接點擊
                                                btn.click();
                                                console.log('方法1點擊成功');
                                            } catch(e) {
                                                console.log('方法1點擊失敗:', e);
                                                
                                                try {
                                                    // 方法2: 使用MouseEvent
                                                    btn.dispatchEvent(new MouseEvent('click', {
                                                        bubbles: true,
                                                        cancelable: true,
                                                        view: window
                                                    }));
                                                    console.log('方法2點擊成功');
                                                } catch(e) {
                                                    console.log('方法2點擊失敗:', e);
                                                }
                                            }
                                            
                                            return {
                                                success: true,
                                                message: '已通過JavaScript直接點擊按鈕',
                                                buttonText: btn.innerText,
                                                buttonClass: btn.className
                                            };
                                        }
                                        
                                        return {
                                            success: false,
                                            message: '未找到確認按鈕'
                                        };
                                    """)
                                    
                                    if js_result and js_result.get('success', False):
                                        self.log_status(f"✓ JavaScript直接點擊按鈕成功: {js_result.get('message')}")
                                        self.log_status(f"按鈕文字: {js_result.get('buttonText')}, 類名: {js_result.get('buttonClass')}")
                                        time.sleep(3)  # 等待操作完成
                                    else:
                                        self.log_status("× JavaScript直接點擊失敗，嘗試下一個方法")
                                        
                                        # 使用XPath直接找按鈕
                                        self.log_status("使用XPath尋找按鈕")
                                        try:
                                            # 嘗試多種XPath定位確認按鈕
                                            xpath_patterns = [
                                                "//div[contains(@class, 'eds-modal__footer')]//button[contains(@class, 'eds-button--primary')]",
                                                "//div[contains(@class, 'eds-modal__box')]//button[contains(text(), '確認')]",
                                                "//button[contains(@class, 'eds-button--primary') and contains(text(), '確認')]",
                                                "//div[contains(@class, 'eds-modal')]//button[contains(text(), '確認')]",
                                                "//button[contains(text(), '確認')]"
                                            ]
                                            
                                            for xpath in xpath_patterns:
                                                buttons = self.driver.find_elements(By.XPATH, xpath)
                                                if buttons and len(buttons) > 0 and buttons[0].is_displayed():
                                                    confirm_button = buttons[0]
                                                    self.log_status(f"✓ 使用XPath找到確認按鈕: {confirm_button.text}")
                                                    
                                                    # 直接使用3種方法點擊
                                                    # 方法1: 執行JS點擊
                                                    self.driver.execute_script("arguments[0].click();", confirm_button)
                                                    self.log_status("已執行JS點擊")
                                                    time.sleep(1)
                                                    
                                                    # 方法2: 使用座標點擊
                                                    rect = self.driver.execute_script("""
                                                        const rect = arguments[0].getBoundingClientRect();
                                                        return {
                                                            left: rect.left,
                                                            top: rect.top,
                                                            width: rect.width,
                                                            height: rect.height
                                                        };
                                                    """, confirm_button)
                                                    
                                                    center_x = int(rect['left'] + rect['width'] / 2)
                                                    center_y = int(rect['top'] + rect['height'] / 2)
                                                    
                                                    self.log_status(f"使用座標點擊: x={center_x}, y={center_y}")
                                                    action = ActionChains(self.driver)
                                                    action.move_to_element_with_offset(confirm_button, 0, 0)
                                                    action.move_by_offset(5, 5)  # 移動到按鈕中心稍微偏右下
                                                    action.click()
                                                    action.perform()
                                                    
                                                    # 方法3: 使用原生點擊
                                                    try:
                                                        confirm_button.click()
                                                        self.log_status("已使用原生點擊方法")
                                                    except Exception as e:
                                                        self.log_status(f"原生點擊失敗: {str(e)}")
                                                    
                                                    break
                                            
                                            # 檢查是否還有彈出視窗
                                            time.sleep(3)
                                            modal_still_visible = False
                                            for selector in modal_selectors:
                                                modal_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                                if modal_elements and len(modal_elements) > 0 and modal_elements[0].is_displayed():
                                                    modal_still_visible = True
                                                    break
                                            
                                            if modal_still_visible:
                                                self.log_status("警告：彈窗仍然存在，嘗試直接關閉它")
                                                
                                                # 直接嘗試關閉彈窗的X按鈕
                                                try:
                                                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".eds-modal__close")
                                                    if close_buttons and len(close_buttons) > 0 and close_buttons[0].is_displayed():
                                                        close_buttons[0].click()
                                                        self.log_status("點擊彈窗的關閉按鈕")
                                                except Exception as e:
                                                    self.log_status(f"點擊關閉按鈕失敗: {str(e)}")
                                                
                                                # 如果仍然存在，詢問用戶手動點擊
                                                if messagebox.askyesno("彈窗點擊問題", 
                                                                    "無法自動點擊彈窗中的確認按鈕。\n\n請手動點擊確認按鈕，然後點擊「是」繼續。"):
                                                    self.log_status("用戶確認已手動點擊按鈕")
                                            else:
                                                self.log_status("✓ 彈窗已關閉，點擊成功")
                                        except Exception as e:
                                            self.log_status(f"XPath按鈕點擊失敗: {str(e)}")
                                    
                                    # 跳過後續的按鈕處理，因為已經嘗試了所有方法
                                    confirm_button = None
                                    modal_found = False
                                    continue
                                
                                # 針對「注意」彈窗的特定選擇器
                                specific_selectors = [
                                    ".eds-modal__footer-buttons .eds-button--primary",
                                    ".eds-modal__footer .eds-button--primary",
                                    ".eds-modal__box .eds-button--primary"
                                ]
                                
                                for specific_selector in specific_selectors:
                                    try:
                                        buttons = self.driver.find_elements(By.CSS_SELECTOR, specific_selector)
                                        for button in buttons:
                                            if button.is_displayed() and "確認" in button.text:
                                                self.log_status(f"找到「注意」彈窗中的確認按鈕: {button.text}")
                                                confirm_button = button
                                                break
                                        if confirm_button:
                                            break
                                    except Exception as e:
                                        self.log_status(f"查找特定按鈕時出錯: {str(e)}")
                                
                                # 一般查找方式
                                if not confirm_button:
                                    # 嘗試使用最精確的選擇器
                                    precise_selectors = [
                                        "button.eds-button.eds-button--primary.eds-button--normal",
                                        "button.eds-button--primary",
                                        ".eds-modal__footer button",
                                        ".eds-modal__footer-buttons button"
                                    ]
                                    
                                    for precise_selector in precise_selectors:
                                        try:
                                            buttons = self.driver.find_elements(By.CSS_SELECTOR, precise_selector)
                                            for button in buttons:
                                                if button.is_displayed() and "確認" in button.text:
                                                    self.log_status(f"找到精確匹配的確認按鈕: {button.text}")
                                                    confirm_button = button
                                                    break
                                            if confirm_button:
                                                break
                                        except Exception as e:
                                            self.log_status(f"查找精確按鈕時出錯: {str(e)}")
                                
                                # 如果仍找不到，嘗試更寬鬆的查找方式
                                if not confirm_button:
                                    # 嘗試查找所有按鈕
                                    button_elements = self.driver.find_elements(By.TAG_NAME, "button")
                                    
                                    # 優先查找文字包含「確認」等的按鈕
                                    for button in button_elements:
                                        if not button.is_displayed():
                                            continue
                                        
                                        button_text = button.text
                                        self.log_status(f"發現按鈕: {button_text}")
                                        if any(text in button_text for text in ["確認", "確定", "繼續", "是"]):
                                            confirm_button = button
                                            break
                                
                                # 如果找到按鈕，使用多種方法點擊
                                if confirm_button:
                                    # 記錄按鈕的完整HTML以便調試
                                    try:
                                        button_html = self.driver.execute_script("return arguments[0].outerHTML;", confirm_button)
                                        self.log_status(f"按鈕HTML: {button_html}")
                                    except:
                                        pass
                                    
                                    # 高亮顯示找到的按鈕
                                    self.driver.execute_script("arguments[0].style.border='5px solid red';", confirm_button)
                                    
                                    # 滾動到按鈕位置
                                    self.log_status("滾動到按鈕位置...")
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", confirm_button)
                                    time.sleep(1)  # 等待滾動完成
                                    
                                    # 獲取按鈕文本用於記錄
                                    button_text = confirm_button.text
                                    
                                    # 如果是「注意」彈窗，使用更精確的點擊方法
                                    if is_notice_modal:
                                        self.log_status(f"使用特殊方法點擊「注意」彈窗的「{button_text}」按鈕...")
                                        
                                        # 先嘗試最原始的方法 - 模擬Tab後Enter
                                        try:
                                            # 發送Escape鍵先清除任何可能的焦點
                                            actions = ActionChains(self.driver)
                                            actions.send_keys(Keys.ESCAPE)
                                            actions.perform()
                                            self.log_status("已發送Escape鍵")
                                            time.sleep(0.5)
                                            
                                            # 發送Tab鍵，讓焦點移動到確認按鈕
                                            for i in range(3):  # 嘗試最多發送3次Tab
                                                actions = ActionChains(self.driver)
                                                actions.send_keys(Keys.TAB)
                                                actions.perform()
                                                self.log_status(f"已發送Tab鍵 {i+1} 次")
                                                time.sleep(0.5)
                                            
                                            # 發送Enter鍵確認
                                            actions = ActionChains(self.driver)
                                            actions.send_keys(Keys.ENTER)
                                            actions.perform()
                                            self.log_status("已發送Enter鍵")
                                            time.sleep(1)
                                            
                                            # 檢查彈窗是否還存在
                                            modal_still_exists = False
                                            for selector in modal_selectors:
                                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                                if elements and len(elements) > 0 and elements[0].is_displayed():
                                                    modal_still_exists = True
                                                    break
                                            
                                            if not modal_still_exists:
                                                self.log_status("✓ 使用鍵盤操作成功關閉彈窗")
                                                return
                                            else:
                                                self.log_status("鍵盤操作未能關閉彈窗，嘗試其他方法")
                                        except Exception as e:
                                            self.log_status(f"鍵盤模擬失敗: {str(e)}")
                                        
                                        # 如果鍵盤操作失敗，嘗試最原始的Selenium方法
                                        try:
                                            # 直接使用原生click，不添加任何ActionChains
                                            confirm_button.click()
                                            self.log_status("使用原生click()方法")
                                            
                                            # 等待一下看是否消失
                                            time.sleep(2)
                                            modal_still_exists = False
                                            for selector in modal_selectors:
                                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                                if elements and len(elements) > 0 and elements[0].is_displayed():
                                                    modal_still_exists = True
                                                    break
                                            
                                            if not modal_still_exists:
                                                self.log_status("✓ 使用原生click()成功關閉彈窗")
                                                return
                                        except Exception as e:
                                            self.log_status(f"原生click()失敗: {str(e)}")
                                        
                                        # 最後嘗試通過pure JavaScript點擊
                                        try:
                                            # 嘗試通過pure JavaScript直接點擊
                                            self.driver.execute_script("""
                                                // 查找所有確認按鈕
                                                const primaryButtons = document.querySelectorAll('button.eds-button--primary');
                                                for (let btn of primaryButtons) {
                                                  if (btn.innerText.includes('確認')) {
                                                    console.log('找到確認按鈕:', btn);
                                                    btn.click();
                                                    return true;
                                                  }
                                                }
                                                
                                                // 嘗試按下Enter鍵
                                                document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {
                                                  key: 'Enter',
                                                  code: 'Enter',
                                                  keyCode: 13,
                                                  which: 13,
                                                  bubbles: true
                                                }));
                                                
                                                return false;
                                            """)
                                            self.log_status("已執行JavaScript點擊")
                                        except Exception as e:
                                            self.log_status(f"JavaScript點擊失敗: {str(e)}")
                                            
                                        # 先截圖保存按鈕位置
                                        try:
                                            screenshot_path = "modal_button.png"
                                            self.driver.save_screenshot(screenshot_path)
                                            self.log_status(f"已保存彈窗截圖到 {screenshot_path}")
                                        except Exception as e:
                                            self.log_status(f"保存截圖失敗: {str(e)}")
                                        
                                        # 方法1: 直接使用 JavaScript 點擊
                                        try:
                                            self.driver.execute_script("""
                                                arguments[0].dispatchEvent(new MouseEvent('click', {
                                                    'view': window,
                                                    'bubbles': true,
                                                    'cancelable': true
                                                }));
                                            """, confirm_button)
                                            self.log_status("使用 JavaScript MouseEvent 點擊")
                                            time.sleep(1)
                                        except Exception as e:
                                            self.log_status(f"JavaScript 點擊失敗: {str(e)}")
                                        
                                        # 方法2: 使用 JavaScript 執行按鈕的 click 方法
                                        try:
                                            self.driver.execute_script("arguments[0].click();", confirm_button)
                                            self.log_status("使用 JavaScript click() 方法點擊")
                                            time.sleep(1)
                                        except Exception as e:
                                            self.log_status(f"JavaScript click() 方法失敗: {str(e)}")
                                        
                                        # 方法3: 使用 ActionChains 點擊
                                        try:
                                            action = ActionChains(self.driver)
                                            action.move_to_element(confirm_button).pause(0.5).click().perform()
                                            self.log_status("使用 ActionChains 點擊")
                                            time.sleep(1)
                                        except Exception as e:
                                            self.log_status(f"ActionChains 點擊失敗: {str(e)}")
                                        
                                        # 方法4: 使用座標點擊
                                        try:
                                            rect = self.driver.execute_script("""
                                                const rect = arguments[0].getBoundingClientRect();
                                                return {
                                                    left: rect.left,
                                                    top: rect.top,
                                                    width: rect.width,
                                                    height: rect.height
                                                };
                                            """, confirm_button)
                                            
                                            center_x = rect['left'] + rect['width'] / 2
                                            center_y = rect['top'] + rect['height'] / 2
                                            
                                            action = ActionChains(self.driver)
                                            action.move_by_offset(center_x, center_y).click().perform()
                                            self.log_status(f"使用座標點擊 ({center_x}, {center_y})")
                                        except Exception as e:
                                            self.log_status(f"座標點擊失敗: {str(e)}")
                                        
                                        # 方法5: 使用send_keys模擬Enter鍵
                                        try:
                                            confirm_button.send_keys("\n")
                                            self.log_status("使用Enter鍵模擬點擊")
                                        except Exception as e:
                                            self.log_status(f"Enter鍵模擬點擊失敗: {str(e)}")
                                    else:
                                        # 嘗試使用多種方法確保點擊成功
                                        self.log_status(f"嘗試點擊「{button_text}」按鈕 (使用多種方法)...")
                                        
                                        # 方法1：直接使用click()方法
                                        try:
                                            confirm_button.click()
                                            self.log_status("方法1：使用element.click()方法點擊")
                                        except Exception as e:
                                            self.log_status(f"方法1失敗: {str(e)}")
                                            
                                            # 方法2：使用JavaScript點擊
                                            try:
                                                self.driver.execute_script("arguments[0].click();", confirm_button)
                                                self.log_status("方法2：使用JavaScript點擊")
                                            except Exception as e:
                                                self.log_status(f"方法2失敗: {str(e)}")
                                                
                                                # 方法3：使用ActionChains模擬人類點擊
                                                try:
                                                    actions = ActionChains(self.driver)
                                                    actions.move_to_element(confirm_button)
                                                    actions.pause(0.5)
                                                    actions.click()
                                                    actions.perform()
                                                    self.log_status("方法3：使用ActionChains點擊")
                                                except Exception as e:
                                                    self.log_status(f"方法3失敗: {str(e)}")
                                                    
                                                    # 方法4：使用更精確的坐標點擊
                                                    try:
                                                        rect = self.driver.execute_script("""
                                                            const rect = arguments[0].getBoundingClientRect();
                                                            return {
                                                                left: rect.left,
                                                                top: rect.top,
                                                                width: rect.width,
                                                                height: rect.height
                                                            }
                                                        """, confirm_button)
                                                        
                                                        # 計算按鈕中心點
                                                        center_x = rect['left'] + rect['width'] / 2
                                                        center_y = rect['top'] + rect['height'] / 2
                                                        
                                                        # 使用坐標點擊
                                                        actions = ActionChains(self.driver)
                                                        actions.move_by_offset(center_x, center_y)
                                                        actions.click()
                                                        actions.perform()
                                                        self.log_status("方法4：使用精確坐標點擊")
                                                    except Exception as e:
                                                        self.log_status(f"方法4失敗: {str(e)}")
                                    
                                    self.log_status(f"已嘗試點擊彈出視窗的「{button_text}」按鈕")
                                    
                                    # 等待確認操作完成後檢查是否還有彈窗
                                    time.sleep(3)
                                    
                                    # 檢查是否還有彈窗
                                    still_has_modal = False
                                    for selector in modal_selectors:
                                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                        if elements and len(elements) > 0 and elements[0].is_displayed():
                                            still_has_modal = True
                                            self.log_status(f"警告：彈窗仍然存在，點擊可能未成功")
                                            break
                                    
                                    if not still_has_modal:
                                        self.log_status("✓ 彈窗已關閉，點擊成功")
                                else:
                                    self.log_status("⚠️ 找到彈出視窗但無法找到可點擊的按鈕")
                                    
                                    # 截圖保存
                                    try:
                                        screenshot_path = "modal_debug.png"
                                        self.driver.save_screenshot(screenshot_path)
                                        self.log_status(f"已保存彈窗截圖到 {screenshot_path}")
                                    except Exception as e:
                                        self.log_status(f"保存截圖失敗: {str(e)}")
                                    
                                    # 詢問用戶是否手動操作
                                    if messagebox.askyesno("找不到確認按鈕", 
                                                           "找到彈出視窗但無法找到確認按鈕。\n\n請手動點擊確認按鈕，然後點擊「是」繼續。"):
                                        self.log_status("用戶確認已手動點擊按鈕")
                                
                                # 等待彈窗操作完成
                                self.log_status("等待彈窗操作完成...")
                                time.sleep(3)
                                
                                break  # 找到並處理了一個彈窗，跳出循環
                        
                        # 如果沒有找到彈窗，記錄日誌
                        if not modal_found:
                            self.log_status("未檢測到彈出視窗")
                        
                        # 檢查是否有第二個彈窗
                        self.log_status("檢查是否有其他彈窗...")
                        time.sleep(1)
                        
                        # 重新檢查是否有彈窗
                        second_modal_found = False
                        for selector in modal_selectors:
                            modal_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if modal_elements and len(modal_elements) > 0 and modal_elements[0].is_displayed():
                                modal = modal_elements[0]
                                second_modal_found = True
                                self.log_status(f"找到第二個彈出視窗: {selector}")
                                
                                # 獲取彈窗文字
                                modal_text = modal.text
                                self.log_status(f"第二個彈出視窗內容: {modal_text[:100]}")
                                
                                # 尋找確認按鈕
                                confirm_button = None
                                button_elements = modal.find_elements(By.TAG_NAME, "button")
                                
                                # 優先查找文字包含「確認」、「確定」等的按鈕
                                for button in button_elements:
                                    if not button.is_displayed():
                                        continue
                                    
                                    button_text = button.text
                                    if any(text in button_text for text in ["確認", "確定", "繼續", "是"]):
                                        confirm_button = button
                                        break
                                
                                # 如果沒找到特定文字的按鈕，嘗試查找主要操作按鈕
                                if not confirm_button:
                                    primary_buttons = modal.find_elements(By.CSS_SELECTOR, "button.eds-button--primary")
                                    if primary_buttons and len(primary_buttons) > 0 and primary_buttons[0].is_displayed():
                                        confirm_button = primary_buttons[0]
                                
                                # 如果仍然沒找到，使用第一個可見按鈕
                                if not confirm_button and len(button_elements) > 0:
                                    for button in button_elements:
                                        if button.is_displayed():
                                            confirm_button = button
                                            break
                                
                                # 如果找到按鈕，使用ActionChains模擬真實點擊
                                if confirm_button:
                                    # 獲取按鈕文本用於記錄
                                    button_text = confirm_button.text
                                    
                                    # 高亮顯示找到的按鈕
                                    self.driver.execute_script("arguments[0].style.border='3px solid red';", confirm_button)
                                    
                                    # 滾動到按鈕位置
                                    self.log_status("滾動到按鈕位置...")
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", confirm_button)
                                    time.sleep(1)  # 等待滾動完成
                                    
                                    # 使用操作鏈模擬更真實的滑鼠行為
                                    self.log_status(f"模擬真實滑鼠點擊第二個彈窗的「{button_text}」按鈕...")
                                    actions = ActionChains(self.driver)
                                    actions.move_to_element(confirm_button)  # 移動滑鼠到元素上
                                    actions.pause(0.5)  # 暫停片刻，模擬人類行為
                                    actions.click()     # 點擊元素
                                    actions.perform()   # 執行這些動作
                                    
                                    self.log_status(f"✓ 已點擊第二個彈出視窗的「{button_text}」按鈕")
                                else:
                                    self.log_status("⚠️ 找到第二個彈出視窗但無法找到可點擊的按鈕")
                                
                                # 等待彈窗操作完成
                                self.log_status("等待彈窗操作完成...")
                                time.sleep(3)
                                
                                break  # 找到並處理了第二個彈窗，跳出循環
                        
                        # 等待頁面載入
                        self.log_status("等待頁面完全載入...")
                        time.sleep(5)  # 增加等待時間確保頁面完全載入
                        
                        # 檢查當前URL，看是否跳回
                        current_url_after_click = self.driver.current_url
                        if current_url_after_click != current_url:
                            self.log_status(f"⚠️ 頁面URL已變更: {current_url_after_click}")
                            
                            # 檢查是否返回到列表頁面
                            if "list" in current_url_after_click.lower():
                                self.log_status("偵測到已返回列表頁面，這可能是正常行為。")
                                
                                # 詢問用戶是否重新導航到目標頁面
                                if messagebox.askyesno("頁面已跳轉", 
                                                     "檢測到頁面已返回列表頁面，這可能意味著操作已完成。\n\n" +
                                                     "您希望返回原始頁面並再次嘗試嗎？"):
                                    self.log_status("正在返回原始頁面...")
                                    self.driver.get(current_url)
                                    time.sleep(3)
                                    
                                    # 詢問用戶手動點擊
                                    if messagebox.askyesno("手動操作", "請手動點擊「編輯折扣活動」按鈕，操作完成後點擊「是」繼續。"):
                                        self.log_status("用戶確認已手動完成操作")
                                        time.sleep(2)
                                else:
                                    self.log_status("用戶選擇在當前頁面繼續")
                                    # 使用當前頁面嘗試分析商品
                                    try:
                                        self.check_and_process_items()
                                        return
                                    except Exception as e:
                                        self.log_status(f"在列表頁面處理商品時出錯: {str(e)}")
                                        # 繼續執行以嘗試其他方法
                        else:
                            self.log_status("✓ 頁面URL保持不變，繼續處理")
                    else:
                        self.log_status("✗ 無法找到「編輯折扣活動」按鈕")
                        
                        # 截圖保存
                        try:
                            screenshot_path = "debug_screenshot.png"
                            self.driver.save_screenshot(screenshot_path)
                            self.log_status(f"已保存當前頁面截圖到 {screenshot_path}")
                        except Exception as e:
                            self.log_status(f"截圖保存失敗: {str(e)}")
                        
                        # 詢問用戶手動操作
                        if messagebox.askyesno("找不到按鈕", 
                                              "無法自動找到「編輯折扣活動」按鈕。\n\n請手動點擊該按鈕，操作完成後點擊「是」繼續。"):
                            self.log_status("用戶確認已手動點擊按鈕")
                            time.sleep(3)  # 給用戶時間操作
                
                except Exception as e:
                    self.log_status(f"嘗試點擊按鈕時發生錯誤: {str(e)}")
                    
                    # 提供手動操作選項
                    if messagebox.askyesno("操作錯誤", 
                                          f"自動點擊時發生錯誤: {str(e)}\n\n是否要嘗試手動操作？"):
                        self.log_status("請手動操作後點擊確認")
                        if messagebox.askyesno("確認", "您已完成手動操作了嗎？"):
                            self.log_status("用戶確認已手動完成操作")
                            time.sleep(2)  # 給系統時間處理
            
            # 檢查是否已在編輯模式
            edit_mode_confirmed = False
            try:
                edit_mode_confirmed = self.driver.execute_script("""
                    return (
                        document.querySelectorAll('div.eds-switch').length > 0 ||
                        window.location.href.includes('edit') ||
                        document.querySelectorAll('.discount-edit-item').length > 0
                    );
                """)
            except Exception as e:
                self.log_status(f"檢查編輯模式時發生錯誤: {str(e)}")
            
            if edit_mode_confirmed or already_in_edit_mode:
                self.log_status("已成功進入編輯模式，開始處理商品...")
                
                # 等待頁面完全載入所有元素
                self.log_status("等待頁面完全載入所有商品和規格...")
                wait_start = time.time()
                max_wait_time = 15  # 最多等待15秒
                
                # 監控商品和規格元素的載入情況
                while time.time() - wait_start < max_wait_time:
                    elements_loaded = self.driver.execute_script("""
                        const productContainers = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                        const specElements = document.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                        const switches = document.querySelectorAll('div.eds-switch');
                        
                        return {
                            productCount: productContainers.length,
                            specCount: specElements.length,
                            switchCount: switches.length,
                            allLoaded: productContainers.length > 0 && specElements.length > 0 && switches.length > 0
                        };
                    """)
                    
                    if elements_loaded.get('allLoaded', False):
                        self.log_status(f"✓ 頁面已完全載入: {elements_loaded.get('productCount', 0)} 個商品, {elements_loaded.get('specCount', 0)} 個規格, {elements_loaded.get('switchCount', 0)} 個開關")
                        break
                    
                    # 每2秒顯示一次載入狀態
                    elapsed = time.time() - wait_start
                    if int(elapsed) % 2 == 0:
                        self.log_status(f"等待頁面載入中... ({int(elapsed)}秒) 已找到 {elements_loaded.get('productCount', 0)} 個商品, {elements_loaded.get('specCount', 0)} 個規格")
                    
                    time.sleep(1)
                
                # 開始處理商品
                self.check_and_process_items()
            else:
                self.log_status("⚠️ 無法確認是否已進入編輯模式")
                
                # 嘗試處理當前頁面
                if messagebox.askyesno("確認", "無法確認是否已進入編輯模式。\n\n是否仍要嘗試處理當前頁面的商品？"):
                    self.log_status("用戶選擇繼續處理當前頁面的商品")
                    self.check_and_process_items()
        
        except Exception as e:
            self.log_status(f"操作過程中發生錯誤: {str(e)}")
            import traceback
            self.log_status(traceback.format_exc())
    
    def analyze_page_structure(self):
        """分析當前頁面結構"""
        try:
            if not self.driver:
                # 連接到Chrome
                self.start_chrome()
                
            if not self.driver:
                messagebox.showerror("錯誤", "無法連接到Chrome瀏覽器")
                return
                
            self.log_status("\n===== 開始分析頁面結構 =====")
            
            # 創建分析器
            analyzer = ShopeePageAnalyzer(self.driver)
            
            # 分析頁面URL
            self.log_status(f"當前URL: {self.driver.current_url}")
            self.root.update_idletasks()
            
            # 嘗試使用XPath選擇器
            self.log_status("\n1. 嘗試使用XPath選擇器...")
            xpath_products = analyzer.find_products_by_xpath()
            
            if "error" in xpath_products:
                self.log_status(f"  XPath選擇器發生錯誤: {xpath_products['error']}")
            else:
                self.log_status(f"  使用XPath選擇器找到 {xpath_products.get('product_count', 0)} 個商品和 {xpath_products.get('spec_count', 0)} 個規格")
                
                # 顯示找到的產品信息
                for i, product in enumerate(xpath_products.get('products', [])[:5]):  # 顯示前5個
                    self.log_status(f"\n  商品 #{i+1}: {product.get('name', '未知名稱')}")
                    
                    # 顯示規格信息
                    for j, spec in enumerate(product.get('specs', [])[:3]):  # 顯示前3個規格
                        spec_info = f"    規格 #{j+1}: {spec.get('name', '未知規格')}"
                        
                        # 添加庫存和價格信息（如果有）
                        if spec.get('stock'):
                            spec_info += f" | 庫存: {spec.get('stock')}"
                        if spec.get('price'):
                            spec_info += f" | 價格: {spec.get('price')}"
                        if spec.get('status'):
                            spec_info += f" | 狀態: {spec.get('status')}"
                            if spec.get('disabled'):
                                spec_info += " (已禁用)"
                        
                        self.log_status(spec_info)
                    
                    # 更新UI
                    self.root.update_idletasks()
                
                # 顯示來源統計
                self.log_status("\n  來源統計:")
                self.log_status(f"    Selenium找到: {xpath_products.get('selenium_product_count', 0)} 個商品和 {xpath_products.get('selenium_spec_count', 0)} 個規格")
                self.log_status(f"    JavaScript找到: {xpath_products.get('js_product_count', 0)} 個商品和 {xpath_products.get('js_spec_count', 0)} 個規格")
            
            self.root.update_idletasks()
            
            # 尋找商品元素
            self.log_status("\n2. 嘗試尋找商品元素...")
            product_elements = analyzer.find_product_elements()
            
            if isinstance(product_elements, dict) and "error" in product_elements:
                self.log_status(f"  錯誤: {product_elements['error']}")
            elif isinstance(product_elements, dict) and "count" in product_elements:
                self.log_status(f"  找到 {product_elements['count']} 個商品，使用選擇器: {product_elements.get('selector', '未知')}")
                self.log_status(f"  範例元素: {json.dumps(product_elements.get('sample', {}), ensure_ascii=False, indent=2)}")
            else:
                self.log_status(f"  找到可能的商品元素: {len(product_elements) if isinstance(product_elements, list) else 0} 個")
            
            self.root.update_idletasks()
            
            # 檢查頁面導航方式
            self.log_status("\n3. 檢查頁面導航方式...")
            
            # 檢查分頁
            pagination = analyzer.find_pagination()
            if pagination.get("found", False):
                self.log_status(f"  檢測到分頁控制，當前第 {pagination.get('currentPage', '1')} 頁，共 {pagination.get('totalPages', '1')} 頁")
                has_next = pagination.get("hasNextPage", False)
                self.log_status(f"  是否有下一頁: {'是' if has_next else '否'}")
            else:
                self.log_status("  未檢測到標準分頁控制")
            
            self.root.update_idletasks()
            
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
            
            self.root.update_idletasks()
            
            # 提取商品詳細信息
            self.log_status("\n4. 提取商品詳細信息...")
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
                    
                    # 更新UI
                    self.root.update_idletasks()
            
            # 分析頁面結構
            self.log_status("\n5. 分析頁面DOM結構...")
            structure = analyzer.get_page_structure()
            
            if isinstance(structure, dict) and "error" in structure:
                self.log_status(f"  錯誤: {structure['error']}")
            else:
                self.log_status(f"  成功提取頁面結構，包含 {len(structure)} 個主要元素")
                
                # 顯示頁面中重要的HTML結構
                self.log_status("\n6. 頁面中的重要元素:")
                
                # 使用JavaScript查找頁面中的關鍵元素
                important_elements = self.driver.execute_script("""
                    let result = {
                        buttons: [],
                        forms: [],
                        tables: [],
                        productContainers: [],
                        switches: []
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
                    
                    // 找出所有開關
                    document.querySelectorAll('div.eds-switch, [role="switch"]').forEach(sw => {
                        const isOpen = sw.classList.contains('eds-switch--open');
                        const isDisabled = sw.classList.contains('eds-switch--disabled');
                        const rect = sw.getBoundingClientRect();
                        const isVisible = rect.width > 0 && rect.height > 0;
                        
                        result.switches.push({
                            className: sw.className,
                            isOpen: isOpen,
                            isDisabled: isDisabled,
                            isVisible: isVisible
                        });
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
                
                # 顯示開關信息
                switches = important_elements.get('switches', [])
                self.log_status(f"  找到 {len(switches)} 個開關")
                
                # 統計開關狀態
                open_switches = sum(1 for sw in switches if sw.get('isOpen', False))
                disabled_switches = sum(1 for sw in switches if sw.get('isDisabled', False))
                visible_switches = sum(1 for sw in switches if sw.get('isVisible', False))
                
                self.log_status(f"    開啟的開關: {open_switches} 個")
                self.log_status(f"    禁用的開關: {disabled_switches} 個")
                self.log_status(f"    可見的開關: {visible_switches} 個")
                self.log_status(f"    可操作的開關: {len(switches) - open_switches - disabled_switches} 個")
            
            self.root.update_idletasks()
            
            # 顯示推薦處理策略
            self.log_status("\n7. 推薦處理策略:")
            if xpath_products and xpath_products.get('product_count', 0) > 0:
                self.log_status("  推薦使用XPath選擇器策略")
                
                # 測試XPath策略
                self.log_status("\n8. 測試XPath策略...")
                xpath_result = analyzer.process_with_xpath_strategy()
                
                if xpath_result.get("strategy") == "xpath" and xpath_result.get("results"):
                    products = xpath_result["results"]
                    self.log_status(f"  測試成功，XPath策略找到並處理了 {len(products)} 個商品")
                    
                    # 顯示操作統計
                    need_action = 0
                    for product in products:
                        for spec in product["specs"]:
                            if spec["action"] == "需要開啟":
                                need_action += 1
                    
                    self.log_status(f"  需要開啟的開關數量: {need_action} 個")
                    
                else:
                    self.log_status(f"  測試失敗: {xpath_result.get('error', '未知錯誤')}")
            
            elif pagination.get("found", False) and pagination.get("totalPages", 1) > 1:
                self.log_status("  推薦使用分頁策略，逐頁處理商品")
            elif scroll_info.get("mayUseInfiniteScroll", False):
                self.log_status("  推薦使用無限滾動策略，邊滾動邊收集商品")
            else:
                self.log_status("  推薦使用單頁處理策略")
                
            self.log_status("\n===== 頁面分析完成 =====")
            
        except Exception as e:
            self.log_status(f"分析頁面結構時發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"分析頁面結構時發生錯誤: {str(e)}")
            
    def set_confirmation(self, result):
        """設置用戶確認結果"""
        self.confirmation_result = result
        self.confirmation_var.set(1)  # 觸發wait_variable
        
    def __del__(self):
        if self.driver:
            self.driver.quit()

    def log_summary_products(self, products):
        """精簡顯示產品和規格摘要信息，用於輕鬆檢視商品列表"""
        if not products or len(products) == 0:
            self.log_status("未找到任何產品")
            return
            
        # 清空當前狀態文本
        self.status_text.delete(1.0, tk.END)
        
        # 顯示總共找到的商品數量
        total_products = len(products)
        total_specs = sum(len(product.get('specs', [])) for product in products)
        
        self.log_status("===== 商品分析摘要 =====")
        self.log_status(f"總共找到: {total_products} 個商品, {total_specs} 個規格")
        self.log_status("=" * 80)
        
        # 計算總頁數
        page_size = 10
        total_pages = (total_products + page_size - 1) // page_size
        
        # 創建頁面選擇Frame
        if hasattr(self, 'page_frame') and self.page_frame:
            try:
                self.page_frame.grid_forget()
            except:
                pass
            
        self.page_frame = ttk.Frame(self.root)
        self.page_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        # 頁碼標籤
        self.page_label = ttk.Label(self.page_frame, text=f"頁面 1 / {total_pages}")
        self.page_label.grid(row=0, column=1, padx=5)
        
        # 頁面切換按鈕
        if total_pages > 1:
            self.prev_btn = ttk.Button(self.page_frame, text="上一頁", state="disabled",
                                       command=lambda: self.show_product_page(products, self.current_page-1, page_size))
            self.prev_btn.grid(row=0, column=0, padx=10)
            
            self.next_btn = ttk.Button(self.page_frame, text="下一頁", 
                                       command=lambda: self.show_product_page(products, self.current_page+1, page_size))
            self.next_btn.grid(row=0, column=2, padx=10)
            
            # 添加輸入頁碼和跳轉按鈕
            ttk.Label(self.page_frame, text="跳至頁碼:").grid(row=0, column=3, padx=(20, 5))
            self.page_entry = ttk.Entry(self.page_frame, width=5)
            self.page_entry.grid(row=0, column=4, padx=5)
            ttk.Button(self.page_frame, text="跳轉", 
                       command=lambda: self.jump_to_page(products, page_size)).grid(row=0, column=5, padx=5)
        
        # 初始頁面
        self.current_page = 1
        
        # 顯示第一頁商品
        self.show_product_page(products, 1, page_size)
        
        # 創建確認處理按鈕
        if hasattr(self, 'action_frame') and self.action_frame:
            try:
                self.action_frame.grid_forget()
            except:
                pass
            
        self.action_frame = ttk.Frame(self.root)
        self.action_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(self.action_frame, text="處理所有商品", 
                  command=lambda: self.process_selected_products(products)).grid(row=0, column=0, padx=10)
        
        ttk.Button(self.action_frame, text="匯出商品列表", 
                  command=lambda: self.export_products(products)).grid(row=0, column=1, padx=10)
        
        ttk.Button(self.action_frame, text="取消", 
                  command=self.cancel_processing).grid(row=0, column=2, padx=10)
    
    def show_product_page(self, products, page, page_size=10):
        """顯示指定頁碼的商品信息"""
        # 清空當前商品顯示
        self.status_text.delete(1.0, tk.END)
        
        # 計算總頁數
        total_products = len(products)
        total_pages = (total_products + page_size - 1) // page_size
        
        # 確保頁碼合法
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
            
        self.current_page = page
        
        # 更新頁碼標籤
        self.page_label.config(text=f"頁面 {page} / {total_pages}")
        
        # 更新按鈕狀態
        if hasattr(self, 'prev_btn'):
            self.prev_btn.config(state="normal" if page > 1 else "disabled")
        if hasattr(self, 'next_btn'):
            self.next_btn.config(state="normal" if page < total_pages else "disabled")
        
        # 計算當前頁顯示的商品
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_products)
        
        self.log_status(f"===== 商品列表 (顯示 {start_idx+1}-{end_idx} / 共 {total_products} 個商品) =====")
        
        # 顯示當前頁的商品
        for i in range(start_idx, end_idx):
            product = products[i]
            product_name = product.get('name', f"商品 #{i+1}")
            specs = product.get('specs', [])
            
            self.log_status(f"\n{i+1}. {product_name}")
            self.log_status("-" * 80)
            
            # 規格計數
            total_specs = len(specs)
            open_specs = sum(1 for spec in specs if spec.get('status') == '開啟')
            closed_specs = total_specs - open_specs
            
            # 庫存計數
            in_stock = sum(1 for spec in specs if spec.get('stock') and ''.join(filter(str.isdigit, str(spec.get('stock', '0')))) != '0')
            sold_out = total_specs - in_stock
            
            # 顯示規格統計
            self.log_status(f"規格總數: {total_specs} | 開啟狀態: {open_specs} | 關閉狀態: {closed_specs}")
            self.log_status(f"有庫存規格: {in_stock} | 售罄規格: {sold_out}")
            
            # 顯示前5個規格的簡要信息
            if specs:
                self.log_status("\n規格預覽:")
                for j, spec in enumerate(specs[:5]):  # 只顯示前5個規格
                    spec_name = spec.get('name', '未知規格')
                    stock = spec.get('stock', '0')
                    price = spec.get('price', '0')
                    status = spec.get('status', '未知')
                    
                    # 處理可能過長的規格名稱
                    if len(spec_name) > 30:
                        spec_name = spec_name[:27] + "..."
                    
                    self.log_status(f"  {spec_name:<30} | 庫存: {stock:<8} | 價格: {price:<12} | 狀態: {status}")
                
                if len(specs) > 5:
                    self.log_status(f"  ... 還有 {len(specs) - 5} 個規格 ...")
            
            self.log_status("-" * 80)
            
            # 每顯示一個商品更新UI
            self.root.update_idletasks()
    
    def jump_to_page(self, products, page_size=10):
        """跳轉到指定頁碼"""
        try:
            page = int(self.page_entry.get())
            self.show_product_page(products, page, page_size)
        except ValueError:
            self.log_status("請輸入有效的頁碼")
    
    def process_selected_products(self, products):
        """處理所有商品"""
        self.log_status("\n準備處理所有商品...")
        
        # 設置確認變量
        self.confirmation_result = True
        
        # 移除分頁和操作按鈕
        if hasattr(self, 'page_frame') and self.page_frame:
            self.page_frame.grid_forget()
        
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.grid_forget()
        
        # 調用原始處理方法
        self._process_products(products)
    
    def export_products(self, products):
        """將商品列表導出到檔案"""
        import datetime
        
        try:
            # 創建檔案名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"產品清單_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"===== 商品列表總共 {len(products)} 個商品 =====\n\n")
                
                for i, product in enumerate(products):
                    product_name = product.get('name', f"商品 #{i+1}")
                    specs = product.get('specs', [])
                    
                    f.write(f"{i+1}. {product_name}\n")
                    f.write("-" * 80 + "\n")
                    
                    for j, spec in enumerate(specs):
                        spec_name = spec.get('name', '未知規格')
                        stock = spec.get('stock', '0')
                        price = spec.get('price', '0')
                        status = spec.get('status', '未知')
                        disabled = spec.get('disabled', False)
                        
                        status_display = f"{status}{' (已禁用)' if disabled else ''}"
                        f.write(f"  規格 #{j+1}: {spec_name} | 庫存: {stock} | 價格: {price} | 狀態: {status_display}\n")
                    
                    f.write("-" * 80 + "\n\n")
            
            self.log_status(f"\n已成功匯出商品列表: {filename}")
            
        except Exception as e:
            self.log_status(f"匯出商品列表時發生錯誤: {str(e)}")
    
    def cancel_processing(self):
        """取消商品處理"""
        self.log_status("\n用戶取消操作")
        
        # 移除分頁和操作按鈕
        if hasattr(self, 'page_frame') and self.page_frame:
            self.page_frame.grid_forget()
        
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.grid_forget()
    
    def _process_products(self, products):
        """實際處理商品的方法"""
        self.log_status("\n開始處理商品...")
        
        # 處理每個商品
        for i, product in enumerate(products):
            self.log_status(f"\n商品 #{i+1}: {product['name']}")
            self.log_status("=" * 80)
            
            # 處理規格
            specs = product.get("specs", [])
            for j, spec in enumerate(specs):
                spec_name = spec.get("name", f"規格 #{j+1}")
                spec_stock = spec.get("stock", "0")
                spec_price = spec.get("price", "0")
                spec_status = spec.get("status", "未知")
                spec_disabled = spec.get("disabled", False)
                
                # 嘗試提取庫存數字
                try:
                    stock_number = int(''.join(filter(str.isdigit, str(spec_stock))))
                except:
                    stock_number = 0
                
                # 確定操作動作
                if stock_number > 0 and not spec_disabled:
                    if spec_status != "開啟":
                        action = "需要開啟"
                    else:
                        action = "狀態正常，無需操作"
                else:
                    action = "狀態正常，無需操作"
                
                status_text = f"規格 #{j+1}: {spec_name} | 庫存: {spec_stock} | 價格: {spec_price} | 狀態: {spec_status}{' (已禁用)' if spec_disabled else ''}"
                self.log_status(status_text)
                
                if action == "需要開啟":
                    self.log_status("需要操作: 開啟按鈕")
                    # 實際操作商品開關
                    self.log_status(f"正在處理 '{spec_name}' 的開關...")
                    result = self._toggle_product_switch(product['name'], spec_name)
                    if result:
                        self.log_status("✓ 已成功開啟開關")
                    else:
                        self.log_status("✗ 開啟開關失敗")
                
                self.log_status("-" * 80)
                
                # 更新界面
                self.root.update_idletasks()
            
            # 每處理5個商品更新一次UI
            if i % 5 == 0:
                self.log_status(f"已處理 {i+1}/{len(products)} 個商品...")
                self.root.update_idletasks()
        
        self.log_status("\n所有商品處理完成！")
    
    def handle_notice_modal(self, modal_element):
        """專門處理「注意」類型的彈窗"""
        self.log_status("開始處理「注意」彈窗...")
        
        try:
            # 讀取彈窗內容用於日誌記錄
            try:
                modal_body = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__body").text
                self.log_status(f"彈窗內容: {modal_body}")
            except:
                pass
            
            # 方法1: 使用JavaScript直接定位並點擊按鈕 (最可靠的方法)
            self.log_status("方法1: 使用JavaScript直接點擊...")
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
                self.log_status("✓ JavaScript方法成功點擊按鈕")
                time.sleep(1)
                
                # 檢查彈窗是否消失
                if not self.is_modal_visible():
                    return True
            
            # 方法2: 使用鍵盤快捷鍵 - 先用escape清除焦點
            self.log_status("方法2: 使用鍵盤模擬...")
            # 先按ESC清除當前焦點
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            
            # 用TAB鍵移動焦點到確認按鈕 (通常是頁面上第3-5個可聚焦元素)
            for i in range(5):
                ActionChains(self.driver).send_keys(Keys.TAB).perform()
                time.sleep(0.5)
            
            # 按Enter確認
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(1)
            
            # 檢查彈窗是否消失
            if not self.is_modal_visible():
                self.log_status("✓ 鍵盤方法成功關閉彈窗")
                return True
            
            # 方法3: 使用XPath精確定位按鈕
            self.log_status("方法3: 使用XPath精確定位...")
            try:
                button = self.driver.find_element(By.XPATH, 
                    "//div[contains(@class, 'eds-modal__footer-buttons')]//button[contains(@class, 'eds-button--primary')]")
                
                if button and button.is_displayed():
                    self.log_status(f"找到按鈕: {button.text}")
                    
                    # 高亮顯示按鈕
                    self.driver.execute_script("arguments[0].style.border='3px solid blue';", button)
                    
                    # 方法3.1: 直接點擊
                    try:
                        button.click()
                        self.log_status("嘗試直接點擊")
                        time.sleep(1)
                        
                        if not self.is_modal_visible():
                            self.log_status("✓ 直接點擊成功")
                            return True
                    except Exception as e:
                        self.log_status(f"直接點擊失敗: {str(e)}")
                    
                    # 方法3.2: 使用JavaScript點擊
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                        self.log_status("嘗試JavaScript點擊")
                        time.sleep(1)
                        
                        if not self.is_modal_visible():
                            self.log_status("✓ JavaScript點擊成功")
                            return True
                    except Exception as e:
                        self.log_status(f"JavaScript點擊失敗: {str(e)}")
                    
                    # 方法3.3: 使用ActionChains點擊
                    try:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(button).pause(0.3).click().perform()
                        self.log_status("嘗試ActionChains點擊")
                        time.sleep(1)
                        
                        if not self.is_modal_visible():
                            self.log_status("✓ ActionChains點擊成功")
                            return True
                    except Exception as e:
                        self.log_status(f"ActionChains點擊失敗: {str(e)}")
            except Exception as e:
                self.log_status(f"XPath尋找按鈕失敗: {str(e)}")
            
            # 方法4: 尋找關閉按鈕
            self.log_status("方法4: 嘗試點擊關閉按鈕...")
            try:
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".eds-modal__close")
                if close_buttons and len(close_buttons) > 0 and close_buttons[0].is_displayed():
                    close_buttons[0].click()
                    self.log_status("點擊關閉按鈕")
                    time.sleep(1)
                    
                    if not self.is_modal_visible():
                        self.log_status("✓ 通過關閉按鈕成功關閉彈窗")
                        return True
            except Exception as e:
                self.log_status(f"點擊關閉按鈕失敗: {str(e)}")
            
            # 方法5: 嘗試發送Escape鍵關閉彈窗
            self.log_status("方法5: 使用Escape鍵...")
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            
            if not self.is_modal_visible():
                self.log_status("✓ Escape鍵成功關閉彈窗")
                return True
            
            # 方法6: 通知用戶手動關閉
            self.log_status("❗ 自動方法均失敗，請手動點擊確認按鈕")
            messagebox.showinfo("需要手動操作", "請手動點擊彈窗中的確認按鈕，然後點擊確定繼續。")
            
            # 等待用戶手動關閉
            for _ in range(10):  # 最多等待10秒
                if not self.is_modal_visible():
                    self.log_status("✓ 彈窗已被手動關閉")
                    return True
                time.sleep(1)
            
            return not self.is_modal_visible()
        
        except Exception as e:
            self.log_status(f"處理「注意」彈窗時發生錯誤: {str(e)}")
            return False
    
    def is_modal_visible(self):
        """檢查彈窗是否可見"""
        try:
            modal_selectors = ['.eds-modal__content', '.shopee-modal__container', '[role="dialog"]', '.eds-modal__box']
            
            for selector in modal_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0 and elements[0].is_displayed():
                    return True
            
            return False
        except:
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceAdjusterGUI(root)
    root.mainloop() 