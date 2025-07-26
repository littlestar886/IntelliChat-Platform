import os
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification
import random

class TextClassifier:
    """基于BERT的文本分类器"""
    
    def __init__(self, model_path, num_labels=2, device=None):
        """初始化分类器"""
        self.model_path = model_path
        self.num_labels = num_labels
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        
    def load_model(self):
        """加载预训练模型和分词器"""
        try:
            # 检查模型文件是否存在
            required_files = ['config.json', 'model.safetensors', 'vocab.txt']
            missing_files = [f for f in required_files if not os.path.exists(os.path.join(self.model_path, f))]
            
            if missing_files:
                print(f"模型文件缺失：{missing_files}，开始下载bert-base-chinese...")
                os.makedirs(self.model_path, exist_ok=True)
                
                # 下载并保存预训练模型
                self.tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
                self.model = BertForSequenceClassification.from_pretrained(
                    "bert-base-chinese", 
                    num_labels=self.num_labels
                )
                
                self.tokenizer.save_pretrained(self.model_path)
                self.model.save_pretrained(self.model_path, safe_serialization=True)
                print(f"模型已保存至：{self.model_path}")
            else:
                # 加载已存在的模型
                self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
                self.model = BertForSequenceClassification.from_pretrained(
                    self.model_path,
                    num_labels=self.num_labels,
                    use_safetensors=True
                )
            
            self.model.to(self.device)
            print(f"✅ 模型加载成功 from {self.model_path}")
            return True
            
        except Exception as e:
            print(f"❌ 模型加载失败: {str(e)}")
            return False
    
    def train(self, questions, labels, batch_size=4, learning_rate=2e-5, epochs=5, val_size=0.2, augmenter=None, augment_times=3):
        """训练模型"""
        if self.model is None or self.tokenizer is None:
            print("❌ 请先加载模型")
            return False
        
        # 划分训练集和验证集
        train_q, val_q, train_lbl, val_lbl = train_test_split(
            questions, labels, test_size=val_size, random_state=42)
        
        # 准备训练数据（支持数据增强）
        from .data_utils import prepare_data  # 从外部文件导入数据处理函数
        
        train_inputs, train_labels = prepare_data(
            self.tokenizer, train_q, train_lbl, augmenter, augment_times)
        val_inputs, val_labels = prepare_data(
            self.tokenizer, val_q, val_lbl, None, 0)  # 验证集不增强
        
        # 创建数据加载器
        train_loader = DataLoader(
            TensorDataset(train_inputs['input_ids'], train_inputs['attention_mask'], train_labels),
            batch_size=batch_size, shuffle=True)
        
        val_loader = DataLoader(
            TensorDataset(val_inputs['input_ids'], val_inputs['attention_mask'], val_labels),
            batch_size=batch_size)
        
        # 设置优化器
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # 训练模型
        print("\n🚀 开始训练...")
        self._train_model(self.model, train_loader, optimizer, epochs)
        
        # 评估模型
        accuracy = self._evaluate(self.model, val_loader)
        print(f"\n🎯 验证集准确率: {accuracy*100:.2f}%")
        
        return True
    
    def predict(self, texts, apply_post_processing=True):
        """对文本进行分类预测"""
        if self.model is None or self.tokenizer is None:
            print("❌ 请先加载模型")
            return []
        
        self.model.eval()
        predictions = []
        
        for text in texts:
            # 预处理文本
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(self.device)
            
            # 模型预测
            with torch.no_grad():
                outputs = self.model(**inputs)
                pred = torch.argmax(outputs.logits, dim=1).item()
            
            # 后处理规则
            if apply_post_processing:
                pred = self._apply_post_processing(text, pred)
            
            predictions.append(pred)
        
        return predictions
    
    def save_model(self, save_path=None):
        """保存模型"""
        if self.model is None or self.tokenizer is None:
            print("❌ 没有可保存的模型")
            return False
        
        save_path = save_path or self.model_path
        os.makedirs(save_path, exist_ok=True)
        
        try:
            self.tokenizer.save_pretrained(save_path)
            self.model.save_pretrained(save_path, safe_serialization=True)
            print(f"✅ 模型已保存至: {save_path}")
            return True
        except Exception as e:
            print(f"❌ 模型保存失败: {str(e)}")
            return False
    
    def _train_model(self, model, dataloader, optimizer, epochs=5):
        """模型训练内部函数"""
        model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                batch = [item.to(self.device) for item in batch]
                optimizer.zero_grad()
                input_ids, attention_mask, labels = batch
                outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(dataloader):.4f}")
    
    def _evaluate(self, model, dataloader):
        """模型评估内部函数"""
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for batch in dataloader:
                batch = [item.to(self.device) for item in batch]
                input_ids, attention_mask, labels = batch
                outputs = model(input_ids, attention_mask=attention_mask)
                _, preds = torch.max(outputs.logits, 1)
                total += labels.size(0)
                correct += (preds == labels).sum().item()
        return correct / total
    
    def _apply_post_processing(self, text, pred):
        """应用后处理规则调整预测结果"""
        # 示例规则：包含特定关键词的问题强制分类为1
        if any(kw in text for kw in ["天气", "温度", "下雨", "气温", "最新情况", "最近", "目前"]):
            return 1
        return pred