#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Excel輸出模組 - 負責將處理結果匯出成Excel檔案
用於記錄商品調價的歷史紀錄

包含功能:
- 生成調整記錄的Excel檔案
- 支援各種格式化和樣式設定
"""

import os
import time
import logging
import pandas as pd
from datetime import datetime

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Excel輸出")

class Excel處理:
    """Excel處理類，提供Excel匯出與格式化功能"""
    
    def __init__(self):
        """初始化Excel處理物件"""
        self.報表目錄 = "報表"  # 預設報表儲存目錄
        
        # 確保報表目錄存在
        self._確保目錄存在(self.報表目錄)
    
    def _確保目錄存在(self, 目錄):
        """確保指定的目錄存在，若不存在則自動創建"""
        if not os.path.exists(目錄):
            try:
                os.makedirs(目錄)
                logger.info(f"已創建報表目錄: {目錄}")
            except Exception as e:
                logger.error(f"無法創建目錄 {目錄}: {str(e)}")
    
    def 生成調整記錄Excel(self, 調整記錄列表):
        """將調整記錄列表匯出成Excel檔案
        
        參數:
            調整記錄列表 (list): 包含調整記錄字典的列表
            
        返回:
            str: 儲存的檔案路徑，若失敗則返回None
        """
        if not 調整記錄列表:
            logger.warning("調整記錄列表為空，無法生成Excel")
            return None
        
        try:
            # 檔案名稱包含日期和時間
            現在時間 = datetime.now().strftime("%Y%m%d_%H%M%S")
            檔案名稱 = f"調價記錄_{現在時間}.xlsx"
            檔案路徑 = os.path.join(self.報表目錄, 檔案名稱)
            
            # 將記錄列表轉換為DataFrame
            df = pd.DataFrame(調整記錄列表)
            
            # 重新排序欄位
            欄位順序 = ["調整時間", "商品名稱", "規格名稱", "原價格", "輸入價格", "調整結果"]
            有效欄位 = [col for col in 欄位順序 if col in df.columns]
            df = df[有效欄位]
            
            # 寫入Excel
            with pd.ExcelWriter(檔案路徑, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="調價記錄", index=False)
                
                # 獲取工作表物件
                worksheet = writer.sheets["調價記錄"]
                
                # 設置欄寬
                worksheet.column_dimensions['A'].width = 20  # 調整時間
                worksheet.column_dimensions['B'].width = 30  # 商品名稱
                worksheet.column_dimensions['C'].width = 30  # 規格名稱
                worksheet.column_dimensions['D'].width = 15  # 原價格
                worksheet.column_dimensions['E'].width = 15  # 輸入價格
                worksheet.column_dimensions['F'].width = 12  # 調整結果
            
            logger.info(f"調價記錄已儲存至: {檔案路徑}")
            return 檔案路徑
            
        except Exception as e:
            logger.error(f"生成Excel時發生錯誤: {str(e)}")
            import traceback
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            return None
    
    def 添加調整統計摘要(self, 檔案路徑, 總處理數, 開關成功數, 價格成功數):
        """在Excel中添加統計摘要資訊
        
        參數:
            檔案路徑 (str): Excel檔案路徑
            總處理數 (int): 總處理規格數量
            開關成功數 (int): 成功設定開關的數量
            價格成功數 (int): 成功調整價格的數量
        """
        if not os.path.exists(檔案路徑):
            logger.warning(f"找不到檔案: {檔案路徑}")
            return False
            
        try:
            # 讀取現有Excel
            excel = pd.ExcelFile(檔案路徑)
            with pd.ExcelWriter(檔案路徑, engine='openpyxl', mode='a') as writer:
                # 創建摘要工作表
                摘要數據 = {
                    "項目": ["總處理規格數", "開關設定成功數", "價格調整成功數", "處理時間"],
                    "數值": [總處理數, 開關成功數, 價格成功數, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                }
                
                摘要df = pd.DataFrame(摘要數據)
                摘要df.to_excel(writer, sheet_name="處理摘要", index=False)
                
                # 設置工作表格式
                worksheet = writer.sheets["處理摘要"]
                worksheet.column_dimensions['A'].width = 20
                worksheet.column_dimensions['B'].width = 25
            
            logger.info(f"已添加處理摘要至: {檔案路徑}")
            return True
            
        except Exception as e:
            logger.error(f"添加摘要時發生錯誤: {str(e)}")
            return False

# 測試代碼
if __name__ == "__main__":
    # 測試資料
    測試記錄 = [
        {
            "商品名稱": "測試商品1",
            "規格名稱": "規格A",
            "原價格": "100",
            "輸入價格": "85",
            "調整結果": True,
            "調整時間": "2023-01-01 12:00:00"
        },
        {
            "商品名稱": "測試商品1",
            "規格名稱": "規格B",
            "原價格": "120",
            "輸入價格": "99",
            "調整結果": False,
            "調整時間": "2023-01-01 12:01:00"
        }
    ]
    
    excel處理 = Excel處理()
    檔案路徑 = excel處理.生成調整記錄Excel(測試記錄)
    
    if 檔案路徑:
        excel處理.添加調整統計摘要(檔案路徑, 2, 1, 1)
        print(f"測試Excel已生成: {檔案路徑}") 