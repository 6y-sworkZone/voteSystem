import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_various_percentages():
    print("=" * 50)
    print("测试各种百分比格式")
    print("=" * 50)

    # 登录用户
    users = []
    for i in range(1, 4):
        username = f"user{i}"
        email = f"user{i}@test.com"
        
        # 尝试注册
        register_data = {
            "username": username,
            "email": email,
            "password": "test123"
        }
        requests.post(f"{BASE_URL}/register", json=register_data)
        
        # 登录
        login_data = {"username": username, "password": "test123"}
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        token = response.json()["access_token"]
        users.append({"username": username, "token": token})
        print(f"✓ 用户 {i} 登录成功")

    # 创建投票（3个选项）
    headers = {"Authorization": f"Bearer {users[0]['token']}"}
    deadline = (datetime.utcnow() + timedelta(days=1)).isoformat()
    poll_data = {
        "title": "最佳前端框架？",
        "description": "选择你认为最好的",
        "deadline": deadline,
        "options": [
            {"text": "React"},
            {"text": "Vue"},
            {"text": "Angular"}
        ]
    }
    response = requests.post(f"{BASE_URL}/polls", json=poll_data, headers=headers)
    poll = response.json()
    poll_id = poll["id"]
    print(f"\n✓ 创建投票成功，ID: {poll_id}")

    # 3个用户分别投票给不同选项（每个选项1票，各33.3%）
    for i, user in enumerate(users):
        option_id = poll["options"][i]["id"]
        user_headers = {"Authorization": f"Bearer {user['token']}"}
        vote_data = {"option_id": option_id}
        requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json=vote_data, headers=user_headers)
        print(f"✓ {user['username']} 投给了: {poll['options'][i]['text']}")

    # 获取结果
    response = requests.get(f"{BASE_URL}/polls/{poll_id}", headers=headers)
    poll_detail = response.json()
    print(f"\n投票结果（总票数: {poll_detail['total_votes']}）:")
    print("-" * 40)
    
    all_ok = True
    for opt in poll_detail["options"]:
        percentage = opt["percentage"]
        percentage_str = f"{percentage}"
        
        # 检查是否有1位小数
        if '.' in percentage_str:
            decimal_part = percentage_str.split('.')[1]
            if len(decimal_part) != 1:
                print(f"✗ {opt['text']}: {opt['vote_count']} 票 ({percentage_str}%) - 小数位数不对")
                all_ok = False
            else:
                print(f"✓ {opt['text']}: {opt['vote_count']} 票 ({percentage_str}%)")
        else:
            # 整数的话，检查前端是否会显示为 x.0
            print(f"⚠ {opt['text']}: {opt['vote_count']} 票 ({percentage_str}%) - 是整数")

    print("-" * 40)
    
    # 再测试：2票给选项1，1票给选项2 = 66.7% 和 33.3%
    print("\n创建第二个投票测试66.7% / 33.3%:")
    
    poll2_data = {
        "title": "喜欢的颜色？",
        "deadline": deadline,
        "options": [
            {"text": "蓝色"},
            {"text": "红色"}
        ]
    }
    response = requests.post(f"{BASE_URL}/polls", json=poll2_data, headers=headers)
    poll2 = response.json()
    poll2_id = poll2["id"]
    
    # user1和user2投给蓝色，user3投给红色
    for i in range(2):
        user_headers = {"Authorization": f"Bearer {users[i]['token']}"}
        requests.post(f"{BASE_URL}/polls/{poll2_id}/vote", json={"option_id": poll2["options"][0]["id"]}, headers=user_headers)
    
    user_headers = {"Authorization": f"Bearer {users[2]['token']}"}
    requests.post(f"{BASE_URL}/polls/{poll2_id}/vote", json={"option_id": poll2["options"][1]["id"]}, headers=user_headers)
    
    response = requests.get(f"{BASE_URL}/polls/{poll2_id}", headers=headers)
    poll2_detail = response.json()
    print(f"投票结果（总票数: {poll2_detail['total_votes']}）:")
    print("-" * 40)
    
    for opt in poll2_detail["options"]:
        percentage = opt["percentage"]
        percentage_str = f"{percentage}"
        print(f"✓ {opt['text']}: {opt['vote_count']} 票 ({percentage_str}%)")
        
        # 验证66.7和33.3
        if opt["vote_count"] == 2 and abs(percentage - 66.7) > 0.1:
            print(f"  期望值约为66.7%")
            all_ok = False
        if opt["vote_count"] == 1 and abs(percentage - 33.3) > 0.1:
            print(f"  期望值约为33.3%")
            all_ok = False

    print("-" * 40)
    
    if all_ok:
        print("\n✓ 所有百分比格式验证通过！")
    else:
        print("\n✗ 部分百分比需要检查")
    
    return all_ok

if __name__ == "__main__":
    test_various_percentages()
