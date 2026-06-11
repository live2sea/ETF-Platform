"""
ETF/LOF 行情加载器（简化版）

功能：
1. 获取ETF实时行情
2. 获取LOF实时行情
3. 与持仓匹配
4. 写入 ods_market_price
"""

import sqlite3
import pandas as pd
import akshare as ak
from datetime import datetime


class MarketPriceLoader:

    def __init__(self):
        self.db_path = "data/etf.db"

    # ==================================================
    # 获取当前持仓
    # ==================================================
    def get_position_codes(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT etf_code, etf_name FROM dwd_position", conn)
        conn.close()
        
        df["etf_code"] = df["etf_code"].astype(str).str.strip()
        return df

    # ==================================================
    # ETF行情
    # ==================================================
    def load_etf_market(self):
        print("开始获取ETF行情...")
        
        try:
            df = ak.fund_etf_spot_em()
            df = df[["代码", "名称", "最新价"]]
            df.columns = ["etf_code", "etf_name", "current_price"]
            df["fund_type"] = "ETF"
            df["etf_code"] = df["etf_code"].astype(str).str.strip()
            
            print(f"ETF行情数量：{len(df)}")
            return df
        except Exception as e:
            print(f"ETF行情获取失败：{e}")
            return pd.DataFrame(columns=["etf_code", "etf_name", "current_price", "fund_type"])

    # ==================================================
    # LOF行情
    # ==================================================
    def load_lof_market(self):
        print("开始获取LOF行情...")
        
        try:
            df = ak.fund_lof_spot_em()
            df = df[["代码", "名称", "最新价"]]
            df.columns = ["etf_code", "etf_name", "current_price"]
            df["fund_type"] = "LOF"
            df["etf_code"] = df["etf_code"].astype(str).str.strip()
            
            print(f"LOF行情数量：{len(df)}")
            return df
        except Exception as e:
            print(f"LOF行情获取失败：{e}")
            return pd.DataFrame(columns=["etf_code", "etf_name", "current_price", "fund_type"])

    # ==================================================
    # 合并行情
    # ==================================================
    def load_market(self):
        etf_df = self.load_etf_market()
        lof_df = self.load_lof_market()
        
        market_df = pd.concat([etf_df, lof_df], ignore_index=True)
        market_df = market_df.drop_duplicates(subset=["etf_code"])
        
        print(f"总行情数量：{len(market_df)}")
        return market_df

    # ==================================================
    # 构建结果
    # ==================================================
    def build_price(self):
        # 获取持仓和行情
        position_df = self.get_position_codes()
        market_df = self.load_market()
        
        # 合并
        result = pd.merge(position_df, market_df, on="etf_code", how="left")
        
        # 处理字段
        result = result.rename(columns={"etf_name_x": "etf_name"})
        result["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 选择最终字段
        result = result[["etf_code", "etf_name", "fund_type", "current_price", "update_time"]]
        
        return result

    # ==================================================
    # 保存数据库
    # ==================================================
    def save_result(self, result):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM ods_market_price")
        result.to_sql("ods_market_price", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()
        print(f"已保存 {len(result)} 条行情数据")

    # ==================================================
    # 显示结果
    # ==================================================
    def print_result(self, result):
        print("\n" + "=" * 80)
        print("持仓行情")
        print("=" * 80)
        
        # 格式化显示
        display_df = result.copy()
        display_df["current_price"] = display_df["current_price"].apply(
            lambda x: f"{x:.3f}" if pd.notna(x) else "N/A"
        )
        print(display_df[["etf_code", "etf_name", "fund_type", "current_price"]].to_string(index=False))
        
        # 检查缺失
        missing = result[result["current_price"].isna()]
        if len(missing) > 0:
            print("\n" + "=" * 80)
            print("缺失行情基金")
            print("=" * 80)
            print(missing[["etf_code", "etf_name"]].to_string(index=False))

    # ==================================================
    # 主流程
    # ==================================================
    def run(self):
        print("开始获取行情...\n")
        
        result = self.build_price()
        self.save_result(result)
        self.print_result(result)
        
        print(f"\n成功获取 {len(result)} 个持仓行情")


if __name__ == "__main__":
    MarketPriceLoader().run()