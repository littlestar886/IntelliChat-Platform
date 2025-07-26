from classifier import TextClassifier
from data_utils import DataAugmenter

def main():
    # 配置参数
    model_path = r'D:\Downloads\bert-base-chinese-finetuned'
    
    # 初始化分类器
    classifier = TextClassifier(model_path, num_labels=2)
    
    # 加载模型
    if not classifier.load_model():
        return
    
    # 示例数据
    questions = [
        # Weather/Environment (1)
        "上海明天的气温是多少？", 
        "洛杉矶现在下雨了吗？",
        "台风路径实时查询",
        "未来一周广州的天气预报",
        "当前北极的臭氧层状况如何？",
        # Technology/Software (0)
        "如何安装Python环境？",
        "TensorFlow和PyTorch哪个更好？",
        "怎样实现一个简单的神经网络？",
        "如何优化深度学习模型的性能？",
        "RAG系统是如何工作的？"
    ]
    
    labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]  # 1需要检索 0直接生成
    
    # 初始化数据增强器
    augmenter = DataAugmenter()
    
    # 训练模型
    classifier.train(questions, labels, batch_size=4, epochs=5, augmenter=augmenter)
    
    # 保存模型
    classifier.save_model()
    
    # 测试模型
    test_questions = [
        "如何搭建RAG中的检索器？",
        "目前中国首富是谁？",
        "北京明天天气怎么样？",
        "Python有哪些常用的深度学习库？"
    ]
    
    print("\n🔍 测试结果:")
    predictions = classifier.predict(test_questions)
    
    for q, pred in zip(test_questions, predictions):
        print(f"问题: {q}")
        print(f"预测: {'需要检索' if pred == 1 else '直接生成'}")
        print("-"*50)

if __name__ == "__main__":
    main()