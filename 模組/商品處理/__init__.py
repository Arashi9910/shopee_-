"""
商品處理子模組包

此包包含與商品處理相關的所有功能模組:
- 搜尋: 商品搜索相關功能
- 規格分析: 商品規格分析功能
- 價格調整: 商品價格調整功能
- 開關控制: 商品規格開關控制功能
- 批量處理: 批量處理商品規格功能
"""

import importlib.util
import sys
import logging
import os

logger = logging.getLogger(__name__)

# 導入所需的類
from .搜尋 import 商品搜尋
from .按鈕操作 import 按鈕操作
from .開關控制 import 開關控制
from .規格分析 import 規格分析
from .價格調整 import 價格調整
from .批量處理 import 批量處理

# 商品處理集成類
class 商品處理集成:
    """整合所有商品處理功能的集成類"""
    
    def __init__(self, driver):
        """初始化商品處理集成類
        
        Args:
            driver: Selenium WebDriver實例
        """
        logger.info("商品處理集成類已初始化")
        self.driver = driver
        
        # 初始化各個功能模組
        self.搜尋 = 商品搜尋(driver)
        self.規格分析 = 規格分析(driver)
        self.價格調整 = 價格調整(driver)
        self.開關控制 = 開關控制(driver)
        self.批量處理 = 批量處理(driver)
    
    def 檢查是否編輯模式(self):
        """檢查當前頁面是否處於編輯模式"""
        return self.搜尋.檢查是否編輯模式()
    
    def 進入編輯模式(self):
        """嘗試進入編輯模式"""
        logger.info("切換到按鈕操作模組的進入編輯模式功能")
        buttons = 按鈕操作(self.driver)
        return buttons.進入編輯模式()
    
    def 搜尋商品(self):
        """搜尋頁面上的所有商品"""
        return self.搜尋.搜尋商品()
    
    def 搜尋特定前綴商品(self, prefix="Fee"):
        """搜尋特定前綴的商品"""
        return self.搜尋.搜尋特定前綴商品(prefix)
    
    def 格式化商品資訊(self, products):
        """格式化商品和規格信息以便顯示"""
        return self.規格分析.格式化商品資訊(products)
    
    def 分析規格類型(self, spec_name):
        """分析規格名稱的類型"""
        return self.規格分析.分析規格類型(spec_name)
    
    def 查找同類規格價格(self, product, target_spec):
        """在商品中查找與目標規格同類的規格價格"""
        return self.規格分析.查找同類規格價格(product, target_spec)
    
    def 調整商品價格(self, 商品名稱, 規格名稱, 新價格):
        """調整商品規格的價格"""
        logger.info(f"透過介面調整商品 '{商品名稱}' 規格 '{規格名稱}' 的價格為 {新價格}")
        return self.價格調整.調整商品價格(商品名稱, 規格名稱, 新價格)
    
    def 批量調整價格(self, products, 調整策略="同類規格統一價格"):
        """批量調整多個商品的價格"""
        return self.批量處理.批量調整價格(products, 調整策略)
    
    def 批量開關控制(self, products, 操作類型="開啟缺貨規格"):
        """批量控制商品規格的開關狀態"""
        return self.批量處理.批量開關控制(products, 操作類型)
    
    def 開啟規格(self, 商品名稱, 規格名稱):
        """開啟特定商品規格"""
        return self.開關控制.開啟規格(商品名稱, 規格名稱)
    
    def 關閉規格(self, 商品名稱, 規格名稱):
        """關閉特定商品規格"""
        return self.開關控制.關閉規格(商品名稱, 規格名稱)
    
    def 處理需要開啟的規格(self, products):
        """處理所有需要開啟的規格
        
        Args:
            products (list): 包含商品規格信息的列表
            
        Returns:
            tuple: (成功數, 總處理數)
        """
        return self.開關控制.處理需要開啟的規格(products)
    
    def 分析商品規格(self, product_info):
        """分析商品規格並生成建議
        
        Args:
            product_info (dict): 包含商品信息的字典
            
        Returns:
            dict: 分析結果和建議
        """
        return self.規格分析.分析商品規格(product_info)
    
    def 批量設置規格價格(self, 價格設定列表):
        """批量設置多個商品規格的價格
        
        Args:
            價格設定列表 (list): 包含多個價格設定的列表
                每個設定應包含: {'商品名稱': str, '規格名稱': str, '價格': float/str, '類型': str}
                
        Returns:
            tuple: (成功數, 總處理數)
        """
        return self.批量處理.批量設置規格價格(價格設定列表)
    
    def 執行完整處理流程(self, 設定列表=None):
        """執行完整的商品處理流程
        
        Args:
            設定列表 (list, optional): 包含價格設定的列表，如果為None則只進行搜尋和分析
            
        Returns:
            dict: 流程執行結果和統計
        """
        logger.info("開始執行完整商品處理流程")
        
        # 進入編輯模式
        if not self.進入編輯模式():
            logger.error("無法進入編輯模式，流程中止")
            return {"success": False, "error": "無法進入編輯模式"}
        
        # 搜尋商品
        products_info = self.搜尋商品()
        
        if products_info["product_count"] == 0:
            logger.warning("未找到任何商品，流程中止")
            return {"success": False, "error": "未找到任何商品", "products": []}
        
        logger.info(f"找到 {products_info['product_count']} 個商品和 {products_info['spec_count']} 個規格")
        
        # 如果有設定列表，執行批量設置
        results = {"success": True, "products": products_info["products"]}
        
        if 設定列表:
            logger.info(f"開始批量設置 {len(設定列表)} 個價格設定")
            success_count, total_count = self.批量設置規格價格(設定列表)
            
            results["price_adjust"] = {
                "success_count": success_count,
                "total_count": total_count,
                "settings": 設定列表
            }
        
        # 處理需要開啟的規格
        logger.info("處理需要開啟的規格")
        success_switch, total_switch = self.處理需要開啟的規格(products_info["products"])
        
        results["switch_adjust"] = {
            "success_count": success_switch,
            "total_count": total_switch
        }
        
        logger.info("完整商品處理流程執行完畢")
        return results

# 暴露整合類作為默認導出
商品處理 = 商品處理集成 