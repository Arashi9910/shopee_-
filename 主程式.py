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
        
        # 添加啟動瀏覽器按鈕
        self.interface.add_button("啟動Chrome瀏覽器", self.start_browser_thread)
        
        # 添加連接瀏覽器按鈕
        self.interface.add_button("連接已開啟的瀏覽器", self.connect_browser_thread)
        
        # 添加編輯折扣活動按鈕
        self.interface.add_button("編輯折扣活動", self.edit_discount_activity_thread)
        
        # 添加批量處理商品規格按鈕
        self.interface.add_button("批量處理商品規格", self.batch_process_thread)
        
        # 在新行添加頁數輸入框和多頁處理按鈕
        頁數標籤 = self.interface.add_label("處理頁數:", row=1, column=0)
        頁數標籤.grid(sticky=tk.E)
        self.頁數輸入 = self.interface.add_entry(default_value="1", width=5, row=1, column=1)
        self.頁數輸入.grid(sticky=tk.W)
        self.interface.add_button("多頁批量處理", self.multi_page_process_thread, row=1, column=2)
        
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
        """編輯折扣活動"""
        try:
            if not self.driver or not self.browser_controller:
                self.interface.log_message("✗ 請先啟動或連接Chrome瀏覽器")
                self.interface.show_warning_dialog("警告", "請先啟動或連接Chrome瀏覽器")
                return
            
            # 檢查當前URL，如果有URL輸入則進行導航
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
                    self.interface.log_message("✓ 成功導航到頁面")
                
            # 進入折扣活動編輯頁面
            self.interface.log_message("開始編輯折扣活動流程...")
            
            # 初始化商品處理
            product_handler = 商品處理集成(self.driver)
            
            # 確保在編輯模式
            if not product_handler.搜尋.檢查是否編輯模式():
                self.interface.log_message("嘗試進入編輯模式...")
                if not product_handler.進入編輯模式():
                    self.interface.log_message("⚠ 無法進入編輯模式，可能需要手動操作")
                    self.interface.show_warning_dialog("警告", "無法進入編輯模式，請手動點擊編輯按鈕後再試")
                    return
                self.interface.log_message("✓ 已成功進入編輯模式")
            else:
                self.interface.log_message("✓ 已處於編輯模式")
            
            # 搜尋商品
            self.interface.log_message("正在搜尋商品...")
            search_result = product_handler.搜尋.搜尋商品()
            
            # 确保search_result包含有效数据
            if not search_result or not isinstance(search_result, dict):
                self.interface.log_message("⚠ 搜尋結果格式錯誤")
                self.interface.show_warning_dialog("警告", "搜尋結果格式錯誤，請重試")
                return
                
            # 提取商品列表
            products = search_result.get("products", [])
            product_count = search_result.get("product_count", 0)
            spec_count = search_result.get("spec_count", 0)
            
            if not products or product_count == 0:
                self.interface.log_message("⚠ 未找到任何商品")
                self.interface.show_warning_dialog("警告", "未找到任何商品，請確認頁面內容")
                return
            
            # 保存商品列表以備后用
            self.products = products
            self.interface.log_message(f"✓ 找到 {product_count} 個商品，共 {spec_count} 個規格")
            
            # 顯示商品規格信息
            info_text = product_handler.規格分析.格式化商品資訊(products)
            self.interface.log_message("顯示商品規格信息:")
            self.interface.log_message(info_text)
            
            self.interface.show_info_dialog("成功", f"成功獲取到 {product_count} 個商品信息\n請點擊「批量處理商品規格」按鈕繼續")
            
        except Exception as e:
            logger.error(f"編輯折扣活動時發生錯誤: {str(e)}")
            self.interface.log_message(f"✗ 錯誤: {str(e)}")
            self.interface.show_error_dialog("錯誤", f"編輯折扣活動時發生錯誤: {str(e)}")
    
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
            結果 = product_handler.批量處理.批量處理商品規格(self.products)
            
            # 確保結果包含三個值
            if isinstance(結果, tuple) and len(結果) == 3:
                總處理數, 開關成功數, 價格成功數 = 結果
            else:
                # 如果返回结果不是预期的三元组，记录错误并使用默认值
                self.interface.log_message("⚠ 批量處理返回的結果格式不正確")
                logger.warning(f"批量處理返回的結果格式不正確: {結果}")
                總處理數 = 0
                開關成功數 = 0
                價格成功數 = 0
            
            # 顯示處理結果
            self.interface.log_message(f"批量處理完成: 總共 {總處理數} 個規格，開啟 {開關成功數} 個，調整價格 {價格成功數} 個")
            
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