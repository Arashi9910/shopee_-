"""
規格分析模組

包含與商品規格分析相關的功能：
- 格式化商品資訊
- 分析規格類型
- 查找同類規格價格
"""

import logging
import re

# 設置日誌
logger = logging.getLogger(__name__)

class 規格分析:
    """處理商品規格分析相關功能的類"""
    
    def __init__(self, driver):
        """初始化規格分析類
        
        Args:
            driver: Selenium WebDriver實例
        """
        self.driver = driver
    
    def 格式化商品資訊(self, products):
        """格式化商品和規格信息，用於顯示在UI上
        
        Args:
            products (list): 商品列表
            
        Returns:
            str: 格式化後的商品和規格信息
        """
        # 獲取最大規格名稱長度，用於格式化
        max_name_length = 40
        for product in products:
            for spec in product.get('specs', []):
                name_length = len(spec.get('name', ''))
                if name_length > max_name_length:
                    max_name_length = name_length
        
        # 建立表頭和分隔線
        output = []
        header_line = "-" * 80
        table_format = f"{{:<{max_name_length}}} | {{:<10}} | {{:<15}} | {{:<10}} | {{:<15}}"
        
        # 遍歷每個商品和規格
        for product in products:
            product_name = product.get('name', '未知商品')
            output.append(f"【{product_name}】")
            output.append(header_line)
            output.append(table_format.format("規格名稱", "庫存", "價格", "狀態", "需要操作"))
            output.append(header_line)
            
            # 處理商品的規格
            specs = product.get('specs', [])
            if not specs:
                output.append("無規格信息")
                output.append(header_line)
                continue
            
            for spec in specs:
                try:
                    # 提取規格信息
                    spec_name = spec.get('name', '未知規格')
                    stock = spec.get('stock', '0')
                    price_display = spec.get('priceDisplay', '')
                    
                    # 修正價格顯示問題
                    if price_display == 'NT$' or not price_display:
                        # 嘗試使用discountPrice或price
                        discount_price = spec.get('discountPrice', '')
                        price = spec.get('price', '')
                        if discount_price:
                            price_display = f"NT${discount_price}"
                        elif price:
                            price_display = f"NT${price}"
                        else:
                            price_display = "未知價格"
                    
                    # 規格狀態
                    status = spec.get('status', '關閉')
                    disabled = spec.get('disabled', False)
                    status_display = f"{status}{'(禁用)' if disabled else ''}"
                    
                    # 計算建議動作
                    action = self._計算建議操作(spec)
                    
                    # 輸出規格行
                    output.append(table_format.format(
                        spec_name,
                        stock,
                        price_display,
                        status_display,
                        action
                    ))
                except Exception as e:
                    logger.error(f"格式化規格信息時出錯: {str(e)}")
                    output.append(f"[格式化錯誤: {str(e)}]")
            
            output.append(header_line)
        
        if not products:
            output.append("未找到任何商品")
        
        return "\n".join(output)
    
    def 分析規格類型(self, spec_name):
        """分析規格名稱，確定其類型（如顏色、尺寸、款式等）
        
        Args:
            spec_name (str): 規格名稱
            
        Returns:
            str: 規格類型（顏色、尺寸、款式等）
        """
        # 去除可能的空格和特殊字符
        spec_name = spec_name.strip()
        if not spec_name:
            return None
            
        # 尺寸相關關鍵詞
        尺寸關鍵詞 = ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "F", "一般", "均碼",
                    "小號", "中號", "大號", "加大", "標準", "特大", "細碼", "大碼",
                    "碼", "寸", "號", "size", "SIZE", "Size"]
        
        # 顏色相關關鍵詞
        顏色關鍵詞 = ["色", "白", "黑", "紅", "黃", "藍", "綠", "紫", "灰", "棕", "粉", 
                    "橙", "橘", "米", "銀", "金", "咖啡", "膚", "卡其", "杏", "醬",
                    "color", "COLOR", "Color", "咖啡色", "紅色", "黃色", "綠色"]
        
        # 款式相關關鍵詞
        款式關鍵詞 = ["款", "版", "型", "樣", "圖", "花", "圖案", "印花", "刺繡", "字母",
                    "圓領", "V領", "短袖", "長袖", "無袖", "高領", "連帽", "背心", "裙", 
                    "褲", "套裝", "外套", "襯衫", "T恤", "上衣", "吊帶", "洋裝", "禮服"]
                    
        # 檢查是否包含尺寸關鍵詞
        for keyword in 尺寸關鍵詞:
            if keyword in spec_name:
                return "尺寸"
                
        # 檢查是否包含顏色關鍵詞
        for keyword in 顏色關鍵詞:
            if keyword in spec_name:
                return "顏色"
                
        # 檢查是否包含款式關鍵詞
        for keyword in 款式關鍵詞:
            if keyword in spec_name:
                return "款式"
        
        # 如果無法確定類型，嘗試根據規格名稱中的數字或字母特徵判斷
        # 如果包含數字和單位，可能是尺寸
        if re.search(r'\d+(\.\d+)?(cm|mm|吋|寸|英寸)?', spec_name):
            return "尺寸"
            
        # 預設返回一個通用類型
        return "通用"
    
    def 查找同類規格價格(self, 商品, 目標規格名稱):
        """智能查找相同商品下類似規格的價格
        
        處理原則:
        1. 首先根據規格類型匹配 (相同 > 包含關係 > 無關)
        2. 如果所有規格價格都相同，則直接使用統一價格
        3. 如果找不到匹配規格但有其他開啟規格，默認價格保持一致
        
        Args:
            商品 (dict): 商品信息
            目標規格名稱 (str): 目標規格名稱
            
        Returns:
            tuple: (建議價格, 參考規格名稱, 是否需要調整)
        """
        目標規格類型 = self.分析規格類型(目標規格名稱)
        logger.info(f"目標規格 '{目標規格名稱}' 的類型識別為: '{目標規格類型}'")
        
        所有規格 = 商品.get('specs', [])
        同類規格列表 = []
        所有有效規格 = []  # 所有開啟且有價格的規格
        
        # 當前規格現有價格
        當前價格 = None
        當前規格對象 = None
        for spec in 所有規格:
            if spec.get('name', '') == 目標規格名稱:
                當前規格對象 = spec
                當前價格 = spec.get('price', '0')
                當前價格類型 = spec.get('priceType', '')
                
                # 如果價格是折扣率，嘗試使用計算價格
                if 當前價格類型 == '折扣率值' and float(當前價格) < 10:
                    原價 = spec.get('originalPrice', '')
                    if 原價:
                        # 計算實際折扣價格
                        當前價格 = round(float(原價) * float(當前價格) / 10)
                    else:
                        # 如果無法計算，記錄為0
                        當前價格 = 0
                else:
                    # 提取數字部分
                    try:
                        當前價格 = int(''.join(filter(str.isdigit, str(當前價格))))
                    except:
                        當前價格 = 0
                break
        
        # 收集所有有效規格並查找同類規格
        for spec in 所有規格:
            規格名稱 = spec.get('name', '')
            if 規格名稱 != 目標規格名稱:  # 排除目標規格自身
                規格類型 = self.分析規格類型(規格名稱)
                規格價格 = spec.get('price', '0')
                規格價格類型 = spec.get('priceType', '')
                規格狀態 = spec.get('status', '') == '開啟'
                
                # 處理折扣率類型的價格
                if 規格價格類型 == '折扣率值' and float(規格價格) < 10:
                    原價 = spec.get('originalPrice', '')
                    if 原價:
                        # 計算實際折扣價格
                        規格價格 = round(float(原價) * float(規格價格) / 10)
                    else:
                        # 如果無法計算，記錄為0
                        規格價格 = 0
                else:
                    # 提取價格數字部分
                    try:
                        規格價格 = int(''.join(filter(str.isdigit, str(規格價格))))
                    except:
                        規格價格 = 0
                
                # 只考慮價格大於0且狀態為開啟的規格
                if 規格價格 > 0 and 規格狀態:
                    logger.info(f"有效規格: '{規格名稱}' (類型: '{規格類型}') 價格: {規格價格}")
                    
                    # 添加到所有有效規格
                    所有有效規格.append({
                        "名稱": 規格名稱,
                        "類型": 規格類型,
                        "價格": 規格價格
                    })
                    
                    # 檢查是否為同類規格
                    if 規格類型 == 目標規格類型:
                        logger.info(f"找到同類規格: '{規格名稱}' 價格: {規格價格}")
                        同類規格列表.append({
                            "名稱": 規格名稱,
                            "類型": 規格類型,
                            "價格": 規格價格,
                            "相似度": 100  # 完全相同的類型
                        })
                    elif 規格類型 in 目標規格類型 or 目標規格類型 in 規格類型:
                        # 計算包含關係的相似度
                        相似度 = min(len(規格類型), len(目標規格類型)) / max(len(規格類型), len(目標規格類型)) * 100
                        logger.info(f"找到部分相似規格: '{規格名稱}' 相似度: {相似度:.1f}% 價格: {規格價格}")
                        同類規格列表.append({
                            "名稱": 規格名稱,
                            "類型": 規格類型,
                            "價格": 規格價格,
                            "相似度": 相似度
                        })
        
        # 按相似度排序同類規格
        同類規格列表.sort(key=lambda x: x["相似度"], reverse=True)
        
        # 檢查所有有效規格的價格是否都相同
        價格統一 = False
        統一價格 = 0
        if 所有有效規格:
            價格列表 = [規格["價格"] for 規格 in 所有有效規格]
            if len(set(價格列表)) == 1:  # 如果所有價格都相同
                價格統一 = True
                統一價格 = 價格列表[0]
                logger.info(f"所有規格價格都是 {統一價格}")
        
        # 決定建議價格
        建議價格 = 0
        參考規格名稱 = ""
        需要調整 = False
        
        # 首先查找最匹配的同類規格
        if 同類規格列表:
            最匹配規格 = 同類規格列表[0]
            建議價格 = 最匹配規格["價格"]
            參考規格名稱 = 最匹配規格["名稱"]
            logger.info(f"基於最匹配規格 '{參考規格名稱}' 建議價格: {建議價格}")
            
            # 檢查是否需要調整
            if 當前價格 != 建議價格:
                需要調整 = True
                logger.info(f"需要調整價格: 當前 {當前價格} -> 建議 {建議價格}")
            else:
                logger.info(f"價格已經一致，不需要調整")
                
        # 如果沒有同類規格但價格統一，使用統一價格
        elif 價格統一:
            建議價格 = 統一價格
            參考規格名稱 = "所有規格統一價格"
            logger.info(f"使用所有規格統一價格: {建議價格}")
            
            # 檢查是否需要調整
            if 當前價格 != 建議價格:
                需要調整 = True
                logger.info(f"需要調整價格: 當前 {當前價格} -> 建議 {建議價格}")
            else:
                logger.info(f"價格已經一致，不需要調整")
                
        # 如果有其他有效規格，使用第一個有效規格的價格
        elif 所有有效規格:
            建議價格 = 所有有效規格[0]["價格"]
            參考規格名稱 = 所有有效規格[0]["名稱"]
            logger.info(f"使用第一個有效規格 '{參考規格名稱}' 的價格: {建議價格}")
            
            # 檢查是否需要調整
            if 當前價格 != 建議價格:
                需要調整 = True
                logger.info(f"需要調整價格: 當前 {當前價格} -> 建議 {建議價格}")
            else:
                logger.info(f"價格已經一致，不需要調整")
        
        # 如果仍然沒有建議價格，但當前規格有價格，保持原價
        elif 當前價格 and 當前價格 > 0:
            建議價格 = 當前價格
            參考規格名稱 = "保持原價"
            logger.info(f"沒有參考規格，保持原價: {建議價格}")
            需要調整 = False
        
        # 最終情況：使用默認價格
        else:
            建議價格 = 499  # 使用一個默認價格
            參考規格名稱 = "默認價格"
            logger.info(f"沒有參考規格，使用默認價格: {建議價格}")
            
            # 檢查是否需要調整
            if 當前價格 != 建議價格:
                需要調整 = True
                logger.info(f"需要調整價格: 當前 {當前價格} -> 建議 {建議價格}")
            else:
                logger.info(f"價格已經一致，不需要調整")
        
        return 建議價格, 參考規格名稱, 需要調整 

    def _計算建議操作(self, spec):
        """根據規格信息計算建議操作
        
        Args:
            spec (dict): 規格信息字典
            
        Returns:
            str: 建議操作
        """
        # 提取規格信息
        stock = spec.get('stock', '0')
        status = spec.get('status', '關閉')
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
        elif stock_number > 0 and disabled:
            action = "無法開啟(已禁用)"
        else:
            action = "正常"
        
        return action 