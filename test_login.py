import requests

BASE_URL = "http://localhost:8000"

def test_login():
    # 先测试 Python requests 方式登录
    print("测试后端登录接口...")
    login_data = {
        "username": "testuser",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✓ 后端登录成功")
        print(f"响应: {response.json()}")
    else:
        print(f"✗ 登录失败: {response.text}")
    
    # 模拟前端发送 JSON 的情况（会失败）
    print("\n模拟前端用 JSON 发送（应该失败）:")
    response = requests.post(f"{BASE_URL}/token", json=login_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 422:
        print("✓ 确认: 发送 JSON 会导致 422 错误")
        print(f"错误详情: {response.json()}")

if __name__ == "__main__":
    test_login()
