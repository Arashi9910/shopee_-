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
    
    def 批量處理商品規格(self, 商品資料列表):
        """批量處理多個商品的開關和價格設定
        
        參數:
            商品資料列表: 包含商品資料的列表
            
        返回:
            tuple: (處理總數, 開關成功數, 價格成功數, 調整記錄列表)
        """
        if not 商品資料列表:
            logger.warning("批量處理傳入的商品列表為空")
            return (0, 0, 0, [])
            
        總處理規格數 = 0
        開關成功數 = 0
        價格成功數 = 0
        調整記錄列表 = []
        
        for product_idx, 商品 in enumerate(商品資料列表):
            商品名稱 = 商品.get("name", f"未命名商品_{product_idx}")
            規格清單 = 商品.get("specs", [])
            
            logger.info(f"處理第 {product_idx + 1}/{len(商品資料列表)} 個商品: {商品名稱}")
            
            # 檢查規格清單是否為空
            if not 規格清單:
                logger.warning(f"商品 '{商品名稱}' 沒有規格資料，跳過處理")
                continue
                
            # 處理每個規格
            for spec_idx, 規格 in enumerate(規格清單):
                規格名稱 = 規格.get("name", f"未命名規格_{spec_idx}")
                參考價格 = 規格.get("price", 0)
                
                # 確保參考價格是數字類型
                try:
                    # 如果是字符串，轉換為數字
                    if isinstance(參考價格, str):
                        # 移除非數字字符（例如貨幣符號）
                        參考價格 = 參考價格.replace(',', '')
                        參考價格 = ''.join(c for c in 參考價格 if c.isdigit() or c == '.')
                        參考價格 = float(參考價格) if 參考價格 else 0
                    參考價格 = float(參考價格)  # 確保轉換為浮點數
                except (ValueError, TypeError):
                    logger.warning(f"⚠ 規格 '{規格名稱}' 的參考價格 '{規格.get('price')}' 無法轉換為數字，設為0")
                    參考價格 = 0
                
                # 增加規格處理計數
                總處理規格數 += 1
                
                logger.info(f"處理規格 [{spec_idx + 1}/{len(規格清單)}]: '{規格名稱}'，參考價格: {參考價格}")
                
                # 1. 處理開關
                if self.開關控制.控制商品規格開關(商品名稱, 規格名稱, True):
                    開關成功數 += 1
                    logger.info(f"✓ 規格 '{規格名稱}' 開關設定成功")
                else:
                    logger.warning(f"✗ 規格 '{規格名稱}' 開關設定失敗")
                
                # 2. 處理價格
                if 參考價格 > 0:
                    價格調整結果 = self.價格調整.調整商品價格(商品名稱, 規格名稱, 參考價格)
                    
                    # 判斷是否返回了調整記錄
                    if isinstance(價格調整結果, tuple) and len(價格調整結果) == 2:
                        價格成功 = 價格調整結果[0]
                        調整記錄 = 價格調整結果[1]
                        調整記錄列表.append(調整記錄)
                    else:
                        價格成功 = 價格調整結果
                    
                    if 價格成功:
                        價格成功數 += 1
                        logger.info(f"✓ 規格 '{規格名稱}' 價格設為 {參考價格} 成功")
                    else:
                        logger.warning(f"✗ 規格 '{規格名稱}' 價格設定失敗")
                else:
                    logger.warning(f"⚠ 規格 '{規格名稱}' 參考價格為零或負值 ({參考價格})，跳過價格設定")
                
                # 操作間隔，避免過度頻繁操作
                time.sleep(0.5)
        
        # 返回處理結果
        logger.info(f"批量處理完成: 共處理 {總處理規格數} 個規格，成功設定開關 {開關成功數} 個，成功設定價格 {價格成功數} 個")
        return (總處理規格數, 開關成功數, 價格成功數, 調整記錄列表) 