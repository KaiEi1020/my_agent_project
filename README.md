# my_agent_project

```bash
# 创建虚拟环境
python3 -m venv venv
# 激活虚拟环境(激活虚拟环境后， pip 会自动指向 Python 3 版本)
source venv/bin/activate
```

```bash
# 定期运行，更新依赖列表
pip freeze > requirements.txt

# 从 requirements.txt 安装所有依赖
pip install -r requirements.txt
```

```bash
# 重新激活虚拟环境
deactivate
source venv/bin/activate
```