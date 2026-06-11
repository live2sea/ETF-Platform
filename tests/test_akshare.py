import akshare as ak

df = ak.fund_etf_spot_em()

print(df.head())
print(df.columns.tolist())