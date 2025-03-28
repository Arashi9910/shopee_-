#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
蝦皮商品規格調價自動化程式

此程式用於自動化調整蝦皮產品規格的啟用狀態。
可自動啟用/停用特定前綴的商品規格，提高調價作業效率。
"""

import sys
import os
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from selenium import webdriver

# 導入自定義模組
from 模組.瀏覽器處理 import 瀏覽器控制
from 模組.商品處理 import 商品處理集成
from 模組.介面處理 import 介面控制
from 模組.彈窗處理 import 彈窗處理
from 模組.紀錄輸出 import 紀錄管理器

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("調價主程式")

class 調價主程式:
    """調價主程式類，整合各個模組功能"""
    
    def __init__(self, root=None):
        """初始化主程式"""
        logger.info("初始化調價主程式")
        self.driver = None
        self.browser_controller = None
        self.root = root
        self.products = []  # 初始化products为空列表，避免后续访问未定义属性
        
        # 設置程式退出時的清理操作
        import atexit
        atexit.register(self._cleanup)
        
        if root:
            # 使用介面控制器創建GUI
            self.interface = 介面控制(root, self)
            self.setup_gui()
        else:
            self.interface = None
        
        # 初始化彈窗處理
        self.popup_handler = 彈窗處理()
        
        # 初始化紀錄管理器
        self.紀錄器 = 紀錄管理器()
    
    def _cleanup(self):
        """清理資源，確保瀏覽器正確關閉"""
        try:
            if hasattr(self, 'browser_controller') and self.browser_controller and self.driver:
                logger.info("程式退出，關閉瀏覽器...")
                self.browser_controller.close_browser()
        except Exception as e:
            logger.error(f"關閉瀏覽器時發生錯誤: {str(e)}")
            # 在這裡無法顯示UI錯誤，只能記錄日誌
    
    def setup_gui(self):
        """設置GUI界面"""
        if not self.interface:
            return
            
        # 設置主視窗標題和大小
        self.root.title("蝦皮商品規格調價自動化")
        self.root.geometry("800x600")
        
        # 創建框架
        self.interface.create_frame()
        
        # 第一行按鈕
        self.interface.add_button("啟動Chrome瀏覽器", self.start_browser_thread, row=0, column=0)
        self.interface.add_button("連接已開啟的瀏覽器", self.connect_browser_thread, row=0, column=1)
        self.interface.add_button("編輯折扣活動", self.edit_discount_activity_thread, row=0, column=2)
        
        # 第二行按鈕
        self.interface.add_button("批量處理商品規格", self.batch_process_thread, row=1, column=0)
        
        # 創建多頁處理區域 (第二行右側)
        page_frame = ttk.Frame(self.interface.button_frame)
        page_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W)
        
        # 添加頁數標籤和輸入框
        ttk.Label(page_frame, text="處理頁數:").grid(row=0, column=0, padx=(0, 5), sticky=tk.E)
        self.頁數輸入 = ttk.Entry(page_frame, width=5)
        self.頁數輸入.insert(0, "1")  # 預設值
        self.頁數輸入.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        # 添加多頁處理按鈕
        ttk.Button(page_frame, text="多頁批量處理", 
                  command=self.multi_page_process_thread,
                  width=20).grid(row=0, column=2)
        
        # 創建日誌區域
        self.interface.create_log_area()
        
        # 設置關閉視窗時的操作
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """關閉視窗時的處理"""
        try:
            if messagebox.askokcancel("關閉", "確定要關閉程式嗎？"):
                # 關閉瀏覽器
                if self.browser_controller and self.driver:
                    self.browser_controller.close_browser()
                # 關閉視窗
                self.root.destroy()
        except Exception as e:
            logger.error(f"關閉視窗時發生錯誤: {str(e)}")
            self.root.destroy()
    
    def start_browser_thread(self):
        """在新線程中啟動瀏覽器"""
        threading.Thread(target=self.start_browser, daemon=True).start()
    
    def connect_browser_thread(self):
        """在新線程中連接瀏覽器"""
        threading.Thread(target=self.connect_browser, daemon=True).start()
    
    def edit_discount_activity_thread(self):
        """在新線程中編輯折扣活動"""
        threading.Thread(target=self.edit_discount_activity, daemon=True).start()
    
    def batch_process_thread(self):
        """在新線程中批量處理商品規格"""
        threading.Thread(target=self.batch_process, daemon=True).start()
    
    def multi_page_process_thread(self):
        """在新線程中執行多頁批量處理"""
        threading.Thread(target=self.multi_page_process, daemon=True).start()
    
    def start_browser(self):
        """啟動Chrome瀏覽器"""
        try:
            self.interface.log_message("正在啟動Chrome瀏覽器...")
            self.browser_controller = 瀏覽器控制()
            
            # 获取用户输入的URL
            url = self.interface.get_url()
            
            # 啟動瀏覽器
            if url:
                self.interface.log_message(f"使用網址: {url}")
                self.driver = self.browser_controller.launch_browser(url=url)
            else:
                self.driver = self.browser_controller.launch_browser()
            
            if self.driver:
                self.interface.log_message("✓ Chrome瀏覽器啟動成功")
                self.interface.show_info_dialog("成功", "Chrome瀏覽器啟動成功")
            else:
                self.interface.log_message("✗ Chrome瀏覽器啟動失敗")
                self.interface.show_error_dialog("錯誤", "Chrome瀏覽器啟動失敗，請檢查Chrome是否已安裝")
        except Exception as e:
            logger.error(f"啟動瀏覽器時發生錯誤: {str(e)}")
            self.interface.log_message(f"✗ 錯誤: {str(e)}")
            self.interface.show_error_dialog("錯誤", f"啟動瀏覽器時發生錯誤: {str(e)}")
    
    def connect_browser(self):
        """連接已開啟的Chrome瀏覽器"""
        try:
            self.interface.log_message("正在連接已開啟的Chrome瀏覽器...")
            self.browser_controller = 瀏覽器控制()
            
            # 連接瀏覽器
            self.driver = self.browser_controller.connect_to_browser()
            
            if self.driver:
                self.interface.log_message("✓ 成功連接到現有的Chrome瀏覽器")
                
                # 获取用户输入的URL
                url = self.interface.get_url()
                
                # 如果有URL，则导航到该URL
                if url:
                    self.interface.log_message(f"導航到網址: {url}")
                    self.browser_controller.導航到網址(url)
                    self.interface.log_message(f"✓ 已導航到: {url}")
                
                self.interface.show_info_dialog("成功", "成功連接到現有的Chrome瀏覽器")
            else:
                self.interface.log_message("✗ 連接Chrome瀏覽器失敗")
                self.interface.show_error_dialog("錯誤", "連接Chrome瀏覽器失敗，請確認Chrome已啟動")
        except Exception as e:
            logger.error(f"連接瀏覽器時發生錯誤: {str(e)}")
            self.interface.log_message(f"✗ 錯誤: {str(e)}")
            self.interface.show_error_dialog("錯誤", f"連接瀏覽器時發生錯誤: {str(e)}")
    
    def edit_discount_activity(self):
        """進入編輯折扣活動頁面並獲取商品數據"""
        try:
            # 檢查瀏覽器是否已啟動
            if not self.driver or not self.browser_controller:
                self.interface.log_message("✗ 請先啟動或連接Chrome瀏覽器")
                self.interface.show_warning_dialog("警告", "請先啟動或連接Chrome瀏覽器")
                return
            
            # 如果有網址輸入，則先導航
            url = self.interface.get_url()
            if url:
                self.interface.log_message(f"導航到活動網址: {url}")
                success = self.browser_controller.導航到網址(url)
                if not success:
                    self.interface.log_message(f"⚠ 導航失敗，請檢查網址是否正確: {url}")
                    self.interface.show_warning_dialog("警告", "導航失敗，請檢查網址是否正確")
                    return
            
            # 初始化商品處理模組
            product_handler = 商品處理集成(self.driver)
            
            # 進入編輯頁面
            self.interface.log_message("嘗試進入編輯模式...")
            if not product_handler.搜尋.進入編輯模式():
                self.interface.log_message("⚠ 無法進入編輯模式，可能需要手動點擊")
                self.interface.show_warning_dialog("警告", "無法自動進入編輯模式，請手動點擊編輯按鈕後再試")
                return
            
            self.interface.log_message("✓ 成功進入編輯模式")
            
            # 獲取商品數據
            self.interface.log_message("正在獲取商品數據...")
            search_result = product_handler.搜尋.搜尋商品()
            
            if not search_result:
                self.interface.log_message("⚠ 未能獲取商品數據")
                self.interface.show_error_dialog("錯誤", "未能獲取商品數據")
                return
            
            # 商品數量
            products = search_result.get("products", [])
            product_count = len(products)
            spec_count = search_result.get("spec_count", 0)
            
            self.interface.log_message(f"✓ 已獲取 {product_count} 個商品，共 {spec_count} 個規格")
            
            # 將商品數據保存以便後續處理
            self.products = products
            
            # 嘗試記錄現有商品價格
            try:
                # 清空現有記錄
                self.紀錄器.清空記錄()
                
                # 記錄所有獲取到的商品和規格初始狀態
                for product in products:
                    商品名稱 = product.get("name", "")
                    for spec in product.get("specs", []):
                        規格名稱 = spec.get("name", "")
                        折扣價格 = spec.get("price", "未知")
                        狀態 = spec.get("status", "")
                        
                        # 記錄初始狀態
                        self.紀錄器.記錄價格調整(
                            商品名稱, 
                            規格名稱, 
                            折扣價格, 
                            "尚未調整", 
                            狀態 == "開啟"
                        )
                
                self.interface.log_message(f"✓ 已記錄 {len(self.紀錄器.調整紀錄列表)} 個商品規格的初始狀態")
            except Exception as record_error:
                logger.warning(f"記錄初始狀態時出錯: {str(record_error)}")
        
        except Exception as e:
            logger.error(f"進入編輯折扣活動頁面時發生錯誤: {str(e)}")
            self.interface.log_message(f"✗ 錯誤: {str(e)}")
            self.interface.show_error_dialog("錯誤", f"進入編輯折扣活動頁面時發生錯誤: {str(e)}")
    
    def batch_process(self):
        """批量處理商品規格，包括開啟按鈕和調整價格"""
        try:
            # 檢查瀏覽器是否已啟動
            if not self.driver or not self.browser_controller:
                self.interface.log_message("✗ 請先啟動或連接Chrome瀏覽器")
                self.interface.show_warning_dialog("警告", "請先啟動或連接Chrome瀏覽器")
                return
            
            # 檢查是否已獲取商品
            if not hasattr(self, 'products') or not self.products:
                self.interface.log_message("⚠ 尚未獲取商品數據，請先點擊「編輯折扣活動」")
                self.interface.show_warning_dialog("警告", "尚未獲取商品數據，請先點擊「編輯折扣活動」")
                return
                
            self.interface.log_message("開始批量處理商品規格...")
            
            # 初始化商品處理模組
            product_handler = 商品處理集成(self.driver)
            
            # 批量處理商品規格
            總處理數, 開關成功數, 價格成功數 = product_handler.批量處理.批量處理商品規格(self.products)
            
            # 記錄商品調整結果
            self.interface.log_message("正在記錄調整結果...")
            
            # 尋找最近處理過的商品，從頁面獲取其規格和價格信息
            try:
                # 使用JavaScript從頁面獲取已處理的商品規格信息
                已處理商品記錄 = self.driver.execute_script("""
                    // 收集已處理的商品規格和價格信息
                    const result = [];
                    
                    // 獲取所有商品容器
                    const productContainers = document.querySelectorAll('div.discount-item-component, div.discount-edit-item');
                    
                    for (const container of productContainers) {
                        // 獲取商品名稱
                        const nameEl = container.querySelector('div.ellipsis-content.single');
                        if (!nameEl) continue;
                        
                        const 商品名稱 = nameEl.textContent.trim();
                        
                        // 獲取規格元素
                        const specElements = container.querySelectorAll('div.discount-view-item-model-component, div.discount-edit-item-model-component');
                        
                        for (const specElement of specElements) {
                            // 獲取規格名稱
                            const specNameEl = specElement.querySelector('div.ellipsis-content.single');
                            if (!specNameEl) continue;
                            
                            const 規格名稱 = specNameEl.textContent.trim();
                            
                            // 獲取價格信息
                            const priceInput = specElement.querySelector('input.eds-input__input');
                            const priceDisplay = specElement.querySelector('.currency-input, [class*="price"]');
                            
                            let 價格 = '未知';
                            if (priceInput) {
                                價格 = priceInput.value;
                            } else if (priceDisplay) {
                                價格 = priceDisplay.textContent.trim();
                            }
                            
                            // 確認是否為開啟狀態
                            const switchEl = specElement.querySelector('div.eds-switch');
                            let 是否開啟 = false;
                            
                            if (switchEl) {
                                是否開啟 = switchEl.classList.contains('eds-switch--open');
                            }
                            
                            result.push({
                                '商品名稱': 商品名稱,
                                '規格名稱': 規格名稱,
                                '折扣價格': 價格,
                                '是否開啟': 是否開啟
                            });
                        }
                    }
                    
                    return result;
                """)
                
                if 已處理商品記錄:
                    for 記錄 in 已處理商品記錄:
                        # 從products中找到對應的規格價格設定
                        商品名稱 = 記錄.get('商品名稱', '')
                        規格名稱 = 記錄.get('規格名稱', '')
                        折扣價格 = 記錄.get('折扣價格', '未知')
                        
                        設定價格 = '未設定'
                        成功狀態 = False
                        
                        # 在products中尋找對應的設定價格
                        for product in self.products:
                            if product.get('name') == 商品名稱:
                                for spec in product.get('specs', []):
                                    if spec.get('name') == 規格名稱:
                                        設定價格 = spec.get('price', '未設定')
                                        # 假設與折扣價格相同的視為成功
                                        成功狀態 = str(設定價格) in str(折扣價格)
                                        break
                        
                        # 記錄調整信息
                        self.紀錄器.記錄價格調整(商品名稱, 規格名稱, 折扣價格, 設定價格, 成功狀態)
                    
                    # 輸出Excel報表
                    excel_path = self.紀錄器.輸出Excel報表()
                    if excel_path:
                        self.紀錄器.添加統計摘要(excel_path, 總處理數, 價格成功數, 總處理數 - 價格成功數)
                        self.interface.log_message(f"✓ 已將調整記錄保存至: {excel_path}")
                        
                        # 打開報表目錄
                        os.startfile(os.path.dirname(excel_path))
                    else:
                        self.interface.log_message("⚠ 無法生成調整記錄Excel")
                else:
                    self.interface.log_message("⚠ 無法從頁面獲取已處理的商品信息")
            except Exception as record_error:
                logger.error(f"記錄調整結果時出錯: {str(record_error)}")
                self.interface.log_message(f"⚠ 記錄調整結果時出錯: {str(record_error)}")
            
            # 更新UI
            if 總處理數 > 0:
                結果訊息 = f"批量處理完成!\n\n總共 {總處理數} 個規格\n開啟 {開關成功數} 個\n調整價格 {價格成功數} 個"
                self.interface.log_message(結果訊息.replace('\n', ' '))
                self.interface.show_info_dialog("處理結果", 結果訊息)
            else:
                self.interface.log_message("未找到需要處理的規格")
                self.interface.show_info_dialog("處理結果", "未找到需要處理的規格")
            
        except Exception as e:
            logger.error(f"批量處理商品規格時發生錯誤: {str(e)}")
            self.interface.log_message(f"✗ 錯誤: {str(e)}")
            self.interface.show_error_dialog("錯誤", f"批量處理商品規格時發生錯誤: {str(e)}")
    
    def multi_page_process(self):
        """執行多頁批量處理"""
        try:
            # 檢查瀏覽器是否已啟動
            if not self.driver or not self.browser_controller:
                self.interface.log_message("✗ 請先啟動或連接Chrome瀏覽器")
                self.interface.show_warning_dialog("警告", "請先啟動或連接Chrome瀏覽器")
                return
            
            # 如果有網址輸入，則先導航
            url = self.interface.get_url()
            if url:
                current_url = self.driver.current_url
                if url not in current_url:
                    self.interface.log_message(f"導航到網址: {url}")
                    success = self.browser_controller.導航到網址(url)
                    if not success:
                        self.interface.log_message(f"⚠ 導航失敗，請檢查網址是否正確: {url}")
                        self.interface.show_warning_dialog("警告", "導航失敗，請檢查網址是否正確")
                        return
            
            # 獲取用戶輸入的頁數
            try:
                頁數 = int(self.頁數輸入.get())
                if 頁數 < 1:
                    raise ValueError("頁數必須大於0")
            except ValueError as e:
                self.interface.log_message(f"⚠ 頁數輸入錯誤: {str(e)}")
                self.interface.show_warning_dialog("警告", f"頁數輸入錯誤: {str(e)}\n請輸入一個大於0的整數")
                return
            
            self.interface.log_message(f"開始批量處理 {頁數} 頁商品...")
            
            # 初始化商品處理模組
            product_handler = 商品處理集成(self.driver)
            
            # 確保在編輯模式
            if not product_handler.搜尋.檢查是否編輯模式():
                self.interface.log_message("嘗試進入編輯模式...")
                success = product_handler.進入編輯模式()
                if not success:
                    self.interface.log_message("⚠ 無法進入編輯模式，可能需要手動操作")
                    self.interface.show_warning_dialog("警告", "無法進入編輯模式，請手動點擊編輯按鈕後再試")
                    return
                self.interface.log_message("✓ 已成功進入編輯模式")
            
            # 執行多頁批量處理
            try:
                success = product_handler.搜尋.批量處理多頁商品(頁數)
                
                # 顯示處理結果
                if success:
                    self.interface.log_message(f"✓ 多頁批量處理完成，共處理了 {頁數} 頁商品")
                    self.interface.show_info_dialog("處理結果", f"多頁批量處理完成!\n\n成功處理了 {頁數} 頁商品")
                else:
                    self.interface.log_message("⚠ 多頁批量處理過程中發生錯誤，請查看日誌了解詳情")
                    self.interface.show_warning_dialog("處理結果", "多頁批量處理過程中發生錯誤，請查看日誌了解詳情")
            except Exception as e:
                logger.error(f"批量處理多頁商品時發生錯誤: {str(e)}")
                self.interface.log_message(f"✗ 多頁處理錯誤: {str(e)}")
                self.interface.show_error_dialog("錯誤", f"批量處理多頁商品時發生錯誤: {str(e)}")
            
        except Exception as e:
            logger.error(f"多頁批量處理時發生錯誤: {str(e)}")
            self.interface.log_message(f"✗ 錯誤: {str(e)}")
            self.interface.show_error_dialog("錯誤", f"多頁批量處理時發生錯誤: {str(e)}")

# 獨立執行此檔案時啟動應用程式
if __name__ == "__main__":
    try:
        # 創建根視窗
        root = tk.Tk()
        
        # 啟動應用程式
        app = 調價主程式(root)
        
        # 執行主循環
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"程式啟動時發生嚴重錯誤: {str(e)}")
        if 'root' in locals() and root:
            messagebox.showerror("嚴重錯誤", f"程式啟動失敗: {str(e)}")
            root.destroy()
    finally:
        # 確保瀏覽器已關閉
        if 'app' in locals() and app and app.browser_controller and app.driver:
            app.browser_controller.close_browser() 