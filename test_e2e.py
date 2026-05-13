import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_e2e():
    print("=" * 50)
    print("开始端到端测试...")
    print("=" * 50)

    # 1. 注册用户
    print("\n1. 注册新用户...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✓ 用户注册成功")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    elif response.status_code == 400 and "用户名已存在" in response.text:
        print("用户已存在，继续测试...")
    else:
        print(f"✗ 注册失败: {response.text}")
        return False

    # 2. 登录获取 token
    print("\n2. 用户登录...")
    login_data = {
        "username": "testuser",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✓ 登录成功")
        print(f"Token: {access_token[:50]}...")
    else:
        print(f"✗ 登录失败: {response.text}")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. 获取当前用户信息
    print("\n3. 获取当前用户信息...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print("✓ 获取用户信息成功")
        print(f"用户ID: {user_data['id']}, 用户名: {user_data['username']}")
    else:
        print(f"✗ 获取用户信息失败: {response.text}")
        return False

    # 4. 创建投票
    print("\n4. 创建投票...")
    deadline = (datetime.utcnow() + timedelta(days=1)).isoformat()
    poll_data = {
        "title": "最喜欢的编程语言？",
        "description": "请选择你最喜欢的编程语言",
        "deadline": deadline,
        "options": [
            {"text": "Python"},
            {"text": "JavaScript"},
            {"text": "TypeScript"}
        ]
    }
    response = requests.post(f"{BASE_URL}/polls", json=poll_data, headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        poll = response.json()
        poll_id = poll["id"]
        print("✓ 投票创建成功")
        print(f"投票ID: {poll_id}, 标题: {poll['title']}")
        print("选项:")
        for opt in poll["options"]:
            print(f"  - {opt['id']}: {opt['text']}")
    else:
        print(f"✗ 创建投票失败: {response.text}")
        return False

    # 5. 获取投票列表
    print("\n5. 获取投票列表...")
    response = requests.get(f"{BASE_URL}/polls", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        polls = response.json()
        print(f"✓ 获取投票列表成功，共 {len(polls)} 个投票")
        for p in polls:
            print(f"  - {p['title']} (票数: {p['total_votes']})")
    else:
        print(f"✗ 获取投票列表失败: {response.text}")
        return False

    # 6. 投票
    print("\n6. 进行投票...")
    option_id = poll["options"][0]["id"]
    vote_data = {"option_id": option_id}
    response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json=vote_data, headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✓ 投票成功")
    elif response.status_code == 400 and "已经投过票了" in response.text:
        print("已经投过票了，继续测试...")
    else:
        print(f"✗ 投票失败: {response.text}")
        return False

    # 7. 再次获取投票详情，查看百分比
    print("\n7. 获取投票详情并验证百分比...")
    response = requests.get(f"{BASE_URL}/polls/{poll_id}", headers=headers)
    if response.status_code == 200:
        poll_detail = response.json()
        print("✓ 获取投票详情成功")
        print(f"总票数: {poll_detail['total_votes']}")
        print("\n选项统计:")
        for opt in poll_detail["options"]:
            print(f"  - {opt['text']}: {opt['vote_count']} 票 ({opt['percentage']}%)")
    else:
        print(f"✗ 获取投票详情失败: {response.text}")
        return False

    # 8. 创建第二个用户并投票来测试百分比
    print("\n8. 创建第二个用户并投票测试百分比...")
    register_data2 = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/register", json=register_data2)
    if response.status_code == 200 or "用户名已存在" in response.text:
        # 登录第二个用户
        login_data2 = {
            "username": "testuser2",
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/token", data=login_data2)
        if response.status_code == 200:
            token2 = response.json()["access_token"]
            headers2 = {"Authorization": f"Bearer {token2}"}
            
            # 第二个用户投给第二个选项
            option_id2 = poll["options"][1]["id"]
            vote_data2 = {"option_id": option_id2}
            response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json=vote_data2, headers=headers2)
            if response.status_code == 200 or "已经投过票了" in response.text:
                print("✓ 第二个用户投票成功")
                
                # 再次获取投票详情查看百分比
                response = requests.get(f"{BASE_URL}/polls/{poll_id}", headers=headers)
                poll_detail = response.json()
                print("\n最终投票统计:")
                print(f"总票数: {poll_detail['total_votes']}")
                all_percentages_ok = True
                for opt in poll_detail["options"]:
                    percentage_str = f"{opt['percentage']}"
                    print(f"  - {opt['text']}: {opt['vote_count']} 票 ({percentage_str}%)")
                    
                    # 验证百分比格式
                    if '.' in percentage_str:
                        decimal_part = percentage_str.split('.')[1]
                        if len(decimal_part) != 1:
                            print(f"    ⚠ 警告: 小数位数不是1位: {percentage_str}")
                            all_percentages_ok = False
                
                if all_percentages_ok:
                    print("✓ 所有百分比格式正确（1位小数）")
                else:
                    print("✗ 部分百分比格式需要调整")

    print("\n" + "=" * 50)
    print("✓ 端到端测试完成！")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_e2e()
