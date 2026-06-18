import re

def code_aware_semantic_splitter(text, max_token_limit=1000):
    # 1. 提取所有代码块的区间
    code_block_pattern = r"(```[a-zA-Z]*\n[\s\S]*?\n```)"
    
    # 2. 将文本按代码块占位符分割，防止切分时破坏代码结构
    blocks = re.split(code_block_pattern, text)
    
    chunks = []
    current_chunk = ""
    
    for block in blocks:
        # 如果是代码块，强行合并，不予切割
        if block.startswith("```"):
            if len(current_chunk) + len(block) > max_token_limit:
                chunks.append(current_chunk)
                current_chunk = block
            else:
                current_chunk += "\n" + block
        else:
            # 如果是普通文本，可以按照句号、换行符等进一步做轻量级切分
            # ... 文本切分逻辑 ...
            current_chunk += block
            
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks