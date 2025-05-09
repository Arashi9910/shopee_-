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
        self.root.title("?衣?寞隤踵??)
        self.root.geometry("1000x800")  # ?游之??蝒偕撖?
        
        # 撱箇?銝餅???
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL頛詨???
        ttk.Label(main_frame, text="隢撓?亥?格暑?雯?:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=90)  # ?游祝?撓?交?
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # ???????
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        # ??Chrome??
        self.start_chrome_button = ttk.Button(button_frame, text="??Chrome", command=self.start_chrome_browser)
        self.start_chrome_button.grid(row=0, column=0, padx=10)
        
        # ??隤踵??
        self.start_button = ttk.Button(button_frame, text="??隤踵", command=self.start_adjustment)
        self.start_button.grid(row=0, column=1, padx=10)
        
        # ?????
        self.analyze_button = ttk.Button(button_frame, text="???蝯?", command=self.analyze_page_structure)
        self.analyze_button.grid(row=0, column=2, padx=10)
        
        # ??＊蝷箏???
        self.status_text = tk.Text(main_frame, height=35, width=90, font=('敺株?甇??擃?, 12))  # ?游之??摮???摮?
        self.status_text.grid(row=2, column=0, columnspan=3, pady=5)
        
        # ?脣?璇?
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.status_text['yscrollcommand'] = scrollbar.set
        
        self.driver = None
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
        # 瘛餃?蝣箄?霈?
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
            self.log_status(f"蝑??? {value} 頞?: {str(e)}")
            return None
            
    def start_chrome_browser(self):
        """??Chrome?汗??""
        try:
            url = self.url_entry.get().strip()
            if not url:
                messagebox.showerror("?航炊", "隢?頛詨蝬脣?")
                return
                
            self.log_status("甇???Chrome...")
            
            # 閮剖?Chrome?賭誘
            chrome_cmd = [
                self.chrome_path,
                '--remote-debugging-port=9222',
                '--remote-allow-origins=*',
                url
            ]
            
            # ?瑁?Chrome
            subprocess.Popen(chrome_cmd)
            self.log_status("Chrome撌脣???隢?汗?其葉摰??餃")
            self.log_status("?餃摰?敺?暺???憪矽?氬???)
            
            # 蝳??Chrome??
            self.start_chrome_button.config(state='disabled')
            
        except Exception as e:
            self.log_status(f"??Chrome??隤? {str(e)}")
            messagebox.showerror("?航炊", f"??Chrome憭望?: {str(e)}")
            
    def start_chrome(self):
        """???啣歇???hrome?汗??""
        try:
            self.log_status("甇????蚓hrome...")
            
            # 閮剖?Chrome?賊?
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            # ?湔雿輻ChromeDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            self.log_status("?????蚓hrome?汗??)
            
        except Exception as e:
            self.log_status(f"??Chrome??隤? {str(e)}")
            messagebox.showerror("?航炊", f"??Chrome憭望?: {str(e)}\n隢Ⅱ靽歇雿輻甇?Ⅱ???詨??hrome")
            if self.driver:
                self.driver.quit()
                self.driver = None
            
    def log_formatted_products(self, products):
        """?澆??＊蝷箇??閬靽⊥"""
        if not products or len(products) == 0:
            self.log_status("?芣?唬遙雿??)
            return
            
        self.log_status("\n====== ?曉????銵?======")
        self.log_status(f"?望??{len(products)} ????)
        
        for i, product in enumerate(products):
            product_name = product.get('name', f"?? #{i+1}")
            specs = product.get('specs', [])
            
            self.log_status(f"\n{i+1}. {product_name}")
            self.log_status("-" * 80)
            
            # 撱箇?銵冽璅?
            self.log_status(f"{'閬?迂':<40} | {'摨怠?':<8} | {'?寞':<12} | {'???:<10} | {'??':<12}")
            self.log_status("-" * 80)
            
            # 憿舐內瘥???
            for spec in specs:
                spec_name = spec.get('name', '?芰閬')
                stock = spec.get('stock', '0')
                price = spec.get('price', '0')
                status = spec.get('status', '?芰')
                disabled = spec.get('disabled', False)
                
                # ?岫??摨怠??詨?
                try:
                    stock_number = int(''.join(filter(str.isdigit, str(stock))))
                except:
                    stock_number = 0
                
                # 蝣箏?????
                if stock_number > 0 and not disabled:
                    if status != "??":
                        action = "?閬???
                    else:
                        action = "甇?虜"
                else:
                    action = "甇?虜"
                
                # ???航????澆?蝔?
                if len(spec_name) > 38:
                    spec_name = spec_name[:35] + "..."
                
                # ?澆??＊蝷?
                status_display = f"{status}{' (撌脩???' if disabled else ''}"
                self.log_status(f"{spec_name:<40} | {stock:<8} | {price:<12} | {status_display:<10} | {action:<12}")
            
            self.log_status("-" * 80)
            
            # ?湔?
            self.root.update_idletasks()
    
    def check_and_process_items(self):
        """瑼Ｘ銝西?????????""
        try:
            # 雿輻?????
            self.log_status("?????...")
            analyzer = ShopeePageAnalyzer(self.driver)
            
            # 皜征???摮???
            self.status_text.delete(1.0, tk.END)
            self.log_status("??撠??... 隢???..")
            
            # ?岫撠Fee?????
            self.log_status("撠?ee???剔???...")
            fee_products_info = analyzer.find_fee_products()
            
            if "error" not in fee_products_info and fee_products_info.get("product_count", 0) > 0:
                products = fee_products_info.get("products", [])
                self.log_status(f"???曉 {len(products)} ?ee???? {fee_products_info.get('spec_count', 0)} ????)
            else:
                # 憒?撠??寞?憭望?嚗?閰虫??祉??寞?
                self.log_status("?芣?啜ee?????岫雿輻銝?祆瘜?..")
                products_info = analyzer.find_products_by_xpath()
                products = products_info.get("products", [])
                self.log_status(f"?曉 {len(products)} ???? {products_info.get('spec_count', 0)} ????)
            
            if not products or len(products) == 0:
                self.log_status("?芣?唬遙雿???隢炎?仿??Ｘ?行迤蝣?)
                return
            
            # 憿舐內?曉????
            self.log_status("\n===== ?曉????銵?=====")
            
            # ??瘥???
            for i, product in enumerate(products):
                product_name = product.get('name', f"?? #{i+1}")
                specs = product.get('specs', [])
                
                self.log_status(f"\n{i+1}. {product_name}")
                self.log_status("-" * 50)
                
                if not specs:
                    self.log_status("  甇文???????)
                    continue
                
                # 撱箇?銵冽璅?
                self.log_status(f"{'閬?迂':<30} | {'摨怠?':<8} | {'???:<10} | {'??'}")
                self.log_status("-" * 70)
                
                # ??瘥???
                for spec in specs:
                    spec_name = spec.get('name', '?芰閬')
                    stock = spec.get('stock', '0')
                    status = spec.get('status', '?芰')
                    disabled = spec.get('disabled', False)
                    
                    # ?岫??摨怠??詨?
                    try:
                        stock_number = int(''.join(filter(str.isdigit, str(stock))))
                    except:
                        stock_number = 0
                    
                    # 蝣箏?????
                    if stock_number > 0 and not disabled:
                        if status != "??":
                            action = "?閬???
                        else:
                            action = "甇?虜"
                    else:
                        action = "甇?虜"
                    
                    # ???航????澆?蝔?
                    if len(spec_name) > 28:
                        spec_name = spec_name[:25] + "..."
                    
                    # 憿舐內閬鞈?
                    self.log_status(f"{spec_name:<30} | {stock:<8} | {status:<10} | {action}")
                    
                    # 憒??閬????瑁?????
                    if action == "?閬???:
                        self.log_status(f"甇???: {spec_name}...")
                        result = self._toggle_product_switch(product_name, spec_name)
                        if result:
                            self.log_status(f"??撌脫?????{spec_name} ????)
                        else:
                            self.log_status(f"???? {spec_name} ???仃??)
                    
                    # ?湔?
                    self.root.update_idletasks()
                
                self.log_status("-" * 50)
            
            self.log_status("\n?????????")
            
        except Exception as e:
            self.log_status(f"??????隤? {str(e)}")
            import traceback
            self.log_status(traceback.format_exc())
    
    def _toggle_product_switch(self, product_name, spec_name):
        """???孵???閬????""
        try:
            self.log_status(f"撠閬 '{spec_name}' ????..")
            
            # 雿輻JavaScript?湔?曉銝行?雿???
            js_result = self.driver.execute_script("""
                function findAndToggleSwitch(productName, specName) {
                    console.log('?岫撠??嚗??? ' + productName + ', 閬: ' + specName);
                    
                    // 擐??函楊頛舀芋撘?撠
                    // 1. 撠??摰孵
                    let productContainer = null;
                    const productContainers = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                    
                    for (const container of productContainers) {
                        const nameEl = container.querySelector('div.ellipsis-content.single');
                        if (nameEl && nameEl.innerText.trim() === productName) {
                            productContainer = container;
                            console.log('?曉??摰孵');
                            break;
                        }
                    }
                    
                    // 2. 憒??曉??摰孵嚗?曇??澆?撠?????
                    if (productContainer) {
                        // 撠閬??
                        const specElements = productContainer.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                        
                        for (const specElement of specElements) {
                            const specNameEl = specElement.querySelector('div.ellipsis-content.single');
                            if (specNameEl && specNameEl.innerText.trim() === specName) {
                                console.log('?曉閬??');
                                
                                // 撠????
                                const switchEl = specElement.querySelector('div.eds-switch');
                                if (switchEl) {
                                    console.log('?曉????');
                                    
                                    // 瑼Ｘ?????
                                    const isOpen = switchEl.classList.contains('eds-switch--open');
                                    const isDisabled = switchEl.classList.contains('eds-switch--disabled');
                                    
                                    if (isDisabled) {
                                        return { success: false, message: "??撌脰◤蝳嚗瘜?雿? };
                                    }
                                    
                                    if (isOpen) {
                                        return { success: true, message: "??撌脩??舫????? };
                                    }
                                    
                                    // 皛曉??圈???蝵桐蒂暺?
                                    switchEl.scrollIntoView({block: 'center'});
                                    setTimeout(() => {
                                        try {
                                            switchEl.click();
                                            console.log('??撌脤???);
                                        } catch(e) {
                                            console.error('暺???憭望?: ' + e);
                                        }
                                    }, 300);
                                    
                                    return { success: true, message: "撌脤????? };
                                }
                            }
                        }
                    }
                    
                    // 憒??⊥???????閬??堆??岫?芷?閬???
                    console.log('?????銝嚗?閰血?刻??澆??交');
                    
                    // 撠????怨??澆???蝝?
                    const specElems = document.querySelectorAll('div.ellipsis-content.single');
                    for (const elem of specElems) {
                        if (elem.innerText.trim() === specName) {
                            console.log('?曉閬?迂?寥???蝝?);
                            
                            // ???交??摰孵
                            let current = elem;
                            let foundSwitch = null;
                            for (let i = 0; i < 5; i++) {
                                if (!current) break;
                                
                                // ?岫?函??蝝葉?暸???
                                const switchEls = current.querySelectorAll('div.eds-switch');
                                if (switchEls.length > 0) {
                                    foundSwitch = switchEls[0];
                                    break;
                                }
                                
                                // ??蝝??
                                current = current.parentElement;
                                if (current) {
                                    // ?函??銝剜?暸???
                                    const parentSwitches = current.querySelectorAll('div.eds-switch');
                                    if (parentSwitches.length > 0) {
                                        foundSwitch = parentSwitches[0];
                                        break;
                                    }
                                }
                            }
                            
                            if (foundSwitch) {
                                console.log('?曉??');
                                
                                // 瑼Ｘ?????
                                const isOpen = foundSwitch.classList.contains('eds-switch--open');
                                const isDisabled = foundSwitch.classList.contains('eds-switch--disabled');
                                
                                if (isDisabled) {
                                    return { success: false, message: "??撌脰◤蝳嚗瘜?雿? };
                                }
                                
                                if (isOpen) {
                                    return { success: true, message: "??撌脩??舫????? };
                                }
                                
                                // 皛曉??圈???蝵桐蒂暺?
                                foundSwitch.scrollIntoView({block: 'center'});
                                setTimeout(() => {
                                    try {
                                        foundSwitch.click();
                                        console.log('??撌脤???);
                                    } catch(e) {
                                        console.error('暺???憭望?: ' + e);
                                    }
                                }, 300);
                                
                                return { success: true, message: "撌脤????? };
                            }
                        }
                    }
                    
                    // ?敺?閰行?唳?????蝳????
                    console.log('??閬?銝嚗?閰行?唬遙雿?函???');
                    const allSwitches = Array.from(document.querySelectorAll('div.eds-switch'))
                        .filter(sw => {
                            const isOpen = sw.classList.contains('eds-switch--open');
                            const isDisabled = sw.classList.contains('eds-switch--disabled');
                            return !isOpen && !isDisabled;
                        });
                    
                    if (allSwitches.length > 0) {
                        // ?曉蝚砌???函???
                        const firstSwitch = allSwitches[0];
                        console.log('?曉?舐????);
                        
                        // 皛曉??圈???蝵桐蒂暺?
                        firstSwitch.scrollIntoView({block: 'center'});
                        setTimeout(() => {
                            try {
                                firstSwitch.click();
                                console.log('??撌脤???);
                            } catch(e) {
                                console.error('暺???憭望?: ' + e);
                            }
                        }, 300);
                        
                        return { success: true, message: "撌脤???啁?蝚砌????? };
                    }
                    
                    return { success: false, message: "?曆??啣?????" };
                }
                
                return findAndToggleSwitch(arguments[0], arguments[1]);
            """, product_name, spec_name)
            
            # 蝑?JavaScript??摰?
            time.sleep(1)
            
            # ??JavaScript蝯?
            if js_result and js_result.get("success", False):
                self.log_status(f"??{js_result.get('message', '??????')}")
                return True
            else:
                error_message = js_result.get("message", "?芰?航炊") if js_result else "JavaScript?瑁?憭望?"
                self.log_status(f"??{error_message}")
                
                # 憒?JavaScript?寞?憭望?嚗?閰虫蝙?汴Path?湔摰???
                self.log_status("?岫雿輻XPath?寞?撠??...")
                try:
                    # ?岫憭車XPath璅∪?
                    xpath_patterns = [
                        f"//div[contains(@class, 'ellipsis-content') and text()='{spec_name}']/ancestor::div[contains(@class, 'model-component')]//div[contains(@class, 'eds-switch')]",
                        f"//div[text()='{spec_name}']/../..//div[contains(@class, 'eds-switch')]",
                        "//div[contains(@class, 'eds-switch') and not(contains(@class, 'eds-switch--open')) and not(contains(@class, 'eds-switch--disabled'))]"
                    ]
                    
                    for xpath in xpath_patterns:
                        switches = self.driver.find_elements(By.XPATH, xpath)
                        if switches:
                            switch = switches[0]
                            # 瑼Ｘ?????
                            is_open = "eds-switch--open" in switch.get_attribute("class")
                            is_disabled = "eds-switch--disabled" in switch.get_attribute("class")
                            
                            if not is_disabled and not is_open:
                                # 皛曉??啣?蝝?蝵?
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch)
                                time.sleep(0.5)
                                
                                # 暺???
                                self.driver.execute_script("arguments[0].click();", switch)
                                self.log_status("??撌脤?XPath暺???")
                                time.sleep(0.5)
                                return True
                            elif is_open:
                                self.log_status("????撌脩??舫?????)
                                return True
                            elif is_disabled:
                                self.log_status("????撌脰◤蝳嚗瘜?雿?)
                                return False
                    
                    self.log_status("???⊥??曉撠?????)
                    return False
                except Exception as e:
                    self.log_status(f"??XPath?交??憭望?: {str(e)}")
                    return False
                
                return False
                
        except Exception as e:
            self.log_status(f"??????隤? {str(e)}")
            return False
    
    def _original_check_and_process_items(self):
        """???????瘜?雿?"""
        try:
            # 蝑????”頛
            self.log_status("蝑????”頛...")
            time.sleep(3)
            
            # ?曉??????
            product_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.discount-edit-item")
            self.log_status(f"?曉 {len(product_cards)} ????)
            
            # ??瘥????
            for card_index, card in enumerate(product_cards):
                try:
                    # ?脣????迂
                    product_name_elem = card.find_element(By.CSS_SELECTOR, "div.ellipsis-content.single")
                    product_name = product_name_elem.text
                    
                    self.log_status(f"\n???迂: {product_name}")
                    self.log_status("=" * 80)
                    
                    # ?曉閰脣????????潮???
                    specs = card.find_elements(By.CSS_SELECTOR, "div.discount-edit-item-model-component")
                    self.log_status(f"?曉 {len(specs)} ???潮??娉n")
                    
                    # ??瘥???
                    for spec in specs:
                        try:
                            # ?脣?閬?迂
                            spec_name = spec.find_element(By.CSS_SELECTOR, "div.ellipsis-content.single").text
                            
                            # 瑼Ｘ摨怠?
                            stock = spec.find_element(By.CSS_SELECTOR, "div.item-content.item-stock").text
                            stock = int(stock.strip())
                            
                            # ?脣??寞
                            price = spec.find_element(By.CSS_SELECTOR, "div.item-content.item-price").text
                            
                            # 瑼Ｘ?????
                            switch = spec.find_element(By.CSS_SELECTOR, "div.eds-switch")
                            is_open = "eds-switch--open" in switch.get_attribute("class")
                            is_disabled = "eds-switch--disabled" in switch.get_attribute("class")
                            
                            # ?澆??＊蝷箄?閮?- 璈怠?憿舐內
                            status_text = f"{spec_name} | 摨怠?: {stock} | {price} | ??: {'??' if is_open else '??'}{' (撌脩???' if is_disabled else ''}"
                            self.log_status(status_text)
                            
                            if stock > 0 and not is_disabled:
                                if not is_open:
                                    self.log_status("?閬?雿? ????")
                                    # 暺?????
                                    self.driver.execute_script("arguments[0].click();", switch)
                                    time.sleep(1)
                                    self.log_status("??撌脣???)
                                else:
                                    self.log_status("??迤撣?)
                            self.log_status("-" * 80)  # ??蝺?
                            
                        except Exception as e:
                            self.log_status(f"??閬??隤? {str(e)}")
                            continue
                
                except Exception as e:
                    self.log_status(f"???? #{card_index+1} ??隤? {str(e)}")
                    continue
                
        except Exception as e:
            self.log_status(f"瑼Ｘ????隤? {str(e)}")
            
    def start_adjustment(self):
        try:
            # ???蚓hrome
            self.start_chrome()
            
            if not self.driver:
                raise Exception("Chrome撽?蝔????仃??)
            
            # ?脣??嗅?URL嚗誑靘踹?蝥炎?交?西歲??
            initial_url = self.driver.current_url
            self.log_status(f"?嗅?URL: {initial_url}")
            
            # 蝑??頛
            self.log_status("蝑??頛...")
            time.sleep(3)
            
            # 瑼Ｘ?臬?閬??
            if "login" in self.driver.current_url.lower():
                self.log_status("?閬?伐?隢?汗?其葉???餃...")
                messagebox.showinfo("?餃?內", "隢?汗?其葉??摰??餃嚗敺??Ⅱ摰匱蝥?)
            
            # 蝣箔??冽迤蝣箇?蝬脤?
            target_url = self.url_entry.get().strip()
            if target_url not in self.driver.current_url:
                self.log_status(f"甇????啁璅雯?? {target_url}")
                self.driver.get(target_url)
                time.sleep(3)
            
            # ?脣??嗅?URL嚗??蝥歲??
            current_url = self.driver.current_url
            self.log_status(f"?格??URL: {current_url}")
            
            # 瑼Ｘ?臬撌脣蝺刻摩璅∪?
            already_in_edit_mode = False
            try:
                edit_mode_check = self.driver.execute_script("""
                    return {
                        hasEditElements: document.querySelectorAll('div.eds-switch').length > 0,
                        isEditUrl: window.location.href.includes('edit')
                    };
                """)
                
                if edit_mode_check and (edit_mode_check.get('hasEditElements', False) or edit_mode_check.get('isEditUrl', False)):
                    self.log_status("撌脣蝺刻摩璅∪?嚗?亥?????)
                    already_in_edit_mode = True
            except Exception as e:
                self.log_status(f"瑼Ｘ蝺刻摩璅∪???隤? {str(e)}")
            
            # 憒?銝蝺刻摩璅∪?嚗??楊頛舀???
            if not already_in_edit_mode:
                self.log_status("甇??交?楊頛舀???暑????..")
                
                # ?曉????
                edit_button = None
                try:
                    # 雿輻憭車?寞??岫?曉??
                    selectors = [
                        "button[data-v-2e4150da][data-v-212c4d7f].edit-button",
                        "button.edit-button",
                        "//button[contains(text(), '蝺刻摩?瘣餃?')]",
                        "//button[contains(@class, 'edit-button')]"
                    ]
                    
                    for selector in selectors:
                        try:
                            if selector.startswith("//"):
                                # XPath?豢???
                                elements = self.driver.find_elements(By.XPATH, selector)
                            else:
                                # CSS?豢???
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                
                            if elements:
                                # ?蕪?箏閬??甇?Ⅱ??????
                                for el in elements:
                                    if "蝺刻摩?瘣餃?" in el.text and el.is_displayed():
                                        edit_button = el
                                        self.log_status(f"???曉?楊頛舀???暑???? {el.text}")
                                        break
                                
                                if edit_button:
                                    break
                        except:
                            continue
                        
                    if not edit_button:
                        # 憒??曆??啁楊頛舀???雿輻?游祝擛??寞?
                        self.log_status("?岫雿輻?游祝擛??寞??交??...")
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            try:
                                if "蝺刻摩" in button.text and button.is_displayed():
                                    edit_button = button
                                    self.log_status(f"?曉?航?楊頛舀??? {button.text}")
                                    break
                            except:
                                continue
                    
                    if edit_button:
                        # 擃漁憿舐內?曉????
                        self.driver.execute_script("arguments[0].style.border='3px solid red';", edit_button)
                        
                        # 皛曉??唳???蝵?
                        self.log_status("皛曉??唳???蝵?..")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", edit_button)
                        time.sleep(1)  # 蝑?皛曉?摰?
                        
                        # 雿輻???芋?祆?祕??曌???
                        self.log_status("璅⊥?祕皛?暺?...")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(edit_button)  # 蝘餃?皛??啣?蝝?
                        actions.pause(0.5)  # ?怠??嚗芋?砌犖憿???
                        actions.click()     # 暺???
                        actions.perform()   # ?瑁?????
                        
                        self.log_status("??撌脤??楊頛舀???暑????)
                        
                        # 蝑?敶閬??箇
                        self.log_status("蝑??航?箇???箄?蝒?..")
                        time.sleep(2)
                        
                        # 瑼Ｘ?臬???箄?蝒?
                        modal_found = False
                        modal_selectors = ['.eds-modal__content', '.shopee-modal__container', '[role="dialog"]', '.eds-modal__box']
                        
                        for selector in modal_selectors:
                            modal_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if modal_elements and len(modal_elements) > 0 and modal_elements[0].is_displayed():
                                modal = modal_elements[0]
                                modal_found = True
                                self.log_status(f"?曉敶閬?: {selector}")
                                
                                # ?脣?敶???
                                modal_text = modal.text
                                self.log_status(f"敶閬??批捆: {modal_text[:100]}")
                                
                                # ?寞????釣??蝒?
                                is_notice_modal = False
                                try:
                                    modal_title = modal.find_element(By.CSS_SELECTOR, ".eds-modal__title")
                                    if modal_title and "瘜冽?" in modal_title.text:
                                        is_notice_modal = True
                                        self.log_status("瑼Ｘ葫?啜釣??蝒?雿輻?寞????孵?")
                                except:
                                    pass
                                
                                # 憒???瘜冽?"敶?嚗蝙?典??冽瘜???
                                    self.log_status("?? 雿輻撠?寞????釣??蝒?..")
                                    if self.handle_notice_modal(modal):
                                        self.log_status("??瘜冽?敶?撌脫?????)
                                        time.sleep(3)  # 蝑???摰?敺????
                                        continue
                                    else:
                                        self.log_status("??瘜冽?敶???憭望?嚗?閰血隞瘜?)

                                # 撠蝣箄??? - ?炎?亦摰???
                                confirm_button = None
                                
                                    # ?湔雿輻JavaScript?交銝阡?????
                                    self.log_status("雿輻?湔JavaScript?寞????釣??蝒?)
                                    
                                    js_result = self.driver.execute_script("""
                                        // ?寞?1: 雿輻蝎曄Ⅱ?SS?豢???
                                        let btn = document.querySelector('.eds-modal__footer-buttons .eds-button--primary');
                                        console.log('?寞?1?曉??:', btn);
                                        
                                        // ?寞?2: ?交??蜓閬????豢?蝣箄???
                                        if (!btn) {
                                            const primaryButtons = document.querySelectorAll('button.eds-button--primary');
                                            for (const button of primaryButtons) {
                                                if (button.innerText.includes('蝣箄?')) {
                                                    btn = button;
                                                    console.log('?寞?2?曉??:', btn);
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        // ?寞?3: ?交???蝒葉????
                                        if (!btn) {
                                            const modalButtons = document.querySelectorAll('.eds-modal__box button');
                                            for (const button of modalButtons) {
                                                if (button.innerText.includes('蝣箄?')) {
                                                    btn = button;
                                                    console.log('?寞?3?曉??:', btn);
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        // ?寞?4: ?撖祇??瘜??交?????
                                        if (!btn) {
                                            const allButtons = document.querySelectorAll('button');
                                            for (const button of allButtons) {
                                                if (button.innerText.includes('蝣箄?')) {
                                                    btn = button;
                                                    console.log('?寞?4?曉??:', btn);
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        if (btn) {
                                            // 閮???靽⊥
                                            console.log('?曉蝣箄???:', btn);
                                            console.log('????:', btn.innerText);
                                            console.log('??憿?:', btn.className);
                                            console.log('??HTML:', btn.outerHTML);
                                            
                                            // 璅???
                                            btn.style.border = '5px solid red';
                                            
                                            // ?岫暺?????蝔格瘜?
                                            try {
                                                // ?寞?1: ?湔暺?
                                                btn.click();
                                                console.log('?寞?1暺???');
                                            } catch(e) {
                                                console.log('?寞?1暺?憭望?:', e);
                                                
                                                try {
                                                    // ?寞?2: 雿輻MouseEvent
                                                    btn.dispatchEvent(new MouseEvent('click', {
                                                        bubbles: true,
                                                        cancelable: true,
                                                        view: window
                                                    }));
                                                    console.log('?寞?2暺???');
                                                } catch(e) {
                                                    console.log('?寞?2暺?憭望?:', e);
                                                }
                                            }
                                            
                                            return {
                                                success: true,
                                                message: '撌脤?JavaScript?湔暺???',
                                                buttonText: btn.innerText,
                                                buttonClass: btn.className
                                            };
                                        }
                                        
                                        return {
                                            success: false,
                                            message: '?芣?啁Ⅱ隤???
                                        };
                                    """)
                                    
                                    if js_result and js_result.get('success', False):
                                        self.log_status(f"??JavaScript?湔暺?????: {js_result.get('message')}")
                                        self.log_status(f"????: {js_result.get('buttonText')}, 憿?: {js_result.get('buttonClass')}")
                                        time.sleep(3)  # 蝑???摰?
                                    else:
                                        self.log_status("? JavaScript?湔暺?憭望?嚗?閰虫?銝?瘜?)
                                        
                                        # 雿輻XPath?湔?暹???
                                        self.log_status("雿輻XPath撠??")
                                        try:
                                            # ?岫憭車XPath摰?蝣箄???
                                            xpath_patterns = [
                                                "//div[contains(@class, 'eds-modal__footer')]//button[contains(@class, 'eds-button--primary')]",
                                                "//div[contains(@class, 'eds-modal__box')]//button[contains(text(), '蝣箄?')]",
                                                "//button[contains(@class, 'eds-button--primary') and contains(text(), '蝣箄?')]",
                                                "//div[contains(@class, 'eds-modal')]//button[contains(text(), '蝣箄?')]",
                                                "//button[contains(text(), '蝣箄?')]"
                                            ]
                                            
                                            for xpath in xpath_patterns:
                                                buttons = self.driver.find_elements(By.XPATH, xpath)
                                                if buttons and len(buttons) > 0 and buttons[0].is_displayed():
                                                    confirm_button = buttons[0]
                                                    self.log_status(f"??雿輻XPath?曉蝣箄???: {confirm_button.text}")
                                                    
                                                    # ?湔雿輻3蝔格瘜???
                                                    # ?寞?1: ?瑁?JS暺?
                                                    self.driver.execute_script("arguments[0].click();", confirm_button)
                                                    self.log_status("撌脣銵S暺?")
                                                    time.sleep(1)
                                                    
                                                    # ?寞?2: 雿輻摨扳?暺?
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
                                                    
                                                    self.log_status(f"雿輻摨扳?暺?: x={center_x}, y={center_y}")
                                                    action = ActionChains(self.driver)
                                                    action.move_to_element_with_offset(confirm_button, 0, 0)
                                                    action.move_by_offset(5, 5)  # 蝘餃??唳??葉敹?敺桀??喃?
                                                    action.click()
                                                    action.perform()
                                                    
                                                    # ?寞?3: 雿輻??暺?
                                                    try:
                                                        confirm_button.click()
                                                        self.log_status("撌脖蝙?典????瘜?)
                                                    except Exception as e:
                                                        self.log_status(f"??暺?憭望?: {str(e)}")
                                                    
                                                    break
                                            
                                            # 瑼Ｘ?臬??敶閬?
                                            time.sleep(3)
                                            modal_still_visible = False
                                            for selector in modal_selectors:
                                                modal_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                                if modal_elements and len(modal_elements) > 0 and modal_elements[0].is_displayed():
                                                    modal_still_visible = True
                                                    break
                                            
                                            if modal_still_visible:
                                                self.log_status("霅血?嚗?蝒??嗅??剁??岫?湔??摰?)
                                                
                                                # ?湔?岫??敶????
                                                try:
                                                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".eds-modal__close")
                                                    if close_buttons and len(close_buttons) > 0 and close_buttons[0].is_displayed():
                                                        close_buttons[0].click()
                                                        self.log_status("暺?敶???????)
                                                except Exception as e:
                                                    self.log_status(f"暺?????憭望?: {str(e)}")
                                                
                                                # 憒?隞摮嚗岷??嗆?????
                                                if messagebox.askyesno("敶?暺???", 
                                                                    "?⊥??芸?暺?敶?銝剔?蝣箄????n\n隢????Ⅱ隤????嗅?暺???匱蝥?):
                                                    self.log_status("?冽蝣箄?撌脫???????)
                                            else:
                                                self.log_status("??敶?撌脤???暺???")
                                        except Exception as e:
                                            self.log_status(f"XPath??暺?憭望?: {str(e)}")
                                    
                                    # 頝喲?敺????????撌脩??岫鈭??瘜?
                                    confirm_button = None
                                    modal_found = False
                                    continue
                                
                                # ???釣??蝒??孵??豢???
                                specific_selectors = [
                                    ".eds-modal__footer-buttons .eds-button--primary",
                                    ".eds-modal__footer .eds-button--primary",
                                    ".eds-modal__box .eds-button--primary"
                                ]
                                
                                for specific_selector in specific_selectors:
                                    try:
                                        buttons = self.driver.find_elements(By.CSS_SELECTOR, specific_selector)
                                        for button in buttons:
                                            if button.is_displayed() and "蝣箄?" in button.text:
                                                self.log_status(f"?曉?釣??蝒葉?Ⅱ隤??? {button.text}")
                                                confirm_button = button
                                                break
                                        if confirm_button:
                                            break
                                    except Exception as e:
                                        self.log_status(f"?交?孵?????? {str(e)}")
                                
                                # 銝?祆?暹撘?
                                if not confirm_button:
                                    # ?岫雿輻?蝎曄Ⅱ??
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
                                                if button.is_displayed() and "蝣箄?" in button.text:
                                                    self.log_status(f"?曉蝎曄Ⅱ?寥??Ⅱ隤??? {button.text}")
                                                    confirm_button = button
                                                    break
                                            if confirm_button:
                                                break
                                        except Exception as e:
                                            self.log_status(f"?交蝎曄Ⅱ????? {str(e)}")
                                
                                # 憒?隞銝嚗?閰行撖祇???暹撘?
                                if not confirm_button:
                                    # ?岫?交?????
                                    button_elements = self.driver.find_elements(By.TAG_NAME, "button")
                                    
                                    # ?芸??交????Ⅱ隤?????
                                    for button in button_elements:
                                        if not button.is_displayed():
                                            continue
                                        
                                        button_text = button.text
                                        self.log_status(f"?潛??: {button_text}")
                                        if any(text in button_text for text in ["蝣箄?", "蝣箏?", "蝜潛?", "??]):
                                            confirm_button = button
                                            break
                                
                                # 憒??曉??嚗蝙?典?蝔格瘜???
                                if confirm_button:
                                    # 閮??????寒TML隞乩噶隤輯岫
                                    try:
                                        button_html = self.driver.execute_script("return arguments[0].outerHTML;", confirm_button)
                                        self.log_status(f"??HTML: {button_html}")
                                    except:
                                        pass
                                    
                                    # 擃漁憿舐內?曉????
                                    self.driver.execute_script("arguments[0].style.border='5px solid red';", confirm_button)
                                    
                                    # 皛曉??唳???蝵?
                                    self.log_status("皛曉??唳???蝵?..")
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", confirm_button)
                                    time.sleep(1)  # 蝑?皛曉?摰?
                                    
                                    # ?脣?????冽閮?
                                    button_text = confirm_button.text
                                    
                                    # 憒??胯釣??蝒?雿輻?渡移蝣箇?暺??寞?
                                        self.log_status(f"雿輻?寞??寞?暺??釣??蝒??button_text}????..")
                                        
                                        # ??閰行????瘜?- 璅⊥Tab敺nter
                                        try:
                                            # ?潮scape?萄?皜隞颱??航?暺?
                                            actions = ActionChains(self.driver)
                                            actions.send_keys(Keys.ESCAPE)
                                            actions.perform()
                                            self.log_status("撌脩?scape??)
                                            time.sleep(0.5)
                                            
                                            # ?潮ab?蛛?霈暺宏?蝣箄???
                                            for i in range(3):  # ?岫?憭??甈﹗ab
                                                actions = ActionChains(self.driver)
                                                actions.send_keys(Keys.TAB)
                                                actions.perform()
                                                self.log_status(f"撌脩?ab??{i+1} 甈?)
                                                time.sleep(0.5)
                                            
                                            # ?潮nter?萇Ⅱ隤?
                                            actions = ActionChains(self.driver)
                                            actions.send_keys(Keys.ENTER)
                                            actions.perform()
                                            self.log_status("撌脩?nter??)
                                            time.sleep(1)
                                            
                                            # 瑼Ｘ敶??臬????
                                            modal_still_exists = False
                                            for selector in modal_selectors:
                                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                                if elements and len(elements) > 0 and elements[0].is_displayed():
                                                    modal_still_exists = True
                                                    break
                                            
                                            if not modal_still_exists:
                                                self.log_status("??雿輻?萇??????敶?")
                                                return
                                            else:
                                                self.log_status("?萇???芾??敶?嚗?閰血隞瘜?)
                                        except Exception as e:
                                            self.log_status(f"?萇璅⊥憭望?: {str(e)}")
                                        
                                        # 憒??萇??憭望?嚗?閰行????elenium?寞?
                                        try:
                                            # ?湔雿輻??click嚗?瘛餃?隞颱?ActionChains
                                            confirm_button.click()
                                            self.log_status("雿輻??click()?寞?")
                                            
                                            # 蝑?銝銝??臬瘨仃
                                            time.sleep(2)
                                            modal_still_exists = False
                                            for selector in modal_selectors:
                                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                                if elements and len(elements) > 0 and elements[0].is_displayed():
                                                    modal_still_exists = True
                                                    break
                                            
                                            if not modal_still_exists:
                                                self.log_status("??雿輻??click()????敶?")
                                                return
                                        except Exception as e:
                                            self.log_status(f"??click()憭望?: {str(e)}")
                                        
                                        # ?敺?閰阡?pure JavaScript暺?
                                        try:
                                            # ?岫??pure JavaScript?湔暺?
                                            self.driver.execute_script("""
                                                // ?交??Ⅱ隤???
                                                const primaryButtons = document.querySelectorAll('button.eds-button--primary');
                                                for (let btn of primaryButtons) {
                                                  if (btn.innerText.includes('蝣箄?')) {
                                                    console.log('?曉蝣箄???:', btn);
                                                    btn.click();
                                                    return true;
                                                  }
                                                }
                                                
                                                // ?岫??Enter??
                                                document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {
                                                  key: 'Enter',
                                                  code: 'Enter',
                                                  keyCode: 13,
                                                  which: 13,
                                                  bubbles: true
                                                }));
                                                
                                                return false;
                                            """)
                                            self.log_status("撌脣銵avaScript暺?")
                                        except Exception as e:
                                            self.log_status(f"JavaScript暺?憭望?: {str(e)}")
                                            
                                        # ???摮???蝵?
                                        try:
                                            screenshot_path = "modal_button.png"
                                            self.driver.save_screenshot(screenshot_path)
                                            self.log_status(f"撌脖?摮?蝒? {screenshot_path}")
                                        except Exception as e:
                                            self.log_status(f"靽??芸?憭望?: {str(e)}")
                                        
                                        # ?寞?1: ?湔雿輻 JavaScript 暺?
                                        try:
                                            self.driver.execute_script("""
                                                arguments[0].dispatchEvent(new MouseEvent('click', {
                                                    'view': window,
                                                    'bubbles': true,
                                                    'cancelable': true
                                                }));
                                            """, confirm_button)
                                            self.log_status("雿輻 JavaScript MouseEvent 暺?")
                                            time.sleep(1)
                                        except Exception as e:
                                            self.log_status(f"JavaScript 暺?憭望?: {str(e)}")
                                        
                                        # ?寞?2: 雿輻 JavaScript ?瑁?????click ?寞?
                                        try:
                                            self.driver.execute_script("arguments[0].click();", confirm_button)
                                            self.log_status("雿輻 JavaScript click() ?寞?暺?")
                                            time.sleep(1)
                                        except Exception as e:
                                            self.log_status(f"JavaScript click() ?寞?憭望?: {str(e)}")
                                        
                                        # ?寞?3: 雿輻 ActionChains 暺?
                                        try:
                                            action = ActionChains(self.driver)
                                            action.move_to_element(confirm_button).pause(0.5).click().perform()
                                            self.log_status("雿輻 ActionChains 暺?")
                                            time.sleep(1)
                                        except Exception as e:
                                            self.log_status(f"ActionChains 暺?憭望?: {str(e)}")
                                        
                                        # ?寞?4: 雿輻摨扳?暺?
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
                                            self.log_status(f"雿輻摨扳?暺? ({center_x}, {center_y})")
                                        except Exception as e:
                                            self.log_status(f"摨扳?暺?憭望?: {str(e)}")
                                        
                                        # ?寞?5: 雿輻send_keys璅⊥Enter??
                                        try:
                                            confirm_button.send_keys("\n")
                                            self.log_status("雿輻Enter?菜芋?祇???)
                                        except Exception as e:
                                            self.log_status(f"Enter?菜芋?祇??仃?? {str(e)}")
                                    else:
                                        # ?岫雿輻憭車?寞?蝣箔?暺???
                                        self.log_status(f"?岫暺??button_text}????(雿輻憭車?寞?)...")
                                        
                                        # ?寞?1嚗?乩蝙?牢lick()?寞?
                                        try:
                                            confirm_button.click()
                                            self.log_status("?寞?1嚗蝙?牠lement.click()?寞?暺?")
                                        except Exception as e:
                                            self.log_status(f"?寞?1憭望?: {str(e)}")
                                            
                                            # ?寞?2嚗蝙?沅avaScript暺?
                                            try:
                                                self.driver.execute_script("arguments[0].click();", confirm_button)
                                                self.log_status("?寞?2嚗蝙?沅avaScript暺?")
                                            except Exception as e:
                                                self.log_status(f"?寞?2憭望?: {str(e)}")
                                                
                                                # ?寞?3嚗蝙?杗ctionChains璅⊥鈭粹?暺?
                                                try:
                                                    actions = ActionChains(self.driver)
                                                    actions.move_to_element(confirm_button)
                                                    actions.pause(0.5)
                                                    actions.click()
                                                    actions.perform()
                                                    self.log_status("?寞?3嚗蝙?杗ctionChains暺?")
                                                except Exception as e:
                                                    self.log_status(f"?寞?3憭望?: {str(e)}")
                                                    
                                                    # ?寞?4嚗蝙?冽蝎曄Ⅱ??璅???
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
                                                        
                                                        # 閮???銝剖?暺?
                                                        center_x = rect['left'] + rect['width'] / 2
                                                        center_y = rect['top'] + rect['height'] / 2
                                                        
                                                        # 雿輻??暺?
                                                        actions = ActionChains(self.driver)
                                                        actions.move_by_offset(center_x, center_y)
                                                        actions.click()
                                                        actions.perform()
                                                        self.log_status("?寞?4嚗蝙?函移蝣箏?璅???)
                                                    except Exception as e:
                                                        self.log_status(f"?寞?4憭望?: {str(e)}")
                                    
                                    self.log_status(f"撌脣?閰阡????箄?蝒??button_text}????)
                                    
                                    # 蝑?蝣箄???摰?敺炎?交?阡???蝒?
                                    time.sleep(3)
                                    
                                    # 瑼Ｘ?臬??敶?
                                    still_has_modal = False
                                    for selector in modal_selectors:
                                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                        if elements and len(elements) > 0 and elements[0].is_displayed():
                                            still_has_modal = True
                                            self.log_status(f"霅血?嚗?蝒??嗅??剁?暺??航?芣???)
                                            break
                                    
                                    if not still_has_modal:
                                        self.log_status("??敶?撌脤???暺???")
                                else:
                                    self.log_status("?? ?曉敶閬?雿瘜?啣暺?????)
                                    
                                    # ?芸?靽?
                                    try:
                                        screenshot_path = "modal_debug.png"
                                        self.driver.save_screenshot(screenshot_path)
                                        self.log_status(f"撌脖?摮?蝒? {screenshot_path}")
                                    except Exception as e:
                                        self.log_status(f"靽??芸?憭望?: {str(e)}")
                                    
                                    # 閰Ｗ??冽?臬????
                                    if messagebox.askyesno("?曆??啁Ⅱ隤???, 
                                                           "?曉敶閬?雿瘜?啁Ⅱ隤??n\n隢????Ⅱ隤????嗅?暺???匱蝥?):
                                        self.log_status("?冽蝣箄?撌脫???????)
                                
                                # 蝑?敶???摰?
                                self.log_status("蝑?敶???摰?...")
                                time.sleep(3)
                                
                                break  # ?曉銝西???銝??蝒?頝喳敺芰
                        
                        # 憒?瘝??曉敶?嚗??隤?
                        if not modal_found:
                            self.log_status("?芣炎皜砍敶閬?")
                        
                        # 瑼Ｘ?臬?洵鈭?蝒?
                        self.log_status("瑼Ｘ?臬?隞?蝒?..")
                        time.sleep(1)
                        
                        # ?瑼Ｘ?臬??蝒?
                        second_modal_found = False
                        for selector in modal_selectors:
                            modal_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if modal_elements and len(modal_elements) > 0 and modal_elements[0].is_displayed():
                                modal = modal_elements[0]
                                second_modal_found = True
                                self.log_status(f"?曉蝚砌????箄?蝒? {selector}")
                                
                                # ?脣?敶???
                                modal_text = modal.text
                                self.log_status(f"蝚砌????箄?蝒摰? {modal_text[:100]}")
                                
                                # 撠蝣箄???
                                confirm_button = None
                                button_elements = modal.find_elements(By.TAG_NAME, "button")
                                
                                # ?芸??交????Ⅱ隤Ⅱ摰?????
                                for button in button_elements:
                                    if not button.is_displayed():
                                        continue
                                    
                                    button_text = button.text
                                    if any(text in button_text for text in ["蝣箄?", "蝣箏?", "蝜潛?", "??]):
                                        confirm_button = button
                                        break
                                
                                # 憒?瘝?啁摰?摮???嚗?閰行?曆蜓閬?雿???
                                if not confirm_button:
                                    primary_buttons = modal.find_elements(By.CSS_SELECTOR, "button.eds-button--primary")
                                    if primary_buttons and len(primary_buttons) > 0 and primary_buttons[0].is_displayed():
                                        confirm_button = primary_buttons[0]
                                
                                # 憒?隞瘝?堆?雿輻蝚砌??閬???
                                if not confirm_button and len(button_elements) > 0:
                                    for button in button_elements:
                                        if button.is_displayed():
                                            confirm_button = button
                                            break
                                
                                # 憒??曉??嚗蝙?杗ctionChains璅⊥?祕暺?
                                if confirm_button:
                                    # ?脣?????冽閮?
                                    button_text = confirm_button.text
                                    
                                    # 擃漁憿舐內?曉????
                                    self.driver.execute_script("arguments[0].style.border='3px solid red';", confirm_button)
                                    
                                    # 皛曉??唳???蝵?
                                    self.log_status("皛曉??唳???蝵?..")
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", confirm_button)
                                    time.sleep(1)  # 蝑?皛曉?摰?
                                    
                                    # 雿輻???芋?祆?祕??曌???
                                    self.log_status(f"璅⊥?祕皛?暺?蝚砌???蝒??button_text}????..")
                                    actions = ActionChains(self.driver)
                                    actions.move_to_element(confirm_button)  # 蝘餃?皛??啣?蝝?
                                    actions.pause(0.5)  # ?怠??嚗芋?砌犖憿???
                                    actions.click()     # 暺???
                                    actions.perform()   # ?瑁?????
                                    
                                    self.log_status(f"??撌脤??洵鈭??箄?蝒??button_text}????)
                                else:
                                    self.log_status("?? ?曉蝚砌????箄?蝒??⊥??曉?舫?????")
                                
                                # 蝑?敶???摰?
                                self.log_status("蝑?敶???摰?...")
                                time.sleep(3)
                                
                                break  # ?曉銝西???蝚砌???蝒?頝喳敺芰
                        
                        # 蝑??頛
                        self.log_status("蝑??摰頛...")
                        time.sleep(5)  # 憓?蝑???蝣箔??摰頛
                        
                        # 瑼Ｘ?嗅?URL嚗??臬頝喳?
                        current_url_after_click = self.driver.current_url
                        if current_url_after_click != current_url:
                            self.log_status(f"?? ?URL撌脰??? {current_url_after_click}")
                            
                            # 瑼Ｘ?臬餈??啣?銵券???
                            if "list" in current_url_after_click.lower():
                                self.log_status("?菜葫?啣歇餈??”?嚗?賣甇?虜銵??)
                                
                                # 閰Ｗ??冽?臬?撠?啁璅???
                                if messagebox.askyesno("?撌脰歲頧?, 
                                                     "瑼Ｘ葫?圈??Ｗ歇餈??”?嚗?賣??唾???撌脣??n\n" +
                                                     "?典?????憪??Ｖ蒂?活?岫??"):
                                    self.log_status("甇?餈????...")
                                    self.driver.get(current_url)
                                    time.sleep(3)
                                    
                                    # 閰Ｗ??冽??暺?
                                    if messagebox.askyesno("????", "隢????楊頛舀???暑??????摰?敺???匱蝥?):
                                        self.log_status("?冽蝣箄?撌脫?????雿?)
                                        time.sleep(2)
                                else:
                                    self.log_status("?冽?豢??函???Ｙ匱蝥?)
                                    # 雿輻?嗅???岫????
                                    try:
                                        self.check_and_process_items()
                                        return
                                    except Exception as e:
                                        self.log_status(f"?典?銵券??Ｚ??????粹: {str(e)}")
                                        # 蝜潛??瑁?隞亙?閰血隞瘜?
                        else:
                            self.log_status("???URL靽?銝?嚗匱蝥???)
                    else:
                        self.log_status("???⊥??曉?楊頛舀???暑????)
                        
                        # ?芸?靽?
                        try:
                            screenshot_path = "debug_screenshot.png"
                            self.driver.save_screenshot(screenshot_path)
                            self.log_status(f"撌脖?摮???Ｘ? {screenshot_path}")
                        except Exception as e:
                            self.log_status(f"?芸?靽?憭望?: {str(e)}")
                        
                        # 閰Ｗ??冽????
                        if messagebox.askyesno("?曆??唳???, 
                                              "?⊥??芸??曉?楊頛舀???暑???n\n隢????府??嚗?雿???暺???匱蝥?):
                            self.log_status("?冽蝣箄?撌脫???????)
                            time.sleep(3)  # 蝯衣?嗆???雿?
                
                except Exception as e:
                    self.log_status(f"?岫暺?????隤? {str(e)}")
                    
                    # ???????賊?
                    if messagebox.askyesno("???航炊", 
                                          f"?芸?暺???隤? {str(e)}\n\n?臬閬?閰行???雿?"):
                        self.log_status("隢???雿?暺?蝣箄?")
                        if messagebox.askyesno("蝣箄?", "?典歇摰?????鈭?嚗?):
                            self.log_status("?冽蝣箄?撌脫?????雿?)
                            time.sleep(2)  # 蝯衣頂蝯望?????
            
            # 瑼Ｘ?臬撌脣蝺刻摩璅∪?
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
                self.log_status(f"瑼Ｘ蝺刻摩璅∪???隤? {str(e)}")
            
            if edit_mode_confirmed or already_in_edit_mode:
                self.log_status("撌脫??脣蝺刻摩璅∪?嚗?憪?????..")
                
                # 蝑??摰頛???蝝?
                self.log_status("蝑??摰頛?????閬...")
                wait_start = time.time()
                max_wait_time = 15  # ?憭?敺?5蝘?
                
                # ???????澆?蝝?頛??
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
                        self.log_status(f"???撌脣??刻??? {elements_loaded.get('productCount', 0)} ???? {elements_loaded.get('specCount', 0)} ???? {elements_loaded.get('switchCount', 0)} ????)
                        break
                    
                    # 瘥?蝘＊蝷箔?甈∟??亦???
                    elapsed = time.time() - wait_start
                    if int(elapsed) % 2 == 0:
                        self.log_status(f"蝑??頛銝?.. ({int(elapsed)}蝘? 撌脫??{elements_loaded.get('productCount', 0)} ???? {elements_loaded.get('specCount', 0)} ????)
                    
                    time.sleep(1)
                
                # ??????
                self.check_and_process_items()
            else:
                self.log_status("?? ?⊥?蝣箄??臬撌脤脣蝺刻摩璅∪?")
                
                # ?岫???嗅??
                if messagebox.askyesno("蝣箄?", "?⊥?蝣箄??臬撌脤脣蝺刻摩璅∪??n\n?臬隞??岫???嗅??????"):
                    self.log_status("?冽?豢?蝜潛????嗅??????)
                    self.check_and_process_items()
        
        except Exception as e:
            self.log_status(f"????銝剔?隤? {str(e)}")
            import traceback
            self.log_status(traceback.format_exc())
    
    def analyze_page_structure(self):
        """???嗅??蝯?"""
        try:
            if not self.driver:
                # ???蚓hrome
                self.start_chrome()
                
            if not self.driver:
                messagebox.showerror("?航炊", "?⊥????蚓hrome?汗??)
                return
                
            self.log_status("\n===== ?????蝯? =====")
            
            # ?萄遣????
            analyzer = ShopeePageAnalyzer(self.driver)
            
            # ???URL
            self.log_status(f"?嗅?URL: {self.driver.current_url}")
            self.root.update_idletasks()
            
            # ?岫雿輻XPath?豢???
            self.log_status("\n1. ?岫雿輻XPath?豢???..")
            xpath_products = analyzer.find_products_by_xpath()
            
            if "error" in xpath_products:
                self.log_status(f"  XPath?豢??函?隤? {xpath_products['error']}")
            else:
                self.log_status(f"  雿輻XPath?豢??冽??{xpath_products.get('product_count', 0)} ???? {xpath_products.get('spec_count', 0)} ????)
                
                # 憿舐內?曉??縑??
                for i, product in enumerate(xpath_products.get('products', [])[:5]):  # 憿舐內????
                    self.log_status(f"\n  ?? #{i+1}: {product.get('name', '?芰?迂')}")
                    
                    # 憿舐內閬靽⊥
                    for j, spec in enumerate(product.get('specs', [])[:3]):  # 憿舐內??????
                        spec_info = f"    閬 #{j+1}: {spec.get('name', '?芰閬')}"
                        
                        # 瘛餃?摨怠???潔縑?荔?憒???
                        if spec.get('stock'):
                            spec_info += f" | 摨怠?: {spec.get('stock')}"
                        if spec.get('price'):
                            spec_info += f" | ?寞: {spec.get('price')}"
                        if spec.get('status'):
                            spec_info += f" | ??? {spec.get('status')}"
                            if spec.get('disabled'):
                                spec_info += " (撌脩???"
                        
                        self.log_status(spec_info)
                    
                    # ?湔UI
                    self.root.update_idletasks()
                
                # 憿舐內靘?蝯梯?
                self.log_status("\n  靘?蝯梯?:")
                self.log_status(f"    Selenium?曉: {xpath_products.get('selenium_product_count', 0)} ???? {xpath_products.get('selenium_spec_count', 0)} ????)
                self.log_status(f"    JavaScript?曉: {xpath_products.get('js_product_count', 0)} ???? {xpath_products.get('js_spec_count', 0)} ????)
            
            self.root.update_idletasks()
            
            # 撠????
            self.log_status("\n2. ?岫撠????...")
            product_elements = analyzer.find_product_elements()
            
            if isinstance(product_elements, dict) and "error" in product_elements:
                self.log_status(f"  ?航炊: {product_elements['error']}")
            elif isinstance(product_elements, dict) and "count" in product_elements:
                self.log_status(f"  ?曉 {product_elements['count']} ????雿輻?豢??? {product_elements.get('selector', '?芰')}")
                self.log_status(f"  蝭???: {json.dumps(product_elements.get('sample', {}), ensure_ascii=False, indent=2)}")
            else:
                self.log_status(f"  ?曉?航????蝝? {len(product_elements) if isinstance(product_elements, list) else 0} ??)
            
            self.root.update_idletasks()
            
            # 瑼Ｘ?撠?孵?
            self.log_status("\n3. 瑼Ｘ?撠?孵?...")
            
            # 瑼Ｘ??
            pagination = analyzer.find_pagination()
            if pagination.get("found", False):
                self.log_status(f"  瑼Ｘ葫?啣???塚??嗅?蝚?{pagination.get('currentPage', '1')} ????{pagination.get('totalPages', '1')} ??)
                has_next = pagination.get("hasNextPage", False)
                self.log_status(f"  ?臬??銝?? {'?? if has_next else '??}")
            else:
                self.log_status("  ?芣炎皜砍璅????批")
            
            self.root.update_idletasks()
            
            # 瑼Ｘ?⊿?皛曉?
            scroll_info = analyzer.check_infinite_scroll()
            if scroll_info.get("mayUseInfiniteScroll", False):
                self.log_status("  瑼Ｘ葫?圈??Ｗ?賭蝙?函?遝??頛?)
                if scroll_info.get("heightChanged", False):
                    before = scroll_info.get("initialHeight", 0)
                    after = scroll_info.get("newHeight", 0)
                    self.log_status(f"  皛曉????ａ?摨? {before}嚗遝??: {after}嚗??? {after - before}")
                
                if scroll_info.get("hasLazyLoadIndicators", False):
                    self.log_status("  瑼Ｘ葫?唳???內?典?蝝?)
            else:
                self.log_status("  ?芣炎皜砍?⊿?皛曉??孵噩")
            
            self.root.update_idletasks()
            
            # ????閰喟敦靽⊥
            self.log_status("\n4. ????閰喟敦靽⊥...")
            products = analyzer.extract_all_products()
            
            if isinstance(products, dict) and "error" in products:
                self.log_status(f"  ?航炊: {products['error']}")
            elif isinstance(products, list):
                self.log_status(f"  ???? {len(products)} ????)
                
                # 憿舐內????????
                for i, product in enumerate(products[:3]):
                    self.log_status(f"\n  ?? #{i+1}: {product.get('name', '?芰?迂')}")
                    self.log_status(f"  閬?賊?: {len(product.get('specs', []))}")
                    
                    # 憿舐內蝚砌????潛?閰喟敦靽⊥
                    if product.get('specs') and len(product.get('specs')) > 0:
                        spec = product['specs'][0]
                        self.log_status(f"  擐??? {spec.get('name', '?芰閬')}")
                        self.log_status(f"  摨怠?: {spec.get('stock', '?芰')}")
                        self.log_status(f"  ?寞: {spec.get('price', '?芰')}")
                        self.log_status(f"  ????? {'??' if spec.get('isOpen') else '??'}{' (撌脩???' if spec.get('isDisabled') else ''}")
                    
                    # ?湔UI
                    self.root.update_idletasks()
            
            # ???蝯?
            self.log_status("\n5. ???DOM蝯?...")
            structure = analyzer.get_page_structure()
            
            if isinstance(structure, dict) and "error" in structure:
                self.log_status(f"  ?航炊: {structure['error']}")
            else:
                self.log_status(f"  ?????蝯?嚗???{len(structure)} ?蜓閬?蝝?)
                
                # 憿舐內?銝剝?閬?HTML蝯?
                self.log_status("\n6. ?銝剔?????:")
                
                # 雿輻JavaScript?交?銝剔????
                important_elements = self.driver.execute_script("""
                    let result = {
                        buttons: [],
                        forms: [],
                        tables: [],
                        productContainers: [],
                        switches: []
                    };
                    
                    // ?曉?????
                    document.querySelectorAll('button').forEach(btn => {
                        if (btn.innerText) {
                            result.buttons.push({
                                text: btn.innerText.slice(0, 30),
                                className: btn.className,
                                disabled: btn.disabled
                            });
                        }
                    });
                    
                    // ?曉??”??
                    document.querySelectorAll('form').forEach(form => {
                        result.forms.push({
                            id: form.id,
                            action: form.action,
                            method: form.method,
                            elements: form.elements.length
                        });
                    });
                    
                    // ?曉??”??
                    document.querySelectorAll('table').forEach(table => {
                        result.tables.push({
                            rows: table.rows.length,
                            className: table.className
                        });
                    });
                    
                    // ?曉?航???捆??
                    document.querySelectorAll('div').forEach(div => {
                        if (div.innerText.includes('??') || 
                            div.innerText.includes('摨怠?') || 
                            div.innerText.includes('?寞')) {
                            if (result.productContainers.length < 5) {
                                result.productContainers.push({
                                    className: div.className,
                                    textPreview: div.innerText.slice(0, 50),
                                    childNodes: div.childNodes.length
                                });
                            }
                        }
                    });
                    
                    // ?曉?????
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
                
                # 憿舐內??
                self.log_status(f"  ?曉 {len(important_elements.get('buttons', []))} ????)
                for i, btn in enumerate(important_elements.get('buttons', [])[:5]):
                    self.log_status(f"    ?? #{i+1}: {btn.get('text')} | ??? {'蝳' if btn.get('disabled') else '?'}")
                
                # 憿舐內銵典
                self.log_status(f"  ?曉 {len(important_elements.get('forms', []))} ?”??)
                
                # 憿舐內?航???捆??
                self.log_status(f"  ?曉 {len(important_elements.get('productContainers', []))} ??賜???摰孵")
                for i, container in enumerate(important_elements.get('productContainers', [])):
                    self.log_status(f"    摰孵 #{i+1}: {container.get('textPreview')}...")
                
                # 憿舐內??靽⊥
                switches = important_elements.get('switches', [])
                self.log_status(f"  ?曉 {len(switches)} ????)
                
                # 蝯梯??????
                open_switches = sum(1 for sw in switches if sw.get('isOpen', False))
                disabled_switches = sum(1 for sw in switches if sw.get('isDisabled', False))
                visible_switches = sum(1 for sw in switches if sw.get('isVisible', False))
                
                self.log_status(f"    ?????? {open_switches} ??)
                self.log_status(f"    蝳???? {disabled_switches} ??)
                self.log_status(f"    ?航????? {visible_switches} ??)
                self.log_status(f"    ?舀?雿???: {len(switches) - open_switches - disabled_switches} ??)
            
            self.root.update_idletasks()
            
            # 憿舐內?刻??蝑
            self.log_status("\n7. ?刻??蝑:")
            if xpath_products and xpath_products.get('product_count', 0) > 0:
                self.log_status("  ?刻雿輻XPath?豢??函???)
                
                # 皜祈岫XPath蝑
                self.log_status("\n8. 皜祈岫XPath蝑...")
                xpath_result = analyzer.process_with_xpath_strategy()
                
                if xpath_result.get("strategy") == "xpath" and xpath_result.get("results"):
                    products = xpath_result["results"]
                    self.log_status(f"  皜祈岫??嚗Path蝑?曉銝西??? {len(products)} ????)
                    
                    # 憿舐內??蝯梯?
                    need_action = 0
                    for product in products:
                        for spec in product["specs"]:
                            if spec["action"] == "?閬???:
                                need_action += 1
                    
                    self.log_status(f"  ?閬??????賊?: {need_action} ??)
                    
                else:
                    self.log_status(f"  皜祈岫憭望?: {xpath_result.get('error', '?芰?航炊')}")
            
            elif pagination.get("found", False) and pagination.get("totalPages", 1) > 1:
                self.log_status("  ?刻雿輻??蝑嚗?????")
            elif scroll_info.get("mayUseInfiniteScroll", False):
                self.log_status("  ?刻雿輻?⊿?皛曉?蝑嚗?皛曉??????)
            else:
                self.log_status("  ?刻雿輻?桅???蝑")
                
            self.log_status("\n===== ???摰? =====")
            
        except Exception as e:
            self.log_status(f"???蝯???隤? {str(e)}")
            messagebox.showerror("?航炊", f"???蝯???隤? {str(e)}")
            
    def set_confirmation(self, result):
        """閮剔蔭?冽蝣箄?蝯?"""
        self.confirmation_result = result
        self.confirmation_var.set(1)  # 閫貊wait_variable
        
    def __del__(self):
        if self.driver:
            self.driver.quit()

    def log_summary_products(self, products):
        """蝎曄陛憿舐內?Ｗ????潭?閬縑?荔??冽頛?瑼Ｚ????”"""
        if not products or len(products) == 0:
            self.log_status("?芣?唬遙雿??)
            return
            
        # 皜征?嗅??????
        self.status_text.delete(1.0, tk.END)
        
        # 憿舐內蝮賢?曉?????
        total_products = len(products)
        total_specs = sum(len(product.get('specs', [])) for product in products)
        
        self.log_status("===== ?????? =====")
        self.log_status(f"蝮賢?曉: {total_products} ???? {total_specs} ????)
        self.log_status("=" * 80)
        
        # 閮?蝮賡???
        page_size = 10
        total_pages = (total_products + page_size - 1) // page_size
        
        # ?萄遣??豢?Frame
        if hasattr(self, 'page_frame') and self.page_frame:
            try:
                self.page_frame.grid_forget()
            except:
                pass
            
        self.page_frame = ttk.Frame(self.root)
        self.page_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        # ?Ⅳ璅惜
        self.page_label = ttk.Label(self.page_frame, text=f"? 1 / {total_pages}")
        self.page_label.grid(row=0, column=1, padx=5)
        
        # ?????
        if total_pages > 1:
            self.prev_btn = ttk.Button(self.page_frame, text="銝???, state="disabled",
                                       command=lambda: self.show_product_page(products, self.current_page-1, page_size))
            self.prev_btn.grid(row=0, column=0, padx=10)
            
            self.next_btn = ttk.Button(self.page_frame, text="銝???, 
                                       command=lambda: self.show_product_page(products, self.current_page+1, page_size))
            self.next_btn.grid(row=0, column=2, padx=10)
            
            # 瘛餃?頛詨?Ⅳ?歲頧???
            ttk.Label(self.page_frame, text="頝唾?Ⅳ:").grid(row=0, column=3, padx=(20, 5))
            self.page_entry = ttk.Entry(self.page_frame, width=5)
            self.page_entry.grid(row=0, column=4, padx=5)
            ttk.Button(self.page_frame, text="頝唾?", 
                       command=lambda: self.jump_to_page(products, page_size)).grid(row=0, column=5, padx=5)
        
        # ???
        self.current_page = 1
        
        # 憿舐內蝚砌?????
        self.show_product_page(products, 1, page_size)
        
        # ?萄遣蝣箄?????
        if hasattr(self, 'action_frame') and self.action_frame:
            try:
                self.action_frame.grid_forget()
            except:
                pass
            
        self.action_frame = ttk.Frame(self.root)
        self.action_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(self.action_frame, text="???????, 
                  command=lambda: self.process_selected_products(products)).grid(row=0, column=0, padx=10)
        
        ttk.Button(self.action_frame, text="?臬???”", 
                  command=lambda: self.export_products(products)).grid(row=0, column=1, padx=10)
        
        ttk.Button(self.action_frame, text="??", 
                  command=self.cancel_processing).grid(row=0, column=2, padx=10)
    
    def show_product_page(self, products, page, page_size=10):
        """憿舐內???Ⅳ???縑??""
        # 皜征?嗅???憿舐內
        self.status_text.delete(1.0, tk.END)
        
        # 閮?蝮賡???
        total_products = len(products)
        total_pages = (total_products + page_size - 1) // page_size
        
        # 蝣箔??Ⅳ??
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
            
        self.current_page = page
        
        # ?湔?Ⅳ璅惜
        self.page_label.config(text=f"? {page} / {total_pages}")
        
        # ?湔?????
        if hasattr(self, 'prev_btn'):
            self.prev_btn.config(state="normal" if page > 1 else "disabled")
        if hasattr(self, 'next_btn'):
            self.next_btn.config(state="normal" if page < total_pages else "disabled")
        
        # 閮??嗅??＊蝷箇???
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_products)
        
        self.log_status(f"===== ???” (憿舐內 {start_idx+1}-{end_idx} / ??{total_products} ???? =====")
        
        # 憿舐內?嗅?????
        for i in range(start_idx, end_idx):
            product = products[i]
            product_name = product.get('name', f"?? #{i+1}")
            specs = product.get('specs', [])
            
            self.log_status(f"\n{i+1}. {product_name}")
            self.log_status("-" * 80)
            
            # 閬閮
            total_specs = len(specs)
            open_specs = sum(1 for spec in specs if spec.get('status') == '??')
            closed_specs = total_specs - open_specs
            
            # 摨怠?閮
            in_stock = sum(1 for spec in specs if spec.get('stock') and ''.join(filter(str.isdigit, str(spec.get('stock', '0')))) != '0')
            sold_out = total_specs - in_stock
            
            # 憿舐內閬蝯梯?
            self.log_status(f"閬蝮賣: {total_specs} | ????? {open_specs} | ????? {closed_specs}")
            self.log_status(f"?澈摮??? {in_stock} | ?桃?閬: {sold_out}")
            
            # 憿舐內?????潛?蝪∟?靽⊥
            if specs:
                self.log_status("\n閬?汗:")
                for j, spec in enumerate(specs[:5]):  # ?芷＊蝷箏?5????
                    spec_name = spec.get('name', '?芰閬')
                    stock = spec.get('stock', '0')
                    price = spec.get('price', '0')
                    status = spec.get('status', '?芰')
                    
                    # ???航????澆?蝔?
                    if len(spec_name) > 30:
                        spec_name = spec_name[:27] + "..."
                    
                    self.log_status(f"  {spec_name:<30} | 摨怠?: {stock:<8} | ?寞: {price:<12} | ??? {status}")
                
                if len(specs) > 5:
                    self.log_status(f"  ... ?? {len(specs) - 5} ????...")
            
            self.log_status("-" * 80)
            
            # 瘥＊蝷箔?????託I
            self.root.update_idletasks()
    
    def jump_to_page(self, products, page_size=10):
        """頝唾??唳?摰?蝣?""
        try:
            page = int(self.page_entry.get())
            self.show_product_page(products, page, page_size)
        except ValueError:
            self.log_status("隢撓?交????Ⅳ")
    
    def process_selected_products(self, products):
        """???????""
        self.log_status("\n皞????????..")
        
        # 閮剔蔭蝣箄?霈?
        self.confirmation_result = True
        
        # 蝘駁????雿???
        if hasattr(self, 'page_frame') and self.page_frame:
            self.page_frame.grid_forget()
        
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.grid_forget()
        
        # 隤輻?????寞?
        self._process_products(products)
    
    def export_products(self, products):
        """撠???銵典??箏瑼?"""
        import datetime
        
        try:
            # ?萄遣瑼???
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"?Ｗ?皜_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"===== ???”蝮賢 {len(products)} ????=====\n\n")
                
                for i, product in enumerate(products):
                    product_name = product.get('name', f"?? #{i+1}")
                    specs = product.get('specs', [])
                    
                    f.write(f"{i+1}. {product_name}\n")
                    f.write("-" * 80 + "\n")
                    
                    for j, spec in enumerate(specs):
                        spec_name = spec.get('name', '?芰閬')
                        stock = spec.get('stock', '0')
                        price = spec.get('price', '0')
                        status = spec.get('status', '?芰')
                        disabled = spec.get('disabled', False)
                        
                        status_display = f"{status}{' (撌脩???' if disabled else ''}"
                        f.write(f"  閬 #{j+1}: {spec_name} | 摨怠?: {stock} | ?寞: {price} | ??? {status_display}\n")
                    
                    f.write("-" * 80 + "\n\n")
            
            self.log_status(f"\n撌脫???箏???銵? {filename}")
            
        except Exception as e:
            self.log_status(f"?臬???”??隤? {str(e)}")
    
    def cancel_processing(self):
        """??????"""
        self.log_status("\n?冽????")
        
        # 蝘駁????雿???
        if hasattr(self, 'page_frame') and self.page_frame:
            self.page_frame.grid_forget()
        
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.grid_forget()
    
    def _process_products(self, products):
        """撖阡??????瘜?""
        self.log_status("\n??????...")
        
        # ??瘥???
        for i, product in enumerate(products):
            self.log_status(f"\n?? #{i+1}: {product['name']}")
            self.log_status("=" * 80)
            
            # ??閬
            specs = product.get("specs", [])
            for j, spec in enumerate(specs):
                spec_name = spec.get("name", f"閬 #{j+1}")
                spec_stock = spec.get("stock", "0")
                spec_price = spec.get("price", "0")
                spec_status = spec.get("status", "?芰")
                spec_disabled = spec.get("disabled", False)
                
                # ?岫??摨怠??詨?
                try:
                    stock_number = int(''.join(filter(str.isdigit, str(spec_stock))))
                except:
                    stock_number = 0
                
                # 蝣箏?????
                if stock_number > 0 and not spec_disabled:
                    if spec_status != "??":
                        action = "?閬???
                    else:
                        action = "??迤撣賂??⊿???"
                else:
                    action = "??迤撣賂??⊿???"
                
                status_text = f"閬 #{j+1}: {spec_name} | 摨怠?: {spec_stock} | ?寞: {spec_price} | ??? {spec_status}{' (撌脩???' if spec_disabled else ''}"
                self.log_status(status_text)
                
                if action == "?閬???:
                    self.log_status("?閬?雿? ????")
                    # 撖阡???????
                    self.log_status(f"甇??? '{spec_name}' ????..")
                    result = self._toggle_product_switch(product['name'], spec_name)
                    if result:
                        self.log_status("??撌脫???????)
                    else:
                        self.log_status("??????憭望?")
                
                self.log_status("-" * 80)
                
                # ?湔?
                self.root.update_idletasks()
            
            # 瘥???????唬?甈｜I
            if i % 5 == 0:
                self.log_status(f"撌脰???{i+1}/{len(products)} ????..")
                self.root.update_idletasks()
        
        self.log_status("\n?????????")
    
    def handle_notice_modal(self, modal_element):
        """撠????釣????敶?"""
        self.log_status("?????釣??蝒?..")
        
        try:
            # 霈??蝒摰寧?潭隤???
            try:
                modal_body = modal_element.find_element(By.CSS_SELECTOR, ".eds-modal__body").text
                self.log_status(f"敶??批捆: {modal_body}")
            except:
                pass
            
            # ?寞?1: 雿輻JavaScript?湔摰?銝阡?????(??舫??瘜?
            self.log_status("?寞?1: 雿輻JavaScript?湔暺?...")
            js_result = self.driver.execute_script("""
                try {
                    // ?湔?脣?蝣箄???
                    const confirmButton = document.querySelector('.eds-modal__footer-buttons .eds-button--primary');
                    if (confirmButton) {
                        // 擃漁憿舐內??
                        confirmButton.style.border = '3px solid red';
                        
                        // 閮???鞈?
                        console.log('蝣箄?????:', confirmButton.innerText);
                        console.log('蝣箄???憿?:', confirmButton.className);
                        
                        // ?岫暺?
                        confirmButton.click();
                        return true;
                    }
                } catch (e) {
                    console.error('JavaScript暺?憭望?:', e);
                    return false;
                }
                return false;
            """)
            
            if js_result:
                self.log_status("??JavaScript?寞???暺???")
                time.sleep(1)
                
                # 瑼Ｘ敶??臬瘨仃
                if not self.is_modal_visible():
                    return True
            
            # ?寞?2: 雿輻?萇敹急??- ?escape皜?阡?
            self.log_status("?寞?2: 雿輻?萇璅⊥...")
            # ??ESC皜?嗅??阡?
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            
            # ?汽AB?萇宏?暺蝣箄??? (?虜?舫??Ｖ?蝚?-5????)
            for i in range(5):
                ActionChains(self.driver).send_keys(Keys.TAB).perform()
                time.sleep(0.5)
            
            # ?nter蝣箄?
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(1)
            
            # 瑼Ｘ敶??臬瘨仃
            if not self.is_modal_visible():
                self.log_status("???萇?寞?????敶?")
                return True
            
            # ?寞?3: 雿輻XPath蝎曄Ⅱ摰???
            self.log_status("?寞?3: 雿輻XPath蝎曄Ⅱ摰?...")
            try:
                button = self.driver.find_element(By.XPATH, 
                    "//div[contains(@class, 'eds-modal__footer-buttons')]//button[contains(@class, 'eds-button--primary')]")
                
                if button and button.is_displayed():
                    self.log_status(f"?曉??: {button.text}")
                    
                    # 擃漁憿舐內??
                    self.driver.execute_script("arguments[0].style.border='3px solid blue';", button)
                    
                    # ?寞?3.1: ?湔暺?
                    try:
                        button.click()
                        self.log_status("?岫?湔暺?")
                        time.sleep(1)
                        
                        if not self.is_modal_visible():
                            self.log_status("???湔暺???")
                            return True
                    except Exception as e:
                        self.log_status(f"?湔暺?憭望?: {str(e)}")
                    
                    # ?寞?3.2: 雿輻JavaScript暺?
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                        self.log_status("?岫JavaScript暺?")
                        time.sleep(1)
                        
                        if not self.is_modal_visible():
                            self.log_status("??JavaScript暺???")
                            return True
                    except Exception as e:
                        self.log_status(f"JavaScript暺?憭望?: {str(e)}")
                    
                    # ?寞?3.3: 雿輻ActionChains暺?
                    try:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(button).pause(0.3).click().perform()
                        self.log_status("?岫ActionChains暺?")
                        time.sleep(1)
                        
                        if not self.is_modal_visible():
                            self.log_status("??ActionChains暺???")
                            return True
                    except Exception as e:
                        self.log_status(f"ActionChains暺?憭望?: {str(e)}")
            except Exception as e:
                self.log_status(f"XPath撠??憭望?: {str(e)}")
            
            # ?寞?4: 撠????
            self.log_status("?寞?4: ?岫暺?????...")
            try:
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".eds-modal__close")
                if close_buttons and len(close_buttons) > 0 and close_buttons[0].is_displayed():
                    close_buttons[0].click()
                    self.log_status("暺?????")
                    time.sleep(1)
                    
                    if not self.is_modal_visible():
                        self.log_status("????????????敶?")
                        return True
            except Exception as e:
                self.log_status(f"暺?????憭望?: {str(e)}")
            
            # ?寞?5: ?岫?潮scape?菟???蝒?
            self.log_status("?寞?5: 雿輻Escape??..")
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            
            if not self.is_modal_visible():
                self.log_status("??Escape?菜?????蝒?)
                return True
            
            # ?寞?6: ??冽????
            self.log_status("???芸??寞??仃??隢????Ⅱ隤???)
            messagebox.showinfo("?閬???雿?, "隢?????蝒葉?Ⅱ隤????嗅?暺?蝣箏?蝜潛???)
            
            # 蝑??冽????
            for _ in range(10):  # ?憭?敺?0蝘?
                if not self.is_modal_visible():
                    self.log_status("??敶?撌脰◤????")
                    return True
                time.sleep(1)
            
            return not self.is_modal_visible()
        
        except Exception as e:
            self.log_status(f"???釣??蝒??潛??航炊: {str(e)}")
            return False
    
    def is_modal_visible(self):
        """瑼Ｘ敶??臬?航?"""
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
