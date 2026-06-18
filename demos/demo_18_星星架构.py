# 星型架构的伪代码设计

class CentralHubAgent:
    def __init__(self):
        self.state = {"document": "", "requirements": [], "status": "init"}
        self.experts = {
            "writer": TechnicalWriterAgent(),
            "reviewer": ReviewerAgent()
        }

    def dispatch(self, user_input):
        # 1. 更新全局状态
        self.state["requirements"].append(user_input)
        
        # 2. 核心：由 Hub 动态决定下一步分配给谁（Routing）
        while self.state["status"] != "completed":
            next_action = self.llm_decide_next_step(self.state)
            
            if next_action == "call_writer":
                self.state = self.experts["writer"].execute(self.state)
            elif next_action == "call_reviewer":
                self.state = self.experts["reviewer"].execute(self.state)
            elif next_action == "output_to_user":
                self.state["status"] = "completed"
                
        return self.state["document"]