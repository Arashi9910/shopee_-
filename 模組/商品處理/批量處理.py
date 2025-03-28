"""
批量處理模組

包含與商品規格批量處理相關的功能：
- 批量處理商品規格
"""

import time
import logging

# 設置日誌
logger = logging.getLogger(__name__)

class 批量處理:
    """處理商品規格批量處理相關功能的類"""
    
    def __init__(self, driver):
        """初始化批量處理類
        
        Args:
            driver: Selenium WebDriver實例
        """
        self.driver = driver
        # 批量處理需要依賴其他模塊的功能
        from .開關控制 import 開關控制
        from .價格調整 import 價格調整
        from .規格分析 import 規格分析
        self.開關控制 = 開關控制(driver)
        self.價格調整 = 價格調整(driver)
        self.規格分析 = 規格分析(driver)
    
    def 批量處理商品規格(self, products):
        """批量處理多個商品的規格，開啟庫存>0但未啟用的規格，並設定與同類規格相同的折扣價
        
        Args:
            products (list): 要處理的商品列表
            
        Returns:
            tuple: (總處理數, 開關成功數, 價格成功數)
        """
        總處理數 = 0
        開關成功數 = 0
        價格成功數 = 0
        
        logger.info(f"開始批量處理 {len(products)} 個商品的規格")
        
        for product in products:
            商品名稱 = product.get('name', '')
            規格列表 = product.get('specs', [])
            
            logger.info(f"處理商品: {商品名稱}，{len(規格列表)} 個規格")
            
            # 先找出該商品中所有已開啟的規格及其價格，用於參考
            已開啟規格價格表 = {}
            for spec in 規格列表:
                規格名稱 = spec.get('name', '')
                狀態 = spec.get('status', '')
                # 更新為直接使用price作為折扣價（已經是NT$輸入框的值）
                折扣價 = spec.get('price', '')
                價格類型 = spec.get('priceType', '')
                
                if 狀態 == "開啟" and 折扣價:
                    # 從規格名稱中提取關鍵特徵（如顏色、尺寸等）
                    規格類型 = self.規格分析.分析規格類型(規格名稱)
                    if 規格類型:
                        logger.info(f"已開啟規格: '{規格名稱}'，類型: {規格類型}，折扣價: {折扣價}，價格類型: {價格類型}")
                        # 儲存類型和價格的對應關係
                        if 規格類型 not in 已開啟規格價格表:
                            已開啟規格價格表[規格類型] = []
                        已開啟規格價格表[規格類型].append({"名稱": 規格名稱, "價格": 折扣價})
            
            logger.info(f"已開啟規格價格表: {已開啟規格價格表}")
            
            # 然後處理需要開啟的規格
            for spec in 規格列表:
                規格名稱 = spec.get('name', '')
                狀態 = spec.get('status', '')
                庫存 = spec.get('stock', '0')
                
                # 只處理庫存>0且未開啟的規格
                try:
                    庫存數字 = int(''.join(filter(str.isdigit, str(庫存))))
                except:
                    庫存數字 = 0
                
                if 庫存數字 > 0 and 狀態 != "開啟":
                    總處理數 += 1
                    logger.info(f"規格 '{規格名稱}' 狀態為 {狀態}，庫存為 {庫存數字}，需要開啟")
                    
                    # 開啟規格
                    if self.開關控制.開啟規格(商品名稱, 規格名稱):
                        開關成功數 += 1
                        logger.info(f"✓ 成功開啟規格 '{規格名稱}'")
                        
                        # 分析該規格屬於哪種類型
                        當前規格類型 = self.規格分析.分析規格類型(規格名稱)
                        logger.info(f"當前規格 '{規格名稱}' 的類型為: {當前規格類型}")
                        
                        # 找出同類型規格的價格
                        參考價格 = None
                        if 當前規格類型 and 當前規格類型 in 已開啟規格價格表:
                            # 獲取該類型的第一個價格作為參考
                            參考規格 = 已開啟規格價格表[當前規格類型][0]
                            參考價格 = 參考規格["價格"]
                            logger.info(f"找到同類型規格 '{參考規格['名稱']}' 的價格: {參考價格}")
                        
                        # 如果找不到同類型，嘗試使用任何已開啟規格的價格
                        if not 參考價格 and 已開啟規格價格表:
                            # 獲取第一個類型的第一個價格
                            第一個類型 = list(已開啟規格價格表.keys())[0]
                            參考規格 = 已開啟規格價格表[第一個類型][0]
                            參考價格 = 參考規格["價格"]
                            logger.info(f"未找到同類型規格，使用規格 '{參考規格['名稱']}' 的價格: {參考價格}")
                        
                        # 如果找到參考價格，設定折扣價
                        if 參考價格:
                            logger.info(f"嘗試將規格 '{規格名稱}' 的折扣價設為 {參考價格}")
                            
                            # 設置等待時間，確保開關操作完成
                            time.sleep(2)
                            
                            # 調整價格
                            if self.價格調整.調整商品價格(商品名稱, 規格名稱, 參考價格):
                                價格成功數 += 1
                                logger.info(f"✓ 成功設置規格 '{規格名稱}' 的折扣價為 {參考價格}")
                                
                                # 將此規格加入已開啟規格列表，以便後續參考
                                if 當前規格類型:
                                    if 當前規格類型 not in 已開啟規格價格表:
                                        已開啟規格價格表[當前規格類型] = []
                                    已開啟規格價格表[當前規格類型].append({"名稱": 規格名稱, "價格": 參考價格})
                            else:
                                logger.warning(f"⚠ 無法設置規格 '{規格名稱}' 的折扣價")
                        else:
                            logger.warning(f"⚠ 無法找到參考價格，跳過價格設定")
                    else:
                        logger.warning(f"⚠ 無法開啟規格 '{規格名稱}'")
        
        logger.info(f"批量處理完成: 總共 {總處理數} 個規格，開啟 {開關成功數} 個，調整價格 {價格成功數} 個")
        
        return 總處理數, 開關成功數, 價格成功數 