import sys
from pathlib import Path
import shutil

project_root = str(Path(__file__).parent.parent.absolute())
sys.path.append(project_root)

import os
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.Classifier.classifier import TextClassifier
from utils.Classifier.data_utils import DataAugmenter
from utils.Retriever.retriever import create_rag_retriever
from dataset import questions, labels

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 只允许前端地址
        "methods": ["GET", "POST", "OPTIONS", "DELETE"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True,  # 关键！允许携带 Cookie
    }
})

# 存储对话历史的全局变量
chat_history = []

# 确保上传文件夹存在
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def init_model():
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 设置模型路径
    models_dir = project_root / "utils" / "Classifier" / "models"
    base_model_path = models_dir / "bert-base-chinese"
    trained_model_path = models_dir / "trained_model"
    
    # 确保models目录存在
    models_dir.mkdir(parents=True, exist_ok=True)

    # 检查是否已有训练好的模型
    if trained_model_path.exists():
        # 验证训练好的模型是否完整
        required_files = ['config.json', 'model.safetensors', 'vocab.txt']
        if all((trained_model_path / f).exists() for f in required_files):
            print("✅ 加载已训练好的模型")
            classifier = TextClassifier(model_path=str(trained_model_path), num_labels=2)
            if classifier.load_model():
                print("✅ 成功加载训练好的模型")
            else:
                print("❌ 训练模型加载失败，尝试重新训练...")
                return init_model()  # 递归调用重新初始化
        else:
            print("❌ 训练好的模型不完整，重新训练...")
            shutil.rmtree(trained_model_path, ignore_errors=True)
            return init_model()
    else:
        # 首次运行，加载基础模型
        print("🔄 首次运行，加载基础BERT模型并训练...")
        if not base_model_path.exists():
            print(f"❌ 基础模型不存在于 {base_model_path}")
            return None, None
            
        classifier = TextClassifier(model_path=str(base_model_path), num_labels=2)
        if not classifier.load_model():
            return None, None
        
        # 进行训练
        print("🔧 开始训练模型...")
        augmenter = DataAugmenter()
        if not classifier.train(questions, labels, batch_size=4, epochs=5, augmenter=augmenter):
            return None, None
        
        # 保存训练好的模型
        print("💾 保存训练好的模型...")
        os.makedirs(trained_model_path, exist_ok=True)
        classifier.save_model(save_path=str(trained_model_path))
        
        # 验证保存结果
        if not all((trained_model_path / f).exists() for f in ['config.json', 'model.safetensors', 'vocab.txt']):
            print("❌ 模型保存不完整，请检查磁盘空间或权限")
            return None, None
    
    # 初始化RAG检索器
    docx_file = project_root / "input.docx"
    if not docx_file.exists():
        print(f"❌ RAG文档不存在: {docx_file}")
        return None, None
        
    retrieve_answer = create_rag_retriever(str(docx_file))
    
    return classifier, retrieve_answer
    

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def handle_chat():
    if request.method == 'OPTIONS':
        # 直接返回 200，让浏览器继续发送 POST
        return jsonify({}), 200
    try:
        try:
            data = request.json
            print("解析的JSON数据:", data)
        except Exception as e:
            print("JSON解析错误:", str(e))
            return jsonify({"error": "无效的JSON格式"}), 400

        if data is None:
            # 尝试以表单形式解析（以防前端发送的是表单数据）
            form_data = request.form
            print("尝试以表单形式解析:", form_data)
            user_message = form_data.get('message', '')
            if not user_message:
                return jsonify({"error": "消息不能为空或格式错误"}), 400
        else:
            user_message = data.get('message', '')
            if not user_message:
                return jsonify({"error": "消息不能为空"}), 400
        
        ai_response = ""
        ai_response += f"您刚才说的是{user_message}\n"

        questions = [user_message]
        predictions = classifier.predict(questions)
        for q, pred in zip(questions, predictions):
                ai_response += f"预测: {'需要检索' if pred == 1 else '直接生成'}\n"
                ai_response += "-"*50

        predictions2 = retrieve_answer(user_message)
        ai_response += f"{predictions2}"
        
        # 记录对话历史
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_history.append({
            "type": "user",
            "content": user_message,
            "timestamp": timestamp
        })
        chat_history.append({
            "type": "ai",
            "content": ai_response,
            "timestamp": timestamp
        })
        
        return jsonify({
            "response": ai_response,
            "timestamp": timestamp
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def handle_upload():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400
    
    if file:
        # 保存文件
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # 记录上传历史并返回固定消息
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_history.append({
            "type": "user",
            "content": f"上传了文件：{file.filename}",
            "timestamp": timestamp
        })
        
        ai_response = f"文件「{file.filename}」已接收，这是固定的处理结果"
        chat_history.append({
            "type": "ai",
            "content": ai_response,
            "timestamp": timestamp
        })
        
        return jsonify({
            "response": ai_response,
            "filename": file.filename,
            "timestamp": timestamp
        })

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取对话历史"""
    return jsonify({
        "history": chat_history
    })

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """清空对话历史"""
    global chat_history
    chat_history = []
    return jsonify({"message": "历史记录已清空"})



if __name__ == '__main__':
    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # 初始化模型
    classifier, retrieve_answer = init_model()
    if classifier is None or retrieve_answer is None:
        print("❌ 模型初始化失败，无法启动服务")
        exit(1)

    app.run(debug=True, host='0.0.0.0', port=5000)
