import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

# 区域参数设置
x_min, x_max = 0, 10
y_min, y_max = 0, 10
dx, dy = 0.5, 0.5  # 采样间隔

# 禁飞区定义（矩形区域列表）
no_fly_zones = [
    {'x1': 2, 'x2': 4, 'y1': 3, 'y2': 5},
    {'x1': 6, 'x2': 8, 'y1': 2, 'y2': 7}
]

# 生成采样路径（避开禁飞区）
sampling_points = []
y_values = np.arange(y_min, y_max + dy / 2, dy)  # 避免浮点误差
x_values = np.arange(x_min, x_max + dx / 2, dx)

for y in y_values:
    for x in x_values:
        in_no_fly = False
        for zone in no_fly_zones:
            if (zone['x1'] <= x <= zone['x2']) and (zone['y1'] <= y <= zone['y2']):
                in_no_fly = True
                break
        if not in_no_fly:
            sampling_points.append([x, y])

sampling_points = np.array(sampling_points)

# 生成模拟深度数据（带噪声的圆形区域）
depth_regions = [
    {'center': [3, 4], 'radius': 2, 'depth': 5},
    {'center': [7, 5], 'radius': 3, 'depth': 8},
    {'center': [1, 8], 'radius': 1.5, 'depth': 3}
]

depths = np.zeros(len(sampling_points))
for i, (x, y) in enumerate(sampling_points):
    depth = 1  # 默认深度
    for region in depth_regions:
        cx, cy = region['center']
        if (x - cx) ** 2 + (y - cy) ** 2 <= region['radius'] ** 2:
            depth = region['depth']
    depths[i] = depth + np.random.normal(0, 0.2)  # 添加噪声

# 区域分割处理（基于空间邻近和深度相似性）
tree = KDTree(sampling_points)
distance_threshold = np.hypot(dx, dy) * 1.1  # 邻域距离阈值
depth_diff_threshold = 1.0  # 深度差异阈值

# 查询所有邻近点
neighbors = tree.query_ball_tree(tree, distance_threshold)

# 区域生长算法
visited = np.zeros(len(sampling_points), dtype=bool)
regions = []

for i in range(len(sampling_points)):
    if not visited[i]:
        stack = [i]
        visited[i] = True
        current_region = [i]

        while stack:
            current = stack.pop()
            for neighbor in neighbors[current]:
                if not visited[neighbor]:
                    if abs(depths[current] - depths[neighbor]) <= depth_diff_threshold:
                        visited[neighbor] = True
                        current_region.append(neighbor)
                        stack.append(neighbor)

        regions.append(current_region)

# 可视化结果
plt.figure(figsize=(14, 6))

# 原始采样点及深度分布
plt.subplot(1, 2, 1)
sc = plt.scatter(sampling_points[:, 0], sampling_points[:, 1], c=depths,
                 cmap='viridis', s=30, edgecolors='k', linewidths=0.5)
for zone in no_fly_zones:
    plt.fill_between([zone['x1'], zone['x2']], zone['y1'], zone['y2'],
                     color='red', alpha=0.3)
plt.title('Sampling Points and Depth Distribution')
plt.colorbar(sc, label='Depth Value')

# 区域分割结果
plt.subplot(1, 2, 2)
colors = plt.cm.tab20.colors
for i, region in enumerate(regions):
    points = sampling_points[region]
    plt.scatter(points[:, 0], points[:, 1], color=colors[i % len(colors)],
                s=30, edgecolors='k', linewidths=0.5, label=f'Area {i + 1}')

for zone in no_fly_zones:
    plt.fill_between([zone['x1'], zone['x2']], zone['y1'], zone['y2'],
                     color='red', alpha=0.3)
plt.title('Depth Region Segmentation Results')
plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1))

plt.tight_layout()
plt.show()