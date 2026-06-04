# my_agent_project
> agent 学习项目

## 虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv
# 激活虚拟环境(激活虚拟环境后， pip 会自动指向 Python 3 版本)
source venv/bin/activate
```

```bash
# 重新激活虚拟环境
deactivate
source venv/bin/activate
```

## 包管理
1. 是一个 `uv` 进行包管理
```bash
# 安装uv
brew install uv

# 安装新依赖
uv add requests

# 安装开发依赖
uv add pytest --dev

# 卸载依赖
uv remove requests

# 根据锁文件自动安装或清理
uv sync

# 查看已安装的包
uv pip list 
uv tree #(以树状图展示依赖关系，极清晰)
```

# 项目启动
```bash
# 安装依赖
uv sync

# 运行项目
uv run main.py

uv run python -m src.my_agent_langchain.weather_agent
```
