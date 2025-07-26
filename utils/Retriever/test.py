import os
from retriever import create_rag_retriever

if __name__ == "__main__":
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docx_file = os.path.join(script_dir, "input.docx")
    
    # 创建检索器
    retrieve_answer = create_rag_retriever(docx_file)
    
    # 简单测试
    test_question = "什么是机器学习？"
    print(f"问题: {test_question}")
    print(f"答案: {retrieve_answer(test_question)}")    