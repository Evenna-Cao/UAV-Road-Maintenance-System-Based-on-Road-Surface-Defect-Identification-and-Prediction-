
import matplotlib
import matplotlib.pyplot as plt

# 全局设置字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
# from matplotlib.patches import Rectangle
# import pandas as pd
#
#
# # ================== 数据加载与处理 ==================
# def load_no_fly_zones(no_fly_file):
#     """加载禁飞区信息和区域尺寸"""
#     with open(no_fly_file, 'r') as f:
#         lines = f.readlines()
#
#     # 解析区域尺寸
#     width, height = map(float, lines[0].strip().split())
#
#     # 解析禁飞区
#     no_fly_zones = []
#     for line in lines[1:]:
#         x1, x2, y1, y2 = map(float, line.strip().split())
#         no_fly_zones.append((x1, x2, y1, y2))
#
#     return width, height, no_fly_zones
#
#
# def generate_flight_path(width, height, no_fly_zones, step=0.5):
#     """生成确定性蛇形航迹并保存"""
#     path = []
#     y = 0.0
#     direction = 1  # 1: 右向扫描, -1: 左向扫描
#
#     while y <= height:
#         # 计算当前行起点终点
#         x_start = 0.0 if direction == 1 else width
#         x_end = width if direction == 1 else 0.0
#
#         # 生成当前行采样点
#         x_values = np.linspace(x_start, x_end, int(width / step) + 1)
#         x_values = np.clip(x_values, 0.0, width)
#
#         for x in x_values:
#             # 检查禁飞区碰撞
#             collision = False
#             for (x1, x2, y1, y2) in no_fly_zones:
#                 if (x1 <= x <= x2) and (y1 <= y <= y2):
#                     collision = True
#                     break
#             if not collision:
#                 path.append((round(x, 2), round(y, 2)))  # 保留两位小数
#
#         # 垂直移动
#         y = round(y + step, 2)
#         direction *= -1
#
#     # 保存航迹
#     np.savetxt("flight_path.txt", path, fmt="%.2f", delimiter=",")
#     return np.array(path)
#
#
# # ================== 深度矩阵重建 ==================
# def reconstruct_depth_matrix(sampled_depths_file, flight_path, width, height):
#     """从航迹和深度数据重建矩阵"""
#     # 加载深度数据
#     depths = np.loadtxt(sampled_depths_file)
#
#     # 计算矩阵尺寸
#     x_coords = np.unique(flight_path[:, 0])
#     y_coords = np.unique(flight_path[:, 1])
#     cols = len(x_coords)
#     rows = len(y_coords)
#
#     # 创建空矩阵
#     depth_grid = np.full((rows, cols), np.nan)
#
#     # 建立坐标映射
#     x_mapping = {x: i for i, x in enumerate(sorted(x_coords))}
#     y_mapping = {y: i for i, y in enumerate(sorted(y_coords))}
#
#     # 填充数据
#     for (x, y), depth in zip(flight_path, depths):
#         if x in x_mapping and y in y_mapping:
#             depth_grid[y_mapping[y], x_mapping[x]] = depth
#
#     return depth_grid, x_coords, y_coords
#
#
# # ================== 区域分割处理 ==================
# def create_mask(depth_grid, no_fly_zones, x_coords, y_coords):
#     """创建有效区域掩码"""
#     mask = np.ones_like(depth_grid, dtype=bool)
#
#     # 处理禁飞区
#     for (x1, x2, y1, y2) in no_fly_zones:
#         # 转换为矩阵索引
#         col_start = np.searchsorted(x_coords, x1, side='left')
#         col_end = np.searchsorted(x_coords, x2, side='right')
#         row_start = np.searchsorted(y_coords, y1, side='left')
#         row_end = np.searchsorted(y_coords, y2, side='right')
#
#         # 应用掩码
#         mask[row_start:row_end, col_start:col_end] = False
#
#     # 处理未采样区域
#     mask[np.isnan(depth_grid)] = False
#     return mask
#
#
# def region_growing(grid, mask, distance=1.5, depth_diff=1.0):
#     """改进的区域生长算法"""
#     valid_points = np.argwhere(mask)
#     valid_depths = grid[mask]
#
#     tree = KDTree(valid_points)
#     neighbors = tree.query_ball_tree(tree, distance)
#
#     visited = np.zeros(len(valid_points), dtype=bool)
#     regions = []
#
#     for i in range(len(valid_points)):
#         if not visited[i]:
#             stack = [i]
#             visited[i] = True
#             current_region = [i]
#
#             while stack:
#                 current = stack.pop()
#                 for neighbor in neighbors[current]:
#                     if not visited[neighbor]:
#                         if abs(valid_depths[current] - valid_depths[neighbor]) <= depth_diff:
#                             visited[neighbor] = True
#                             current_region.append(neighbor)
#                             stack.append(neighbor)
#             regions.append(current_region)
#
#     return valid_points, valid_depths, regions
#
#
# # ================== 结果可视化与输出 ==================
# def visualize_results(depth_grid, region_map, stats, label_positions,
#                       x_coords, y_coords, no_fly_zones, width, height):
#     """可视化结果"""
#     plt.figure(figsize=(16, 8))
#
#     # 原始深度图
#     ax1 = plt.subplot(1, 2, 1)
#     extent = [x_coords[0], x_coords[-1], y_coords[0], y_coords[-1]]
#     im1 = ax1.imshow(depth_grid, cmap='viridis', origin='lower',
#                      extent=extent, aspect='auto')
#
#     # 区域分割图
#     ax2 = plt.subplot(1, 2, 2)
#     im2 = ax2.imshow(region_map, cmap='tab20', origin='lower',
#                      extent=extent, aspect='auto')
#
#     # 添加区域编号
#     for idx, (y, x) in enumerate(label_positions):
#         ax2.text(x_coords[x], y_coords[y], f'区域{idx + 1}',
#                  ha='center', va='center', color='white',
#                  bbox=dict(facecolor='black', alpha=0.5, boxstyle='round'))
#
#     # 添加禁飞区
#     for (x1, x2, y1, y2) in no_fly_zones:
#         for ax in [ax1, ax2]:
#             ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
#                                    facecolor='red', alpha=0.3))
#
#     # 添加颜色条
#     plt.colorbar(im1, ax=ax1, label='深度值')
#     plt.colorbar(im2, ax=ax2, label='区域编号')
#
#     ax1.set_title('原始深度分布')
#     ax2.set_title('深度区域分割')
#     plt.tight_layout()
#     plt.savefig('analysis_results.png', dpi=300)
#     plt.show()
#
#
# def save_statistics(stats, x_coords, y_coords):
#     """保存统计信息"""
#     df = pd.DataFrame(stats)
#     # 添加坐标信息
#     df['最小X'] = [x_coords[pts[:, 1].min()] for pts in df['points']]
#     df['最大X'] = [x_coords[pts[:, 1].max()] for pts in df['points']]
#     df['最小Y'] = [y_coords[pts[:, 0].min()] for pts in df['points']]
#     df['最大Y'] = [y_coords[pts[:, 0].max()] for pts in df['points']]
#     df.drop(columns=['points'], inplace=True)
#
#     df.to_excel('区域统计表.xlsx', index=False, engine='openpyxl')
#
#
# # ================== 主程序 ==================
# if __name__ == "__main__":
#     # 输入文件
#     no_fly_file = "no_fly_zones.txt"
#     sampled_depths_file = "sampled_depths.txt"
#
#     # 步骤1：生成并保存航迹
#     width, height, no_fly_zones = load_no_fly_zones(no_fly_file)
#     flight_path = generate_flight_path(width, height, no_fly_zones)
#
#     # 步骤2：重建深度矩阵
#     depth_grid, x_coords, y_coords = reconstruct_depth_matrix(
#         sampled_depths_file, flight_path, width, height)
#
#     # 步骤3：创建掩码
#     mask = create_mask(depth_grid, no_fly_zones, x_coords, y_coords)
#
#     # 步骤4：区域分割
#     valid_points, valid_depths, regions = region_growing(depth_grid, mask)
#
#     # 步骤5：生成结果数据
#     region_map = np.full_like(depth_grid, np.nan)
#     stats = []
#     label_positions = []
#
#     for region_id, region in enumerate(regions):
#         # 区域统计
#         pts = valid_points[region]
#         depths = valid_depths[region]
#         region_map[pts[:, 0], pts[:, 1]] = region_id
#
#         # 标签位置
#         tree = KDTree(pts)
#         center = np.mean(pts, axis=0)
#         _, idx = tree.query(center)
#         label_positions.append(pts[idx])
#
#         # 统计信息
#         stats.append({
#             '区域ID': region_id + 1,
#             '平均深度': np.mean(depths),
#             '深度标准差': np.std(depths),
#             '最小深度': np.min(depths),
#             '最大深度': np.max(depths),
#             '点数': len(region),
#             'points': pts  # 临时存储用于坐标转换
#         })
#
#     # 步骤6：可视化与保存
#     visualize_results(depth_grid, region_map, stats, label_positions,
#                       x_coords, y_coords, no_fly_zones, width, height)
#     save_statistics(stats, x_coords, y_coords)


import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
# from scipy import stats
# from matplotlib.patches import Rectangle
# import pandas as pd
#
#
# # ================== 数据加载与处理 ==================
# def load_no_fly_zones(no_fly_file):
#     """加载禁飞区信息和区域尺寸"""
#     with open(no_fly_file, 'r') as f:
#         lines = f.readlines()
#
#     width, height = map(float, lines[0].strip().split())
#     no_fly_zones = [tuple(map(float, line.strip().split())) for line in lines[1:]]
#
#     return width, height, no_fly_zones
#
#
# def generate_flight_path_with_checks(width, height, no_fly_zones, step=0.5):
#     """生成包含禁飞区检测点的航迹"""
#     path = []
#     check_points = []
#
#     # 生成主航迹（蛇形扫描）
#     y = 0.0
#     direction = 1
#     while y <= height:
#         x_start = 0.0 if direction == 1 else width
#         x_end = width if direction == 1 else 0.0
#         x_values = np.linspace(x_start, x_end, int(width / step) + 1)
#
#         for x in x_values:
#             x = round(x, 2)
#             y_round = round(y, 2)
#             in_no_fly = any((x1 <= x <= x2) and (y1 <= y_round <= y2)
#                             for (x1, x2, y1, y2) in no_fly_zones)
#
#             if in_no_fly:
#                 check_points.append((x, y_round))  # 记录检测点
#             else:
#                 path.append((x, y_round))
#
#         # 添加垂直方向检测点
#         for (x1, x2, y1, y2) in no_fly_zones:
#             vy = np.linspace(max(y1, 0), min(y2, height), int((y2 - y1) / step) + 1)
#             for v in vy:
#                 path.append((x1 + (x2 - x1) / 2, round(v, 2)))  # 禁飞区中心垂直线
#
#         y = round(y + step, 2)
#         direction *= -1
#
#     full_path = path + check_points
#     np.savetxt("flight_path.txt", full_path, fmt="%.2f", delimiter=",")
#     return np.array(full_path), np.array(check_points)
#
#
# # ================== 深度验证 ==================
# def validate_no_fly_depths(sampled_points, sampled_depths, no_fly_zones):
#     """验证禁飞区深度异常"""
#     # 分类检测点和普通点
#     no_fly_depths = []
#     normal_depths = []
#
#     for (x, y), depth in zip(sampled_points, sampled_depths):
#         in_no_fly = any((x1 <= x <= x2) and (y1 <= y <= y2)
#                         for (x1, x2, y1, y2) in no_fly_zones)
#         if in_no_fly:
#             no_fly_depths.append(depth)
#         else:
#             normal_depths.append(depth)
#
#     # 统计检验
#     if len(no_fly_depths) < 3 or len(normal_depths) < 3:
#         raise ValueError("采样点不足，无法进行有效验证")
#
#     t_stat, p_value = stats.ttest_ind(no_fly_depths, normal_depths)
#
#     print(f"验证结果：")
#     print(f"禁飞区平均深度：{np.mean(no_fly_depths):.2f} ± {np.std(no_fly_depths):.2f}")
#     print(f"正常区平均深度：{np.mean(normal_depths):.2f} ± {np.std(normal_depths):.2f}")
#     print(f"t检验统计量：{t_stat:.2f}, p值：{p_value:.4f}")
#
#     if p_value > 0.05 or t_stat < 2:
#         raise ValueError("禁飞区深度特征不符合预期，终止处理")
#     print("深度验证通过\n")
#
#
# # ================== 矩阵重建与处理 ==================
# def reconstruct_depth_matrix(sampled_points, sampled_depths, width, height):
#     """重建深度矩阵"""
#     x_coords = np.unique(sampled_points[:, 0])
#     y_coords = np.unique(sampled_points[:, 1])
#
#     depth_grid = np.full((len(y_coords), len(x_coords)), np.nan)
#     x_idx = {x: i for i, x in enumerate(sorted(x_coords))}
#     y_idx = {y: i for i, y in enumerate(sorted(y_coords))}
#
#     for (x, y), d in zip(sampled_points, sampled_depths):
#         depth_grid[y_idx[round(y, 2)], x_idx[round(x, 2)]] = d
#
#     return depth_grid, x_coords, y_coords
#
#
# # ================== 区域分割与可视化 ==================
# def process_and_visualize(depth_grid, x_coords, y_coords, no_fly_zones, width, height):
#     """完整处理流程"""
#     # 创建掩码
#     mask = np.ones_like(depth_grid, dtype=bool)
#     for (x1, x2, y1, y2) in no_fly_zones:
#         x_mask = (x_coords >= x1) & (x_coords <= x2)
#         y_mask = (y_coords >= y1) & (y_coords <= y2)
#         mask[np.ix_(y_mask, x_mask)] = False
#     mask[np.isnan(depth_grid)] = False
#
#     # 区域分割
#     valid_points = np.argwhere(mask)
#     valid_depths = depth_grid[mask]
#     tree = KDTree(valid_points)
#     neighbors = tree.query_ball_tree(tree, 1.5)
#
#     regions = []
#     visited = np.zeros(len(valid_points), bool)
#     for i in range(len(valid_points)):
#         if not visited[i]:
#             stack = [i]
#             current_region = []
#             while stack:
#                 idx = stack.pop()
#                 if not visited[idx]:
#                     visited[idx] = True
#                     current_region.append(idx)
#                     stack.extend(neighbors[idx])
#             regions.append(current_region)
#
#     # 生成结果
#     region_map = np.full_like(depth_grid, -1, dtype=float)
#     stats_data = []
#     label_positions = []
#
#     for rid, region in enumerate(regions):
#         pts = valid_points[region]
#         depths = valid_depths[region]
#         region_map[pts[:, 0], pts[:, 1]] = rid
#
#         # 标签定位
#         center = np.mean(pts, axis=0)
#         dists = np.linalg.norm(pts - center, axis=1)
#         label_pos = pts[np.argmin(dists)]
#         label_positions.append(label_pos)
#
#         # 统计信息
#         stats_data.append({
#             '区域ID': rid + 1,
#             '平均深度': np.mean(depths),
#             '标准差': np.std(depths),
#             '最小深度': np.min(depths),
#             '最大深度': np.max(depths),
#             '点数': len(region),
#             '中心X': x_coords[pts[:, 1].mean().astype(int)],
#             '中心Y': y_coords[pts[:, 0].mean().astype(int)]
#         })
#
#     # 可视化
#     plt.figure(figsize=(18, 8))
#
#     # 原始深度分布
#     ax1 = plt.subplot(1, 2, 1)
#     im1 = ax1.imshow(depth_grid, cmap='viridis', origin='lower',
#                      extent=[x_coords[0], x_coords[-1], y_coords[0], y_coords[-1]])
#     plt.colorbar(im1, ax=ax1, label='深度值')
#     ax1.set_title('原始深度分布')
#
#     # 区域分割结果
#     ax2 = plt.subplot(1, 2, 2)
#     im2 = ax2.imshow(region_map, cmap='tab20', origin='lower',
#                      extent=[x_coords[0], x_coords[-1], y_coords[0], y_coords[-1]])
#     for pos in label_positions:
#         ax2.text(x_coords[pos[1]], y_coords[pos[0]], f'区域{region_map[pos[0], pos[1]] + 1}',
#                  ha='center', va='center', color='white',
#                  bbox=dict(facecolor='black', alpha=0.5))
#     plt.colorbar(im2, ax=ax2, label='区域ID')
#     ax2.set_title('深度区域分割')
#
#     # 添加禁飞区
#     for (x1, x2, y1, y2) in no_fly_zones:
#         for ax in [ax1, ax2]:
#             ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
#                                    facecolor='red', alpha=0.3, edgecolor='none'))
#
#     plt.tight_layout()
#     plt.savefig('depth_analysis.png', dpi=300, bbox_inches='tight')
#
#     # 保存统计
#     pd.DataFrame(stats_data).to_excel('区域统计.xlsx', index=False, engine='openpyxl')
#
#
# # ================== 主流程 ==================
# if __name__ == "__main__":
#     # 输入文件
#     no_fly_file = "no_fly_zones.txt"
#     sampled_depths_file = "sampled_depths.txt"
#
#     try:
#         # 步骤1：生成航迹
#         width, height, no_fly_zones = load_no_fly_zones(no_fly_file)
#         flight_path, check_points = generate_flight_path_with_checks(width, height, no_fly_zones)
#
#         # 步骤2：加载采样数据
#         sampled_points = np.loadtxt("flight_path.txt", delimiter=",")
#         sampled_depths = np.loadtxt(sampled_depths_file)
#
#         # 步骤3：深度验证
#         validate_no_fly_depths(sampled_points, sampled_depths, no_fly_zones)
#
#         # 步骤4：重建矩阵
#         depth_grid, x_coords, y_coords = reconstruct_depth_matrix(sampled_points, sampled_depths, width, height)
#
#         # 步骤5：处理与可视化
#         process_and_visualize(depth_grid, x_coords, y_coords, no_fly_zones, width, height)
#         print("处理完成，结果已保存")
#
#     except Exception as e:
#         print(f"\n错误终止：{str(e)}")
#         exit(1)

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.patches import Rectangle
import pandas as pd
import random


# ================== 数据加载与处理 ==================


# ================== 结果输出与可视化 ==================
# def save_full_depth_excel(depth_grid, width, height, x_step, y_step):
#     """生成完整深度分布表"""
#     rows, cols = depth_grid.shape
#     df = pd.DataFrame(
#         index=np.round(np.arange(0, height + y_step, y_step), 2),
#         columns=np.round(np.arange(0, width + x_step, x_step), 2)
#     )
#
#     for row in range(rows):
#         for col in range(cols):
#             df.iloc[row, col] = depth_grid[row, col]
#
#     df.to_excel("完整深度分布.xlsx", na_rep='N/A')
#
#
# def visualize_results(depth_grid, region_map, no_fly_zones, width, height):
#     """生成并保存可视化结果"""
#     plt.figure(figsize=(18, 9))
#
#     # 原始深度分布图
#     ax1 = plt.subplot(1, 2, 1)
#     im1 = ax1.imshow(depth_grid, cmap='viridis', origin='lower',
#                      extent=[0, width, 0, height], aspect='auto')
#     plt.colorbar(im1, ax=ax1, label='深度值')
#     ax1.set_title("完整深度分布")
#
#     # 区域分割结果图
#     ax2 = plt.subplot(1, 2, 2)
#     im2 = ax2.imshow(region_map, cmap='tab20', origin='lower',
#                      extent=[0, width, 0, height], aspect='auto')
#     plt.colorbar(im2, ax=ax2, label='区域编号')
#     ax2.set_title("深度区域分割")
#
#     # 绘制禁飞区
#     for (x1, x2, y1, y2) in no_fly_zones:
#         for ax in [ax1, ax2]:
#             ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
#                                    facecolor='red', alpha=0.3, edgecolor='none'))
#
#     plt.tight_layout()
#     plt.savefig('深度分析结果.png', dpi=300, bbox_inches='tight')
#     # 保存统计信息到Excel（添加引擎参数）


# # ================== 主流程 ==================
# if __name__ == "__main__":
#     # 输入文件
#     no_fly_file = "no_fly_zones.txt"
#     sampled_depths_file = "sampled_depths.txt"
#
#     try:
#         # 步骤1：生成航迹
#         width, height, no_fly_zones = load_no_fly_zones(no_fly_file)
#         flight_path = generate_flight_path(width, height, no_fly_zones)
#
#         # 步骤2：加载数据
#         sampled_points = np.loadtxt("flight_path.txt", delimiter=",")
#         sampled_depths = np.loadtxt(sampled_depths_file)
#
#         # 步骤3：验证检测点
#         validate_check_points(sampled_points, sampled_depths, no_fly_zones)
#         print("深度验证通过")
#
#         # 步骤4：重建完整矩阵
#         depth_grid, x_step, y_step = reconstruct_full_matrix(
#             sampled_points, sampled_depths, width, height)
#
#         # 步骤5：生成区域分割
#         valid_points = np.argwhere(~np.isnan(depth_grid))
#         tree = KDTree(valid_points)
#         regions = tree.query_ball_tree(tree, 1.5)
#
#         # 区域标记
#         region_map = np.full_like(depth_grid, -1, dtype=float)
#         region_id = 0
#         visited = np.zeros(len(valid_points), dtype=bool)
#         save_full_depth_excel(depth_grid, width, height, x_step, y_step)
#
#         for i in range(len(valid_points)):
#             if not visited[i]:
#                 stack = [i]
#                 while stack:
#                     idx = stack.pop()
#                     if not visited[idx]:
#                         visited[idx] = True
#                         region_map[valid_points[idx][0], valid_points[idx][1]] = region_id
#                         stack.extend(regions[idx])
#                 region_id += 1
#
#         # 步骤6：保存结果
#
#         visualize_results(depth_grid, region_map, no_fly_zones, width, height)
#         print("处理完成，结果已保存")
#
#     except Exception as e:
#         print(f"\n处理终止：{str(e)}")
#         exit(1)

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.patches import Rectangle
import pandas as pd
import random


# ================== 核心功能模块 ==================
def create_region_map(valid_points, valid_depths, regions, grid_shape):
    """创建区域填色矩阵并计算统计信息
    参数：
        valid_points - 有效点坐标矩阵
        valid_depths - 对应深度值
        regions - 区域划分结果
        grid_shape - 原始网格尺寸

    返回：
        region_map - 区域编号矩阵
        region_depth_map - 区域平均深度矩阵
        stats - 区域统计信息列表
    """
    region_map = np.full(grid_shape, -1, dtype=int)
    region_depth_map = np.full(grid_shape, np.nan)
    stats = []
    label_positions = []

    for region_id, region in enumerate(regions):
        region_depths = valid_depths[region]
        region_coords = valid_points[region]

        # 计算统计指标
        mean_depth = np.mean(region_depths)
        std_depth = np.std(region_depths)
        min_depth = np.min(region_depths)
        max_depth = np.max(region_depths)
        area_size = len(region)

        # 记录标签位置（区域中心）
        center = np.mean(region_coords, axis=0)
        label_positions.append(center)

        # 存储统计信息
        stats.append({
            '区域ID': region_id + 1,
            '平均深度': mean_depth,
            '深度标准差': std_depth,
            '最小深度': min_depth,
            '最大深度': max_depth,
            '区域面积': area_size
        })

        # 填充区域矩阵
        for pt_idx in region:
            y, x = valid_points[pt_idx]
            region_map[int(y), int(x)] = region_id
            region_depth_map[int(y), int(x)] = mean_depth

    return region_map, region_depth_map, stats, label_positions


# ================== 主处理流程 ==================
def main_processing_flow():
    try:
        # 加载禁飞区数据
        width, height, no_fly_zones = load_no_fly_zones("no_fly_zones.txt")

        # 生成航迹并采样
        flight_path = generate_flight_path(width, height, no_fly_zones)
        sampled_points = np.loadtxt("flight_path.txt", delimiter=",")
        sampled_depths = np.loadtxt("sampled_depths.txt")

        # 验证数据
        validate_check_points(sampled_points, sampled_depths, no_fly_zones)

        # 重建深度矩阵
        depth_grid, x_step, y_step = reconstruct_full_matrix(
            sampled_points, sampled_depths, width, height)

        # 创建有效区域掩码
        mask = create_mask(depth_grid, no_fly_zones, width, height)

        # 区域分割
        valid_points = np.argwhere(~np.isnan(depth_grid) & mask)
        valid_depths = depth_grid[~np.isnan(depth_grid) & mask]
        tree = KDTree(valid_points)
        neighbors = tree.query_ball_tree(tree, 1.5)

        # 执行区域生长
        regions = []
        visited = np.zeros(len(valid_points), dtype=bool)
        for i in range(len(valid_points)):
            if not visited[i]:
                stack = [i]
                current_region = []
                while stack:
                    idx = stack.pop()
                    if not visited[idx]:
                        visited[idx] = True
                        current_region.append(idx)
                        stack.extend(neighbors[idx])
                regions.append(current_region)

        # 生成区域映射和统计信息
        region_map, _, stats, labels = create_region_map(
            valid_points, valid_depths, regions, depth_grid.shape)

        # 保存统计结果
        pd.DataFrame(stats).to_excel("区域统计表.xlsx", index=False, engine='openpyxl')

        # 可视化输出
        visualize_results(depth_grid, region_map, no_fly_zones, width, height)
        print("处理成功完成")

    except Exception as e:
        print(f"处理失败：{str(e)}")
        exit(1)


# ================== 辅助函数 ==================
def visualize_results(depth_grid, region_map, no_fly_zones, width, height):
    """可视化结果并保存图片"""
    plt.figure(figsize=(18, 9))

    # 原始深度分布
    plt.subplot(1, 2, 1)
    plt.imshow(depth_grid, cmap='viridis', origin='lower',
               extent=[0, width, 0, height], aspect='auto')
    plt.colorbar(label='深度值')
    plt.title("原始深度分布")

    # 区域分割结果
    plt.subplot(1, 2, 2)
    plt.imshow(region_map, cmap='tab20', origin='lower',
               extent=[0, width, 0, height], aspect='auto')
    plt.colorbar(label='区域编号')
    plt.title("深度区域分割")

    # 添加禁飞区
    for (x1, x2, y1, y2) in no_fly_zones:
        for ax in plt.gcf().axes:
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
                                   facecolor='red', alpha=0.3, edgecolor='none'))

    plt.tight_layout()
    plt.savefig('分析结果.png', dpi=300, bbox_inches='tight')
    plt.close()


# ================== 其他配套函数 ==================
# 此处需要保留之前定义的以下函数：
def load_no_fly_zones(no_fly_file):
    """加载禁飞区信息和区域尺寸"""
    with open(no_fly_file, 'r') as f:
        lines = f.readlines()

    width, height = map(float, lines[0].strip().split())
    no_fly_zones = [tuple(map(float, line.strip().split())) for line in lines[1:]]

    return width, height, no_fly_zones


def generate_flight_path(width, height, no_fly_zones, step=0.5, check_ratio=0.05):
    """生成带有限检测点的航迹"""
    path = []
    check_points = []

    # 生成主航迹（蛇形扫描）
    y = 0.0
    direction = 1
    while y <= height:
        x_start = 0.0 if direction == 1 else width
        x_end = width if direction == 1 else 0.0
        x_values = np.linspace(x_start, x_end, int(width / step) + 1)

        for x in x_values:
            x = round(x, 2)
            y_round = round(y, 2)
            in_no_fly = any((x1 <= x <= x2) and (y1 <= y_round <= y2)
                            for (x1, x2, y1, y2) in no_fly_zones)

            if not in_no_fly:
                path.append((x, y_round))

        # 在每个禁飞区随机采样检测点
        for zone in no_fly_zones:
            x1, x2, y1, y2 = zone
            for _ in range(int((x2 - x1) * (y2 - y1) * check_ratio)):
                x = round(random.uniform(x1, x2), 2)
                y = round(random.uniform(y1, y2), 2)
                check_points.append((x, y))

        y = round(y + step, 2)
        direction *= -1

    full_path = path + check_points
    np.savetxt("flight_path.txt", full_path, fmt="%.2f", delimiter=",")
    return np.array(full_path)


# ================== 深度验证 ==================
def validate_check_points(sampled_points, sampled_depths, no_fly_zones, threshold=2.0):
    """验证检测点深度异常"""
    check_depths = []
    normal_depths = []

    for (x, y), depth in zip(sampled_points, sampled_depths):
        if any((x1 <= x <= x2) and (y1 <= y <= y2) for (x1, x2, y1, y2) in no_fly_zones):
            check_depths.append(depth)
        else:
            normal_depths.append(depth)

    if not check_depths:
        raise ValueError("未检测到禁飞区采样点")

    # 简单阈值验证
    avg_check = np.mean(check_depths)
    avg_normal = np.mean(normal_depths)

    print(f"验证结果：")
    print(f"禁飞区检测点平均深度：{avg_check:.2f}（共{len(check_depths)}个点）")
    print(f"正常区域平均深度：{avg_normal:.2f}")
    print(f"深度差异倍数：{avg_check / avg_normal:.1f}x")

    if avg_check / avg_normal < threshold:
        raise ValueError(f"禁飞区深度不足正常区域的{threshold}倍，数据可能异常")


# ================== 矩阵重建与处理 ==================
def reconstruct_full_matrix(sampled_points, sampled_depths, width, height):
    """重建完整深度矩阵"""
    # 生成坐标网格
    x_res = int(width / (sampled_points[1, 0] - sampled_points[0, 0])) + 1
    y_res = int(height / (sampled_points[x_res, 1] - sampled_points[0, 1])) + 1

    depth_grid = np.full((y_res, x_res), np.nan)
    x_step = width / (x_res - 1)
    y_step = height / (y_res - 1)

    for (x, y), d in zip(sampled_points, sampled_depths):
        col = int(round(x / x_step))
        row = int(round(y / y_step))
        if 0 <= row < y_res and 0 <= col < x_res:
            depth_grid[row, col] = d

    return depth_grid, x_step, y_step

# - load_no_fly_zones()
# - generate_flight_path()
# - validate_check_points()
# - reconstruct_full_matrix()
# - create_mask()

if __name__ == "__main__":
    main_processing_flow()