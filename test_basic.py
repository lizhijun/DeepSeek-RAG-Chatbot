import requests

# 测试文档列表API
response = requests.get("http://localhost:5005/api/documents")
print(f"文档列表API响应: {response.status_code}")
print(response.json())

# 测试聊天API
response = requests.post(
    "http://localhost:5005/api/chat",
    json={"query": "Hello, how are you?"}
)
print(f"聊天API响应: {response.status_code}")
if response.status_code == 200:
    print(response.json())
else:
    print(response.text) 