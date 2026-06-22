# 💡 2026 生产级安全沙箱执行骨架
from e2b import Sandbox

def execute_agent_code(generated_code: str):
    print("\n[Node: 🛡️ 安全执行器] 正在初始化 E2B 隔离沙箱...")
    
    # 1. 一键启动一个完全隔离的微型沙箱环境
    with Sandbox() as sbx:
        print(f"🚀 安全隔离舱已就绪，正在安全运行代码...")
        
        # 2. 在沙箱内部执行 AI 生成的代码
        execution = sbx.run_python(generated_code)
        
        # 3. 检查沙箱内部是否有报错或恶意越界行为
        if execution.error:
            return f"安全拦截：代码在沙箱内运行失败: {execution.error.message}"
        
        # 4. 只把安全的标准输出（stdout）拿回来
        print("✅ 沙箱安全运行完毕，成功提取结果。")
        return execution.stdout

# 💡 此时，即使代码里有 'rm -rf /'，也只能在沙箱虚拟舱里自嗨，
# 沙箱生命周期一结束，连同病毒一起灰飞烟灭，主服务器稳如泰山！