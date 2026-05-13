import requests

BASE_URL = "http://localhost:8000"

def create_test_user():
    register_data = {
        "username": "test",
        "email": "test@example.com",
        "password": "123456"
    }
    
    # 尝试注册
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    if response.status_code == 200:
        print("✓ 用户 test 创建成功")
    elif response.status_code == 400 and "用户名已存在" in response.text:
        print("用户 test 已存在")
    else:
        print(f"创建用户失败: {response.text}")
    
    # 测试登录
    print("\n测试登录:")
    login_data = {
        "username": "test",
        "password": "123456"
    }
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    if response.status_code == 200:
        print("✓ 登录成功！")
        print(f"Token: {response.json()['access_token'][:60]}...")
    else:
        print(f"登录失败: {response.status_code} - {response.text}")

if __name__ == "__main__":
    create_test_user()
