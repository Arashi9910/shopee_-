#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
整合測試腳本

此腳本用於測試主程式與重構後的模組是否可以正常整合
"""

import sys
import os
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("整合測試")

def test_import():
    """測試主程式與模組的導入"""
    logger.info("測試主程式與模組的導入...")
    
    try:
        # 嘗試導入主程式
        from 主程式 import 調價主程式
        logger.info("✓ 成功導入主程式")
        
        # 嘗試導入商品處理模組
        from 模組.商品處理 import 商品處理集成
        logger.info("✓ 成功導入商品處理集成模組")
        
        # 嘗試導入子模組
        from 模組.商品處理.搜尋 import 商品搜尋
        from 模組.商品處理.規格分析 import 規格分析
        from 模組.商品處理.價格調整 import 價格調整
        from 模組.商品處理.開關控制 import 開關控制
        from 模組.商品處理.批量處理 import 批量處理
        
        logger.info("✓ 成功導入所有子模組")
        return True
    except Exception as e:
        logger.error(f"✗ 模組導入失敗: {str(e)}")
        return False

def test_instance_creation():
    """測試實例化主程式和模組"""
    logger.info("測試實例化主程式和模組...")
    
    try:
        # 嘗試創建 Mock WebDriver
        class MockDriver:
            def __init__(self):
                self.current_url = "https://example.com"
                
            def execute_script(self, script, *args):
                return {"product_count": 0, "spec_count": 0, "products": []}
                
            def find_elements(self, by, value):
                return []
        
        # 創建模擬 driver
        mock_driver = MockDriver()
        
        # 從主程式導入類
        from 主程式 import 調價主程式
        
        # 嘗試實例化主程式（不帶GUI）
        app = 調價主程式()
        logger.info("✓ 成功實例化主程式")
        
        # 嘗試實例化商品處理集成類
        from 模組.商品處理 import 商品處理集成
        product_handler = 商品處理集成(mock_driver)
        logger.info("✓ 成功實例化商品處理集成類")
        
        # 檢查各個模組是否已正確實例化
        if not hasattr(product_handler, '搜尋器'):
            logger.error("✗ 搜尋器未正確實例化")
            return False
            
        if not hasattr(product_handler, '規格分析器'):
            logger.error("✗ 規格分析器未正確實例化")
            return False
            
        if not hasattr(product_handler, '價格調整器'):
            logger.error("✗ 價格調整器未正確實例化")
            return False
            
        if not hasattr(product_handler, '開關控制器'):
            logger.error("✗ 開關控制器未正確實例化")
            return False
            
        if not hasattr(product_handler, '批量處理器'):
            logger.error("✗ 批量處理器未正確實例化")
            return False
            
        logger.info("✓ 所有子模組已正確實例化")
        return True
    except Exception as e:
        logger.error(f"✗ 實例化失敗: {str(e)}")
        return False

def test_method_delegation():
    """測試方法代理"""
    logger.info("測試方法代理...")
    
    try:
        # 嘗試創建 Mock WebDriver
        class MockDriver:
            def __init__(self):
                self.current_url = "https://example.com"
                
            def execute_script(self, script, *args):
                return {"product_count": 0, "spec_count": 0, "products": []}
                
            def find_elements(self, by, value):
                return []
        
        # 創建模擬 driver
        mock_driver = MockDriver()
        
        # 從主程式導入類
        from 主程式 import 調價主程式
        
        # 嘗試實例化主程式（不帶GUI）
        app = 調價主程式()
        app.driver = mock_driver
        
        # 嘗試實例化商品處理集成類 (通過主程式使用的名稱)
        from 模組.商品處理 import 商品處理集成 as 商品處理
        product_handler = 商品處理(mock_driver)
        
        # 檢查方法代理
        proxy_methods = [
            '點擊編輯按鈕',
            '檢查是否編輯模式',
            '進入編輯模式',
            '搜尋商品',
            '搜尋特定前綴商品',
            '格式化商品資訊',
            '分析規格類型',
            '查找同類規格價格',
            '切換商品規格開關',
            '調整商品價格',
            '批量處理商品規格'
        ]
        
        for method in proxy_methods:
            if not hasattr(product_handler, method):
                logger.error(f"✗ 方法 '{method}' 未正確代理")
                return False
        
        logger.info("✓ 所有方法均已正確代理")
        return True
    except Exception as e:
        logger.error(f"✗ 方法代理測試失敗: {str(e)}")
        return False

def run_tests():
    """運行所有測試"""
    logger.info("開始運行整合測試...")
    
    tests = [
        ("模組導入測試", test_import),
        ("實例化測試", test_instance_creation),
        ("方法代理測試", test_method_delegation)
    ]
    
    success_count = 0
    fail_count = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n開始執行測試: {test_name}")
        
        if test_func():
            logger.info(f"✓ 測試 '{test_name}' 成功")
            success_count += 1
        else:
            logger.error(f"✗ 測試 '{test_name}' 失敗")
            fail_count += 1
    
    logger.info(f"\n測試執行完成，共執行 {len(tests)} 個測試，成功 {success_count} 個，失敗 {fail_count} 個")
    
    return success_count == len(tests)

if __name__ == "__main__":
    if run_tests():
        logger.info("✅ 所有測試通過！模組整合成功。")
        sys.exit(0)
    else:
        logger.error("❌ 測試未全部通過，請檢查模組整合是否正確。")
        sys.exit(1) 