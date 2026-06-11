import socket
import requests

# 1. 测试DNS解析
print("1. 测试DNS解析...")
try:
    ip = socket.gethostbyname('push2.eastmoney.com')
    print(f"   ✅ 解析成功: {ip}")
except Exception as e:
    print(f"   ❌ 解析失败: {e}")

# 2. 测试网络连接
print("\n2. 测试网络连接...")
try:
    response = requests.get('https://www.baidu.com', timeout=5)
    print(f"   ✅ 百度连接成功: {response.status_code}")
except Exception as e:
    print(f"   ❌ 百度连接失败: {e}")

# 3. 测试东方财富连接
print("\n3. 测试东方财富连接...")
try:
    response = requests.get('https://push2.eastmoney.com', timeout=5)
    print(f"   ✅ 东方财富连接成功")
except Exception as e:
    print(f"   ❌ 东方财富连接失败: {e}")