import matplotlib
import matplotlib.pyplot as plt

# 全局设置字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

# import os
# import torch
# import torchvision.transforms as transforms
# from PIL import Image
# from torch.autograd import Variable
#
# # ================== 配置参数 ==================
# DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# MODEL_PATH = "E:\\Desktop\\深度学习+\\图像识别model\\model_混凝土表面裂纹大数据5.pth"
# TEST_DIR = "E:\\Desktop\\深度学习+\\picture—test"
#
# # ================== 数据预处理 ==================
# # 与验证集保持一致
# transform_test = transforms.Compose([
#     transforms.Resize((224, 224)),  # 保持与验证集相同的resize
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.5, 0.5, 0.5],  # 与训练时相同的归一化参数
#                          std=[0.5, 0.5, 0.5])
# ])
#
# # ================== 类别标签加载 ==================
# # 需要与训练时的类别顺序严格一致！
# # 这里假设训练时的类别为：['正常', '裂缝'] 或其他实际类别
# # 请根据实际训练数据修改
# class_names = ['正常路面', '裂缝路面']  # 示例类别，需替换为实际类别
#
#
# # ================== 模型加载 ==================
# def load_model(model_path):
#     """安全加载模型"""
#     model = torch.load(model_path, map_location=DEVICE)
#     model.eval()
#     return model.to(DEVICE)
#
#
# # ================== 预测函数 ==================
# def predict_image(image_path, model):
#     """单张图像预测"""
#     try:
#         # 加载并预处理图像
#         img = Image.open(image_path).convert('RGB')  # 确保转为RGB
#         img_tensor = transform_test(img).unsqueeze(0)  # 添加batch维度
#         img_var = Variable(img_tensor).to(DEVICE)
#
#         # 执行预测
#         with torch.no_grad():
#             output = model(img_var)
#             _, pred = torch.max(output.data, 1)
#
#         return class_names[pred.item()]
#
#     except Exception as e:
#         print(f"处理图像 {image_path} 时发生错误: {str(e)}")
#         return None
#
#
# # ================== 主流程 ==================
# if __name__ == "__main__":
#     # 加载模型
#     model = load_model(MODEL_PATH)
#     print("模型加载成功，开始检测...")
#
#     # 遍历测试目录
#     for filename in os.listdir(TEST_DIR):
#         if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#             image_path = os.path.join(TEST_DIR, filename)
#
#             # 执行预测
#             prediction = predict_image(image_path, model)
#
#             if prediction is not None:
#                 print(f"图像: {filename} \t 检测结果: {prediction}")


import os
import re
import torch
import pandas as pd
from PIL import Image
from torchvision import transforms


# ================== 系统配置 ==================
class Config:
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    GRID_SIZE = 1.0  # 单位：米，每个图像覆盖区域
    MODEL_CONFIG = {
        "marble": {
            "model_path": "models/marble.pth",
            "transform": transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ]),
            "defect_classes": ['crack', 'dot', 'joint']
        },
        "road": {
            "model_path": "models/road.pth",
            "transform": transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            ]),
            "defect_classes": ['Cracks', 'Patch', 'Potholes', 'Surface Defects']
        },
        "concrete": {
            "model_path": "models/concrete.pth",
            "transform": transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.Grayscale(num_output_channels=3),
                transforms.ToTensor(),
                transforms.Normalize([0.5] * 3, [0.5] * 3)
            ]),
            "defect_classes": ['positive']
        }
    }


# ================== 核心检测模块 ==================
class DefectDetector:
    def __init__(self):
        self.models = self._load_models()

    def _load_models(self):
        """预加载所有检测模型"""
        models = {}
        for scene, cfg in Config.MODEL_CONFIG.items():
            model = torch.load(cfg["model_path"], map_location=Config.DEVICE)
            model.eval()
            models[scene] = {
                "model": model.to(Config.DEVICE),
                "transform": cfg["transform"],
                "defect_classes": cfg["defect_classes"]
            }
        return models

    def parse_coordinates(self, filename):
        """解析图像坐标"""
        match = re.search(r"\(([\d.]+),([\d.]+)\)", filename)
        return float(match.group(1)), float(match.group(2)) if match else (None, None)

    def detect(self, image_path):
        """执行缺陷检测"""
        scene = os.path.basename(os.path.dirname(image_path))
        if scene not in self.models:
            return None

        try:
            # 加载图像
            img = Image.open(image_path).convert('RGB')

            # 执行转换
            transform = self.models[scene]["transform"]
            tensor = transform(img).unsqueeze(0).to(Config.DEVICE)

            # 模型预测
            with torch.no_grad():
                outputs = self.models[scene]["model"](tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                conf, pred = torch.max(probs, 1)

            # 获取分类结果
            class_name = self.models[scene]["defect_classes"][pred.item()]
            return {
                "scene": scene,
                "class": class_name,
                "confidence": conf.item(),
                "is_defect": class_name != "good"
            }
        except Exception as e:
            print(f"检测失败: {str(e)}")
            return None


# ================== 空间映射模块 ==================
class SpatialMapper:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.defect_zones = []

    def add_defect(self, x, y, defect_class):
        """添加缺陷区域"""
        x_min = x - self.grid_size / 2
        x_max = x + self.grid_size / 2
        y_min = y - self.grid_size / 2
        y_max = y + self.grid_size / 2
        self.defect_zones.append({
            "x_range": (x_min, x_max),
            "y_range": (y_min, y_max),
            "type": defect_class
        })

    def merge_zones(self, threshold=0.5):
        """合并相邻缺陷区域"""
        merged = []
        for zone in sorted(self.defect_zones, key=lambda z: z["x_range"][0]):
            if not merged:
                merged.append(zone)
                continue

            last = merged[-1]
            # X轴重叠检测
            x_overlap = (zone["x_range"][0] <= last["x_range"][1] + threshold)
            y_overlap = (zone["y_range"][0] <= last["y_range"][1] + threshold)

            if x_overlap and y_overlap:
                # 合并区域
                new_x = (min(last["x_range"][0], zone["x_range"][0]),
                         max(last["x_range"][1], zone["x_range"][1]))
                new_y = (min(last["y_range"][0], zone["y_range"][0]),
                         max(last["y_range"][1], zone["y_range"][1]))
                merged[-1] = {
                    "x_range": new_x,
                    "y_range": new_y,
                    "type": f"Merged_{last['type']}"
                }
            else:
                merged.append(zone)

        self.defect_zones = merged

    def export_zones(self, output_excel, output_txt):
        """导出禁飞区文件"""
        # 生成Excel文件
        df = pd.DataFrame([{
            "x_min": zone["x_range"][0],
            "x_max": zone["x_range"][1],
            "y_min": zone["y_range"][0],
            "y_max": zone["y_range"][1],
            "defect_type": zone["type"]
        } for zone in self.defect_zones])
        df.to_excel(output_excel, index=False)

        # 生成txt文件供路径规划使用
        x_max = max(zone["x_range"][1] for zone in self.defect_zones)
        y_max = max(zone["y_range"][1] for zone in self.defect_zones)
        with open(output_txt, 'w') as f:
            f.write(f"{x_max} {y_max}\n")
            for zone in self.defect_zones:
                line = f"{zone['x_range'][0]} {zone['x_range'][1]} {zone['y_range'][0]} {zone['y_range'][1]}\n"
                f.write(line)


# ================== 主处理流程 ==================
def process_dataset(input_dir, output_excel="defects.xlsx", output_txt="no_fly_zones.txt"):
    detector = DefectDetector()
    mapper = SpatialMapper(Config.GRID_SIZE)

    # 遍历图像文件
    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            # 解析坐标
            x, y = detector.parse_coordinates(file)
            if x is None or y is None:
                continue

            # 执行检测
            result = detector.detect(os.path.join(root, file))
            if result and result["is_defect"]:
                mapper.add_defect(x, y, result["class"])

    # 后处理
    mapper.merge_zones()
    mapper.export_zones(output_excel, output_txt)
    print(f"检测完成！生成文件：{output_excel} 和 {output_txt}")


# ================== 执行入口 ==================
if __name__ == "__main__":
    process_dataset(
        input_dir="D:/RoadInspectionData",
        output_excel="defect_areas.xlsx",
        output_txt="no_fly_zones.txt"
    )
