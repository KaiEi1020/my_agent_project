import os

import zai
from dotenv import load_dotenv
from zai import ZhipuAiClient


load_dotenv()


def run_demo():
    try:
        print(zai.__version__)
        client = ZhipuAiClient(api_key=os.getenv("ZAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.getenv("ZAI_MODEL"),
            messages=[{"role": "user", "content": "请帮我写一首诗..."}],
        )
        print(response.choices[0].message.content)
    except Exception as error:
        print(f"具体错误信息：{error}")


if __name__ == "__main__":
    run_demo()
