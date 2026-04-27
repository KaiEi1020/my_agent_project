import requests
import zai
import os
from zai import ZhipuAiClient
from dotenv import load_dotenv
from test_class import TestClass


load_dotenv()  # 加载 .env 文件   

def fetch_data():
    # 换成国内更稳定的名言 API：一言 (Hitokoto)
    url = "https://v1.hitokoto.cn/"
    
    try:
        # Action: 执行请求
        response = requests.get(url, timeout=5) # 设置 5 秒超时，防止 Agent 死等
        
        # Observation: 观察结果
        if response.status_code == 200:
            data = response.json()
            print("--- Agent 获取到新知识 (Hitokoto) ---")
            print(f"内容: {data['hitokoto']}")
            print(f"来源: {data['from']}")
        else:
            print(f"获取失败，错误码: {response.status_code}")
            
    except Exception as e:
        # Reflection: 错误捕获与分析
        print(f"感知到异常: 网络似乎不通，或者域名解析失败了。")
        print(f"具体错误信息: {e}")

def testGLM():
    try:
        print(zai.__version__)
        client = ZhipuAiClient(api_key=os.getenv("ZAI_API_KEY"))
        response = client.chat.completions.create(
            model="glm-4.6v",
            messages=[
                {"role": "user", "content": "请帮我写一个..."}
            ]
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"具体错误信息: {e}")



if __name__ == "__main__":
    test = TestClass()
    test.run()
    # testGLM()
    # fetch_data()
    