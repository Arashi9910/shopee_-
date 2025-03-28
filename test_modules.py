#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模組重構測試腳本

此腳本用於測試重構後的模組結構是否正常運作
"""

import sys
import os
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("測試腳本")

def test_module_import():
    """測試模組導入"""
    logger.info("測試模組導入...")
    
    try:
        # 嘗試導入商品處理模組
        from 模組.商品處理 import 商品處理
        logger.info("✓ 成功導入商品處理模組")
        
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

def test_class_creation():
    """測試類實例化"""
    logger.info("測試類實例化...")
    
    try:
        # 從商品處理模組導入類
        from 模組.商品處理 import 商品處理
        
        # 嘗試創建 Mock WebDriver
        class MockDriver:
            def __init__(self):
                self.current_url = "https://example.com"
                
            def execute_script(self, script, *args):
                return None
                
            def find_elements(self, by, value):
                return []
        
        # 創建模擬 driver
        mock_driver = MockDriver()
        
        # 嘗試實例化商品處理類
        處理器 = 商品處理(mock_driver)
        logger.info("✓ 成功實例化商品處理類")
        
        # 檢查各個模組是否已正確實例化
        if not hasattr(處理器, '搜尋器'):
            logger.error("✗ 搜尋器未正確實例化")
            return False
            
        if not hasattr(處理器, '規格分析器'):
            logger.error("✗ 規格分析器未正確實例化")
            return False
            
        if not hasattr(處理器, '價格調整器'):
            logger.error("✗ 價格調整器未正確實例化")
            return False
            
        if not hasattr(處理器, '開關控制器'):
            logger.error("✗ 開關控制器未正確實例化")
            return False
            
        if not hasattr(處理器, '批量處理器'):
            logger.error("✗ 批量處理器未正確實例化")
            return False
            
        logger.info("✓ 所有子模組已正確實例化")
        return True
    except Exception as e:
        logger.error(f"✗ 類實例化失敗: {str(e)}")
        return False

def test_method_delegation():
    """測試方法代理"""
    logger.info("測試方法代理...")
    
    try:
        # 從商品處理模組導入類
        from 模組.商品處理 import 商品處理
        
        # 嘗試創建 Mock WebDriver
        class MockDriver:
            def __init__(self):
                self.current_url = "https://example.com"
                
            def execute_script(self, script, *args):
                return None
                
            def find_elements(self, by, value):
                return []
        
        # 創建模擬 driver
        mock_driver = MockDriver()
        
        # 嘗試實例化商品處理類
        處理器 = 商品處理(mock_driver)
        
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
            if not hasattr(處理器, method):
                logger.error(f"✗ 方法 '{method}' 未正確代理")
                return False
        
        logger.info("✓ 所有方法均已正確代理")
        return True
    except Exception as e:
        logger.error(f"✗ 方法代理測試失敗: {str(e)}")
        return False

def run_tests():
    """運行所有測試"""
    logger.info("開始運行模組重構測試...")
    
    tests = [
        ("模組導入測試", test_module_import),
        ("類實例化測試", test_class_creation),
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
        logger.info("✅ 所有測試通過！模組重構成功。")
        sys.exit(0)
    else:
        logger.error("❌ 測試未全部通過，請檢查模組重構是否正確。")
        sys.exit(1) 