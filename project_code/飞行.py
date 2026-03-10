# -*- coding: utf-8 -*-
import time
import logging
import numpy as np
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils.multiranger import Multiranger
from cflib.crazyflie.log import LogConfig
import pandas as pd
from PIL import Image
import torch
from pathlib import Path

# ================== 系统配置 ==================
uri = 'radio://0/80/2M/E7E7E7E7E7'
FLIGHT_HEIGHT = 0.6  # 飞行高度（米）
SAMPLE_INTERVAL = 0.5  # 采样间隔（秒）
MODEL_PATH = "path/to/defect_model.pth"


# ================== 深度学习模型加载 ==================
class DefectDetector:
    def __init__(self):
        self.model = torch.load(MODEL_PATH).eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.5] * 3, [0.5] * 3)
        ])

    def detect(self, image):
        tensor = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            output = self.model(tensor)
        return output.argmax().item()


detector = DefectDetector()


# ================== 无人机控制类 ==================
class InspectionDrone:
    def __init__(self, scf):
        self.scf = scf
        self.pc = PositionHlCommander(
            scf,
            default_height=FLIGHT_HEIGHT,
            controller=PositionHlCommander.CONTROLLER_PID
        )
        self.multiranger = Multiranger(scf)
        self.data_buffer = []
        self.defect_zones = []

        # 配置AI Deck图像传输
        self._init_image_transfer()

    def _init_image_transfer(self):
        self.scf.cf.param.set_value('camera.stream', '1')
        self.scf.cf.loc.receivedPacket.add_callback(self._image_callback)

    def _image_callback(self, data):
        """AI Deck图像接收回调"""
        img = Image.frombytes('RGB', (320, 240), data)
        defect_type = detector.detect(img)
        if defect_type != 0:  # 0表示正常
            pos = self.pc.get_position()
            self.defect_zones.append({
                'x': pos.x, 'y': pos.y,
                'type': defect_type
            })
            print(f"检测到缺陷@{pos.x:.2f},{pos.y:.2f} 类型:{defect_type}")

    def _depth_sampling(self):
        """多传感器深度采样"""
        if self.multiranger.down < FLIGHT_HEIGHT * 0.8:
            pos = self.pc.get_position()
            self.data_buffer.append({
                'x': pos.x,
                'y': pos.y,
                'depth': self.multiranger.down,
                'timestamp': time.time()
            })

    def execute_path(self, path_file):
        """执行预规划路径"""
        path = np.loadtxt(path_file)
        for x, y in path:
            self.pc.go_to(x, y)

            # 持续采样直到到达下一点
            start_time = time.time()
            while time.time() - start_time < SAMPLE_INTERVAL:
                self._depth_sampling()
                time.sleep(0.1)

        self._save_data()

    def _save_data(self):
        """保存采样数据"""
        df = pd.DataFrame(self.data_buffer)
        df.to_csv('depth_samples.csv', index=False)
        print(f"保存{len(df)}个深度采样点")

        defect_df = pd.DataFrame(self.defect_zones)
        defect_df.to_csv('defect_zones.csv', index=False)
        print(f"记录{len(defect_df)}个缺陷区域")


# ================== 主流程 ==================
def main():
    # 初始化通信
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # 启动无人机
        scf.cf.platform.send_arming_request(True)
        time.sleep(1)

        # 初始化检测系统
        drone = InspectionDrone(scf)

        try:
            # 执行预规划路径
            drone.execute_path('flight_path.txt')

            # 返回起飞点
            drone.pc.go_to(0, 0)

        finally:
            # 降落并关闭
            drone.pc.land()
            scf.cf.platform.send_arming_request(False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()