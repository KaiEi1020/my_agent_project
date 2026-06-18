from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# 🔒 子图的独立状态：里面的变量外部大图看不见！
class OCRSubState(TypedDict):
    raw_images: list[str]
    extracted_text: str
    ocr_confidence: float  # 临时变量：置信度


# 子图内部的打工人节点
def ocr_processor(state: OCRSubState):
    print("\n   [子图节点: OCR 处理器] 正在解析图片...")
    # 模拟提取
    return {"extracted_text": "公司2025年净利润增长10%", "ocr_confidence": 0.98}


# 编排子图
ocr_subgraph_builder = StateGraph(OCRSubState)
ocr_subgraph_builder.add_node("ocr_processor", ocr_processor)
ocr_subgraph_builder.add_edge(START, "ocr_processor")
ocr_subgraph_builder.add_edge("ocr_processor", END)

ocr_subgraph = ocr_subgraph_builder.compile()


# 🌐 全局大图的状态
class MainState(TypedDict):
    pdf_path: str
    extracted_text: str
    audit_report: str  # 最终报告


# 大图 wrapper 节点：负责主图状态 <-> 子图状态的输入/输出转换
def ocr_team_wrapper(state: MainState):
    print("\n[主图节点: OCR 团队 Wrapper] 正在把 PDF 转成子图输入...")

    subgraph_input: OCRSubState = {
        "raw_images": [f"{state['pdf_path']}#page=1"],
        "extracted_text": "",
        "ocr_confidence": 0.0,
    }
    subgraph_output = ocr_subgraph.invoke(subgraph_input)

    print(
        "[主图节点: OCR 团队 Wrapper] "
        f"OCR 置信度：{subgraph_output['ocr_confidence']}"
    )
    return {"extracted_text": subgraph_output["extracted_text"]}


# 大图的普通节点：报告生成器
def report_generator(state: MainState):
    print("\n[主图节点: 报告生成器] 正在根据提取内容生成审计报告...")
    return {"audit_report": f"【审计通过】识别内容：{state['extracted_text']}。"}


# 编排大图
main_workflow = StateGraph(MainState)

# 💡 核心：通过 wrapper 节点把独立子图接入主图！
main_workflow.add_node("ocr_team", ocr_team_wrapper)
main_workflow.add_node("report_generator", report_generator)

main_workflow.add_edge(START, "ocr_team")
main_workflow.add_edge("ocr_team", "report_generator")
main_workflow.add_edge("report_generator", END)

main_app = main_workflow.compile()


if __name__ == "__main__":
    result = main_app.invoke({"pdf_path": "mock_audit_report.pdf"})
    print("\n最终结果:")
    print(result)
