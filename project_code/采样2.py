import matplotlib
import matplotlib.pyplot as plt

# 全局设置字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
#
#
# def load_data(depth_file, no_fly_file):
#     """加载深度数据和禁飞区定义"""
#     depth_grid = np.loadtxt(depth_file)
#     rows, cols = depth_grid.shape
#
#     # 生成坐标网格（假设为等间距网格，坐标从0开始）
#     x_coords = np.arange(cols)
#     y_coords = np.arange(rows)
#
#     # 读取禁飞区
#     no_fly_zones = []
#     with open(no_fly_file, 'r') as f:
#         for line in f:
#             parts = list(map(float, line.strip().split()))
#             if len(parts) == 4:
#                 no_fly_zones.append(parts)
#
#     # 生成有效采样点
#     sampling_points = []
#     depths = []
#     for y in y_coords:
#         for x in x_coords:
#             if not any(z[0] <= x <= z[1] and z[2] <= y <= z[3] for z in no_fly_zones):
#                 sampling_points.append([x, y])
#                 depths.append(depth_grid[int(y), int(x)])
#
#     return np.array(sampling_points), np.array(depths), no_fly_zones
#
#
# def region_growing(points, depths, distance_thresh=1.1, depth_thresh=1.0):
#     """区域生长算法进行深度区域分割"""
#     tree = KDTree(points)
#     neighbors = tree.query_ball_tree(tree, distance_thresh)
#
#     visited = np.zeros(len(points), dtype=bool)
#     regions = []
#
#     for i in range(len(points)):
#         if not visited[i]:
#             stack = [i]
#             visited[i] = True
#             current_region = [i]
#
#             while stack:
#                 current = stack.pop()
#                 for neighbor in neighbors[current]:
#                     if not visited[neighbor]:
#                         if abs(depths[current] - depths[neighbor]) <= depth_thresh:
#                             visited[neighbor] = True
#                             current_region.append(neighbor)
#                             stack.append(neighbor)
#
#             regions.append(current_region)
#     return regions
#
#
# def visualize_results(points, depths, regions, no_fly_zones):
#     """可视化结果"""
#     # 计算区域统计信息
#     region_stats = []
#     for region in regions:
#         region_depths = depths[region]
#         region_stats.append({
#             'mean': np.mean(region_depths),
#             'std': np.std(region_depths),
#             'min': np.min(region_depths),
#             'max': np.max(region_depths)
#         })
#
#     plt.figure(figsize=(16, 7))
#
#     # 原始深度分布
#     plt.subplot(1, 2, 1)
#     sc = plt.scatter(points[:, 0], points[:, 1], c=depths, cmap='viridis',
#                      s=40, edgecolor='k', linewidth=0.5)
#     for zone in no_fly_zones:
#         plt.fill_between([zone[0], zone[1]], zone[2], zone[3],
#                          color='red', alpha=0.3)
#     plt.colorbar(sc, label='Depth Value')
#     plt.title('Original Depth Distribution')
#
#     # 区域分割结果
#     plt.subplot(1, 2, 2)
#     colors = plt.cm.tab20.colors
#     legend_handles = []
#
#     for i, region in enumerate(regions):
#         color = colors[i % len(colors)]
#         pts = points[region]
#         plt.scatter(pts[:, 0], pts[:, 1], color=color,
#                     s=40, edgecolor='k', linewidth=0.5)
#
#         # 创建图例项
#         stats = region_stats[i]
#         label = (f"Region {i + 1}\n"
#                  f"Mean: {stats['mean']:.2f}\n"
#                  f"Std: {stats['std']:.2f}\n"
#                  f"Range: {stats['min']:.2f}-{stats['max']:.2f}")
#         legend_handles.append(
#             plt.Line2D([0], [0], marker='o', color='w',
#                        markerfacecolor=color, markersize=10, label=label))
#
#     for zone in no_fly_zones:
#         plt.fill_between([zone[0], zone[1]], zone[2], zone[3],
#                          color='red', alpha=0.3)
#
#     plt.title('Depth Region Segmentation')
#     plt.legend(handles=legend_handles, loc='upper left',
#                bbox_to_anchor=(1.05, 1), fontsize=8)
#
#     plt.tight_layout()
#     plt.show()
#
#
# if __name__ == "__main__":
#     # 输入文件路径
#     depth_file = "depth.txt"
#     no_fly_file = "no_fly_zones.txt"
#
#     # 处理数据
#     sampling_points, depths, no_fly_zones = load_data(depth_file, no_fly_file)
#
#     # 参数设置（可根据实际情况调整）
#     distance_threshold = 1.5  # 空间邻域阈值
#     depth_diff_threshold = 1.0  # 深度差异阈值
#
#     # 执行区域分割
#     regions = region_growing(sampling_points, depths,
#                              distance_threshold, depth_diff_threshold)
#
#     # 可视化结果
#     visualize_results(sampling_points, depths, regions, no_fly_zones)


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
# from matplotlib.colors import Normalize
#
#
# def load_data(depth_file, no_fly_file):
#     """加载深度数据和禁飞区定义"""
#     depth_grid = np.loadtxt(depth_file)
#     rows, cols = depth_grid.shape
#
#     # 生成坐标网格（假设网格从(0,0)开始）
#     x_coords = np.arange(cols)
#     y_coords = np.arange(rows)
#
#     # 读取禁飞区
#     no_fly_zones = np.loadtxt(no_fly_file)
#     if no_fly_zones.ndim == 1:
#         no_fly_zones = no_fly_zones.reshape(1, -1)
#
#     # 生成有效采样点
#     sampling_points = []
#     depths = []
#     for y in y_coords:
#         for x in x_coords:
#             # 检查是否在禁飞区内
#             in_no_fly = False
#             for zone in no_fly_zones:
#                 x1, x2, y1, y2 = zone
#                 if x1 <= x <= x2 and y1 <= y <= y2:
#                     in_no_fly = True
#                     break
#             if not in_no_fly:
#                 sampling_points.append([x, y])
#                 depths.append(depth_grid[int(y), int(x)])
#
#     return np.array(sampling_points), np.array(depths), no_fly_zones
#
#
# def region_growing(points, depths, distance_thresh=1.5, depth_thresh=1.0):
#     """改进的区域生长算法确保覆盖所有点"""
#     tree = KDTree(points)
#     neighbors = tree.query_ball_tree(tree, distance_thresh)
#
#     visited = np.zeros(len(points), dtype=bool)
#     regions = []
#
#     for i in range(len(points)):
#         if not visited[i]:
#             stack = [i]
#             visited[i] = True
#             current_region = [i]
#
#             # 区域生长
#             while stack:
#                 current = stack.pop()
#                 # 查找邻近点
#                 for neighbor in neighbors[current]:
#                     if not visited[neighbor]:
#                         # 检查深度差异
#                         if abs(depths[current] - depths[neighbor]) <= depth_thresh:
#                             visited[neighbor] = True
#                             current_region.append(neighbor)
#                             stack.append(neighbor)
#
#             regions.append(current_region)
#
#     # 确保所有点都被包含（处理可能的孤立点）
#     unvisited = np.where(~visited)[0]
#     for idx in unvisited:
#         regions.append([idx])
#
#     return regions
#
#
# def visualize_results(points, depths, regions, no_fly_zones):
#     """改进的可视化：自然形状区域 + 深度颜色映射"""
#     # 计算区域统计信息
#     region_means = [np.mean(depths[region]) for region in regions]
#     region_stds = [np.std(depths[region]) for region in regions]
#
#     # 创建颜色映射
#     norm = Normalize(vmin=np.min(region_means), vmax=np.max(region_means))
#     cmap = plt.get_cmap('viridis')
#
#     plt.figure(figsize=(16, 8))
#
#     # 原始深度分布
#     ax1 = plt.subplot(1, 2, 1)
#     sc = ax1.scatter(points[:, 0], points[:, 1], c=depths, cmap=cmap,
#                      s=40, edgecolor='k', linewidth=0.5)
#     for zone in no_fly_zones:
#         ax1.fill_between([zone[0], zone[1]], zone[2], zone[3],
#                          color='red', alpha=0.3)
#     plt.colorbar(sc, ax=ax1, label='Depth Value')
#     ax1.set_title('Original Depth Distribution')
#
#     # 区域分割结果（自然形状 + 平均深度颜色）
#     ax2 = plt.subplot(1, 2, 2)
#
#     # 为每个区域生成颜色
#     for i, region in enumerate(regions):
#         color = cmap(norm(region_means[i]))
#         # 绘制区域点集
#         ax2.scatter(points[region, 0], points[region, 1],
#                     color=color, s=40, edgecolor='k',
#                     linewidth=0.5)
#
#     # 绘制禁飞区
#     for zone in no_fly_zones:
#         ax2.fill_between([zone[0], zone[1]], zone[2], zone[3],
#                          color='red', alpha=0.3)
#
#     # 创建颜色条（关键修正点）
#     sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
#     sm.set_array([])
#     cbar = plt.colorbar(sm, ax=ax2, label='Average Depth')
#     cbar.ax.tick_params(labelsize=8)
#
#     ax2.set_title('Natural-shaped Depth Regions')
#
#     # 保存统计信息
#     with open('region_statistics.csv', 'w') as f:
#         f.write("RegionID,MeanDepth,StdDepth\n")
#         for i, (mean, std) in enumerate(zip(region_means, region_stds)):
#             f.write(f"{i + 1},{mean:.2f},{std:.2f}\n")
#
#     plt.tight_layout()
#     plt.show()
#
#
# if __name__ == "__main__":
#     # 输入文件路径
#     depth_file = "depth.txt"
#     no_fly_file = "no_fly_zones.txt"
#
#     # 处理数据
#     sampling_points, depths, no_fly_zones = load_data(depth_file, no_fly_file)
#
#     # 参数设置（根据实际情况调整）
#     distance_threshold = 1.5  # 邻域距离阈值（建议为网格间距的1.2-1.5倍）
#     depth_diff_threshold = 1.0  # 深度差异阈值
#
#     # 执行区域分割
#     regions = region_growing(sampling_points, depths,
#                              distance_threshold, depth_diff_threshold)
#
#     # 可视化结果
#     visualize_results(sampling_points, depths, regions, no_fly_zones)


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
# from matplotlib.colors import Normalize
# from matplotlib.patches import Rectangle
#
#
# def load_data(depth_file, no_fly_file):
#     """加载数据并生成网格矩阵"""
#     # 读取原始深度数据
#     depth_grid = np.loadtxt(depth_file)
#     rows, cols = depth_grid.shape
#
#     # 读取禁飞区
#     no_fly_zones = np.loadtxt(no_fly_file)
#     if no_fly_zones.ndim == 1:
#         no_fly_zones = no_fly_zones.reshape(1, -1)
#
#     # 创建有效点掩码矩阵
#     mask = np.ones_like(depth_grid, dtype=bool)
#     for zone in no_fly_zones:
#         x1, x2, y1, y2 = map(int, zone)
#         mask[y1:y2 + 1, x1:x2 + 1] = False
#
#     return depth_grid, mask, no_fly_zones
#
#
# def create_region_map(valid_points, regions, grid_shape):
#     """创建区域填色矩阵"""
#     region_map = np.full(grid_shape, -1, dtype=int)  # -1表示禁飞区
#     region_depth_map = np.full(grid_shape, np.nan)
#
#     for region_id, region in enumerate(regions):
#         for pt_idx in region:
#             y, x = valid_points[pt_idx]
#             region_map[int(y), int(x)] = region_id
#             region_depth_map[int(y), int(x)] = np.mean(valid_depths[region])
#
#     return region_map, region_depth_map
#
#
# def visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones):
#     """连续区域填充可视化"""
#     plt.figure(figsize=(16, 8))
#
#     # 原始深度填充图
#     ax1 = plt.subplot(1, 2, 1)
#     masked_data = np.ma.masked_where(~mask, original_grid)
#     im1 = ax1.imshow(masked_data, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 区域分割填充图
#     ax2 = plt.subplot(1, 2, 2)
#     masked_region = np.ma.masked_where(np.isnan(region_depth_map), region_depth_map)
#     im2 = ax2.imshow(masked_region, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 为两个子图添加统一颜色条
#     plt.colorbar(im1, ax=ax1, label='Depth Value')
#     plt.colorbar(im2, ax=ax2, label='Region Average Depth')
#
#     # 添加禁飞区覆盖层
#     for ax in [ax1, ax2]:
#         for zone in no_fly_zones:
#             x1, x2, y1, y2 = zone
#             ax.add_patch(Rectangle((x1, y1), x2 - x1 + 1, y2 - y1 + 1,
#                                    facecolor='red', alpha=0.3))
#         ax.set_xlim(0, original_grid.shape[1])
#         ax.set_ylim(0, original_grid.shape[0])
#         ax.set_aspect('equal')
#
#     ax1.set_title('Original Depth Distribution')
#     ax2.set_title('Seamless Region Segmentation')
#     plt.tight_layout()
#     plt.show()
#
#
# def region_growing(grid, mask, distance=1.5, depth_diff=1.0):
#     """基于网格的区域生长算法"""
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
# if __name__ == "__main__":
#     # 输入文件
#     depth_file = "depth.txt"
#     no_fly_file = "no_fly_zones.txt"
#
#     # 加载数据
#     original_grid, mask, no_fly_zones = load_data(depth_file, no_fly_file)
#
#     # 区域分割
#     valid_points, valid_depths, regions = region_growing(original_grid, mask,
#                                                          distance=1.5, depth_diff=1.0)
#
#     # 创建填色矩阵
#     region_map, region_depth_map = create_region_map(valid_points, regions, original_grid.shape)
#
#     # 可视化
#     visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones)


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
# from matplotlib.colors import Normalize
# from matplotlib.patches import Rectangle
# import csv
#
#
# def load_data(depth_file, no_fly_file):
#     """加载数据并生成网格矩阵"""
#     depth_grid = np.loadtxt(depth_file)
#     rows, cols = depth_grid.shape
#
#     no_fly_zones = np.loadtxt(no_fly_file)
#     if no_fly_zones.ndim == 1:
#         no_fly_zones = no_fly_zones.reshape(1, -1)
#
#     mask = np.ones_like(depth_grid, dtype=bool)
#     for zone in no_fly_zones:
#         x1, x2, y1, y2 = map(int, zone)
#         mask[y1:y2 + 1, x1:x2 + 1] = False
#
#     return depth_grid, mask, no_fly_zones
#
#
# def create_region_map(valid_points, valid_depths, regions, grid_shape):
#     """创建区域填色矩阵并计算统计信息"""
#     region_map = np.full(grid_shape, -1, dtype=int)
#     region_depth_map = np.full(grid_shape, np.nan)
#     stats = []
#
#     for region_id, region in enumerate(regions):
#         region_depths = valid_depths[region]
#         mean_depth = np.mean(region_depths)
#         std_depth = np.std(region_depths)
#         min_depth = np.min(region_depths)
#         max_depth = np.max(region_depths)
#         area_size = len(region)
#
#         stats.append({
#             'RegionID': region_id + 1,
#             'MeanDepth': mean_depth,
#             'StdDepth': std_depth,
#             'MinDepth': min_depth,
#             'MaxDepth': max_depth,
#             'AreaSize': area_size
#         })
#
#         for pt_idx in region:
#             y, x = valid_points[pt_idx]
#             region_map[int(y), int(x)] = region_id
#             region_depth_map[int(y), int(x)] = mean_depth  # 确保使用平均深度
#
#     return region_map, region_depth_map, stats
#
#
# def visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats):
#     """可视化结果并保存统计信息"""
#     plt.figure(figsize=(16, 8))
#
#     # 原始深度图
#     ax1 = plt.subplot(1, 2, 1)
#     masked_data = np.ma.masked_where(~mask, original_grid)
#     im1 = ax1.imshow(masked_data, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 区域分割图
#     ax2 = plt.subplot(1, 2, 2)
#     masked_region = np.ma.masked_where(np.isnan(region_depth_map), region_depth_map)
#     im2 = ax2.imshow(masked_region, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 添加颜色条
#     plt.colorbar(im1, ax=ax1, label='Depth Value')
#     plt.colorbar(im2, ax=ax2, label='Region Average Depth')
#
#     # 绘制禁飞区
#     for ax in [ax1, ax2]:
#         for zone in no_fly_zones:
#             x1, x2, y1, y2 = zone
#             ax.add_patch(Rectangle((x1, y1), x2 - x1 + 1, y2 - y1 + 1,
#                                    facecolor='red', alpha=0.3))
#         ax.set_xlim(0, original_grid.shape[1])
#         ax.set_ylim(0, original_grid.shape[0])
#         ax.set_aspect('equal')
#
#     ax1.set_title('Original Depth Distribution')
#     ax2.set_title('Depth Region Segmentation')
#
#     # 保存统计信息
#     with open('region_statistics.csv', 'w', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=stats[0].keys())
#         writer.writeheader()
#         writer.writerows(stats)
#
#     plt.tight_layout()
#     plt.show()
#
#
# def region_growing(grid, mask, distance, depth_diff):
#     """
#     区域生长算法
#     参数说明：
#     distance - 空间邻域半径（单位：网格数）：
#        增大：合并更大空间范围 → 区域更少、更大
#        减小：仅合并相邻点 → 区域更多、更小
#
#     depth_diff - 允许的深度差异阈值：
#        增大：允许更大深度差异 → 区域更少
#        减小：需要更相似深度 → 区域更多
#     """
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
# if __name__ == "__main__":
#     # 输入文件
#     depth_file = "depth.txt"
#     no_fly_file = "no_fly_zones.txt"
#
#     # 加载数据
#     original_grid, mask, no_fly_zones = load_data(depth_file, no_fly_file)
#
#     # 参数设置（在此调整关键参数）
#     distance_threshold = 1.5  # 典型范围：1.0-3.0
#     depth_diff_threshold = 1.0  # 典型范围：0.5-2.0
#
#     # 执行区域分割
#     valid_points, valid_depths, regions = region_growing(
#         original_grid, mask,
#         distance=distance_threshold,
#         depth_diff=depth_diff_threshold
#     )
#
#     # 生成填色矩阵和统计信息
#     region_map, region_depth_map, stats = create_region_map(
#         valid_points, valid_depths, regions, original_grid.shape
#     )
#
#     # 可视化并保存结果
#     visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats)


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
# from matplotlib.patches import Rectangle
# import pandas as pd

#
#
# def load_data(depth_file, no_fly_file):
#     """加载数据并生成网格矩阵"""
#     depth_grid = np.loadtxt(depth_file)
#     rows, cols = depth_grid.shape
#
#     no_fly_zones = np.loadtxt(no_fly_file)
#     if no_fly_zones.ndim == 1:
#         no_fly_zones = no_fly_zones.reshape(1, -1)
#
#     mask = np.ones_like(depth_grid, dtype=bool)
#     for zone in no_fly_zones:
#         x1, x2, y1, y2 = map(int, zone)
#         mask[y1:y2 + 1, x1:x2 + 1] = False
#
#     return depth_grid, mask, no_fly_zones
#
#
# def create_region_map(valid_points, valid_depths, regions, grid_shape):
#     """创建区域填色矩阵并计算统计信息"""
#     region_map = np.full(grid_shape, -1, dtype=int)
#     region_depth_map = np.full(grid_shape, np.nan)
#     stats = []
#     region_centers = []
#
#     for region_id, region in enumerate(regions):
#         region_depths = valid_depths[region]
#         region_coords = valid_points[region]
#
#         # 计算统计信息
#         mean_depth = np.mean(region_depths)
#         std_depth = np.std(region_depths)
#         min_depth = np.min(region_depths)
#         max_depth = np.max(region_depths)
#         area_size = len(region)
#         center_y, center_x = np.mean(region_coords, axis=0)
#
#         stats.append({
#             '区域ID': region_id + 1,
#             '平均深度': mean_depth,
#             '深度标准差': std_depth,
#             '最小深度': min_depth,
#             '最大深度': max_depth,
#             '区域面积': area_size,
#             '中心X坐标': center_x,
#             '中心Y坐标': center_y
#         })
#
#         region_centers.append((center_x, center_y))
#
#         # 填充区域矩阵
#         for pt_idx in region:
#             y, x = valid_points[pt_idx]
#             region_map[int(y), int(x)] = region_id
#             region_depth_map[int(y), int(x)] = mean_depth
#
#     return region_map, region_depth_map, stats, region_centers
#
#
# def visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats, region_centers):
#     """可视化结果并添加区域标注"""
#     plt.figure(figsize=(16, 8))
#
#     # 原始深度图
#     ax1 = plt.subplot(1, 2, 1)
#     masked_data = np.ma.masked_where(~mask, original_grid)
#     im1 = ax1.imshow(masked_data, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 区域分割图
#     ax2 = plt.subplot(1, 2, 2)
#     masked_region = np.ma.masked_where(np.isnan(region_depth_map), region_depth_map)
#     im2 = ax2.imshow(masked_region, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 添加区域编号标注
#     for idx, (x, y) in enumerate(region_centers):
#         ax2.text(x, y, f'区域{idx + 1}',
#                  ha='center', va='center',
#                  color='white', fontsize=8,
#                  bbox=dict(facecolor='black', alpha=0.5, boxstyle='round'))
#
#     # 添加颜色条
#     plt.colorbar(im1, ax=ax1, label='深度值')
#     plt.colorbar(im2, ax=ax2, label='区域平均深度')
#
#     # 绘制禁飞区
#     for ax in [ax1, ax2]:
#         for zone in no_fly_zones:
#             x1, x2, y1, y2 = zone
#             ax.add_patch(Rectangle((x1, y1), x2 - x1 + 1, y2 - y1 + 1,
#                                    facecolor='red', alpha=0.3))
#         ax.set_xlim(0, original_grid.shape[1])
#         ax.set_ylim(0, original_grid.shape[0])
#         ax.set_aspect('equal')
#
#     ax1.set_title('原始深度分布')
#     ax2.set_title('深度区域分割（带区域编号）')
#
#     # 保存统计信息到Excel（添加引擎参数）
#     df = pd.DataFrame(stats)
#     df.to_excel('区域统计表.xlsx', index=False, engine='openpyxl')
#
#     plt.tight_layout()
#     plt.show()
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
# if __name__ == "__main__":
#     # 输入文件
#     depth_file = "depth.txt"
#     no_fly_file = "no_fly_zones.txt"
#
#     # 加载数据
#     original_grid, mask, no_fly_zones = load_data(depth_file, no_fly_file)
#
#     # 参数设置
#     distance_threshold = 1.5  # 增大此值合并更大区域
#     depth_diff_threshold = 1.0  # 增大此值允许更大深度差异
#
#     # 执行区域分割
#     valid_points, valid_depths, regions = region_growing(
#         original_grid, mask,
#         distance=distance_threshold,
#         depth_diff=depth_diff_threshold
#     )
#
#     # 生成填色矩阵和统计信息
#     region_map, region_depth_map, stats, centers = create_region_map(
#         valid_points, valid_depths, regions, original_grid.shape
#     )
#
#     # 可视化并保存结果
#     visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats, centers)


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import KDTree
# from matplotlib.patches import Rectangle
# import pandas as pd
#
#
# def load_data(depth_file, no_fly_file):
#     """加载数据并生成网格矩阵"""
#     depth_grid = np.loadtxt(depth_file)
#     rows, cols = depth_grid.shape
#
#     no_fly_zones = np.loadtxt(no_fly_file)
#     if no_fly_zones.ndim == 1:
#         no_fly_zones = no_fly_zones.reshape(1, -1)
#
#     mask = np.ones_like(depth_grid, dtype=bool)
#     for zone in no_fly_zones:
#         x1, x2, y1, y2 = map(int, zone)
#         mask[y1:y2 + 1, x1:x2 + 1] = False
#
#     return depth_grid, mask, no_fly_zones
#
#
# def find_label_position(points):
#     """确保标签位置在区域内"""
#     # 使用区域点集构建KDTree
#     tree = KDTree(points)
#
#     # 计算几何中心
#     center = np.mean(points, axis=0)
#
#     # 寻找距离中心最近的区域点
#     dist, idx = tree.query(center)
#     return points[idx]
#
#
# def create_region_map(valid_points, valid_depths, regions, grid_shape):
#     """创建区域填色矩阵并计算统计信息"""
#     region_map = np.full(grid_shape, -1, dtype=int)
#     region_depth_map = np.full(grid_shape, np.nan)
#     stats = []
#     label_positions = []
#
#     for region_id, region in enumerate(regions):
#         region_depths = valid_depths[region]
#         region_coords = valid_points[region]
#
#         # 计算统计信息
#         mean_depth = np.mean(region_depths)
#         std_depth = np.std(region_depths)
#         min_depth = np.min(region_depths)
#         max_depth = np.max(region_depths)
#         area_size = len(region)
#
#         # 寻找标签位置
#         label_pos = find_label_position(region_coords)
#         label_positions.append(label_pos)
#
#         stats.append({
#             '区域ID': region_id + 1,
#             '平均深度': mean_depth,
#             '深度标准差': std_depth,
#             '最小深度': min_depth,
#             '最大深度': max_depth,
#             '区域面积': area_size
#         })
#
#         # 填充区域矩阵
#         for pt_idx in region:
#             y, x = valid_points[pt_idx]
#             region_map[int(y), int(x)] = region_id
#             region_depth_map[int(y), int(x)] = mean_depth
#
#     return region_map, region_depth_map, stats, label_positions
#
#
# def visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats, label_positions):
#     """可视化结果并添加区域标注"""
#     plt.figure(figsize=(16, 8))
#
#     # 原始深度图
#     ax1 = plt.subplot(1, 2, 1)
#     masked_data = np.ma.masked_where(~mask, original_grid)
#     im1 = ax1.imshow(masked_data, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 区域分割图
#     ax2 = plt.subplot(1, 2, 2)
#     masked_region = np.ma.masked_where(np.isnan(region_depth_map), region_depth_map)
#     im2 = ax2.imshow(masked_region, cmap='viridis', origin='lower',
#                      extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
#
#     # 添加区域编号标注
#     for idx, (x, y) in enumerate(label_positions):
#         ax2.text(x, y, f'区域{idx + 1}',
#                  ha='center', va='center',
#                  color='white', fontsize=8,
#                  bbox=dict(facecolor='black', alpha=0.5, boxstyle='round'))
#
#     # 添加颜色条
#     plt.colorbar(im1, ax=ax1, label='深度值')
#     plt.colorbar(im2, ax=ax2, label='区域平均深度')
#
#     # 绘制禁飞区
#     for ax in [ax1, ax2]:
#         for zone in no_fly_zones:
#             x1, x2, y1, y2 = zone
#             ax.add_patch(Rectangle((x1, y1), x2 - x1 + 1, y2 - y1 + 1,
#                                    facecolor='red', alpha=0.3))
#         ax.set_xlim(0, original_grid.shape[1])
#         ax.set_ylim(0, original_grid.shape[0])
#         ax.set_aspect('equal')
#
#     ax1.set_title('原始深度分布')
#     ax2.set_title('深度区域分割（带区域编号）')
#
#     # 保存统计信息到Excel
#     df = pd.DataFrame(stats)
#     df.to_excel('区域统计表.xlsx', index=False, engine='openpyxl')
#
#     plt.tight_layout()
#     plt.show()
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
# if __name__ == "__main__":
#     # 输入文件
#     depth_file = "depth.txt"
#     no_fly_file = "no_fly_zones.txt"
#
#     # 加载数据
#     original_grid, mask, no_fly_zones = load_data(depth_file, no_fly_file)
#
#     # 参数设置
#     distance_threshold = 1.5  # 增大此值合并更大区域
#     depth_diff_threshold = 1.0  # 增大此值允许更大深度差异
#
#     # 执行区域分割
#     valid_points, valid_depths, regions = region_growing(
#         original_grid, mask,
#         distance=distance_threshold,
#         depth_diff=depth_diff_threshold
#     )
#
#     # 生成填色矩阵和统计信息
#     region_map, region_depth_map, stats, label_pos = create_region_map(
#         valid_points, valid_depths, regions, original_grid.shape
#     )
#
#     # 可视化并保存结果
#     visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats, label_pos)


import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.patches import Rectangle
import pandas as pd


def load_no_fly_zones(no_fly_file):
    """加载禁飞区信息和区域尺寸"""
    with open(no_fly_file, 'r') as f:
        lines = f.readlines()

    # 解析区域尺寸
    width, height = map(float, lines[0].strip().split())

    # 解析禁飞区
    no_fly_zones = []
    for line in lines[1:]:
        x1, x2, y1, y2 = map(float, line.strip().split())
        no_fly_zones.append((x1, x2, y1, y2))

    return width, height, no_fly_zones


def generate_flight_path(width, height, no_fly_zones, step=0.5):
    """生成蛇形避障航迹（增加边界约束）"""
    path = []
    y = 0.0
    direction = 1  # 扫描方向：1向右，-1向左

    while y <= height:
        x_start = 0.0 if direction == 1 else width
        x_end = width if direction == 1 else 0.0

        # 当前行采样点（限制在有效范围内）
        x_values = np.clip(
            np.arange(x_start, x_end + step / 2, step * direction),
            0.0, width
        )

        for x in x_values:
            # 检查是否在禁飞区内
            in_no_fly = False
            for (x1, x2, y1, y2) in no_fly_zones:
                if (x1 <= x <= x2) and (y1 <= y <= y2):
                    in_no_fly = True
                    break
            if not in_no_fly:
                path.append((x, y))

        # 移动到下一行（限制在有效范围内）
        y = min(y + step, height)
        direction *= -1

    return np.array(path)


def save_flight_data(flight_path, path_file):
    """保存航迹和深度采样数据（修正坐标转换）"""
    # 保存航迹点
    np.savetxt(path_file, flight_path, fmt='%.2f', delimiter=',')
    #
    # # 获取深度矩阵尺寸
    # rows, cols = depth_grid.shape
    #
    # # 采样深度数据（带坐标转换）
    # sampled_depths = []
    # for x, y in flight_path:
    #     # 坐标转换为矩阵索引
    #     col = int(round((x / width) * (cols - 1)))
    #     row = int(round((y / height) * (rows - 1)))
    #
    #     # 边界检查
    #     col = np.clip(col, 0, cols - 1)
    #     row = np.clip(row, 0, rows - 1)
    #
    #     sampled_depths.append(depth_grid[row, col])
    #
    # # 保存深度数据
    # np.savetxt(depth_file, sampled_depths, fmt='%.4f')


def load_depth_data(depth_file):
    """加载深度矩阵"""
    return np.loadtxt(depth_file)


def create_region_map(valid_points, valid_depths, regions, grid_shape):
    """创建区域填色矩阵并计算统计信息"""
    region_map = np.full(grid_shape, -1, dtype=int)
    region_depth_map = np.full(grid_shape, np.nan)
    stats = []
    label_positions = []

    for region_id, region in enumerate(regions):
        region_depths = valid_depths[region]
        region_coords = valid_points[region]

        # 计算统计信息
        mean_depth = np.mean(region_depths)
        std_depth = np.std(region_depths)
        min_depth = np.min(region_depths)
        max_depth = np.max(region_depths)
        area_size = len(region)

        # 寻找标签位置
        label_pos = find_label_position(region_coords)
        label_positions.append(label_pos)

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


def find_label_position(points):
    """确保标签位置在区域内"""
    tree = KDTree(points)
    center = np.mean(points, axis=0)
    dist, idx = tree.query(center)
    return points[idx]


def visualize_results(original_grid, region_depth_map, mask, no_fly_zones, stats, label_positions):
    """可视化结果并添加区域标注"""
    plt.figure(figsize=(16, 8))

    # 原始深度图
    ax1 = plt.subplot(1, 2, 1)
    masked_data = np.ma.masked_where(~mask, original_grid)
    im1 = ax1.imshow(masked_data, cmap='viridis', origin='lower',
                     extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])

    # 区域分割图
    ax2 = plt.subplot(1, 2, 2)
    masked_region = np.ma.masked_where(np.isnan(region_depth_map), region_depth_map)
    im2 = ax2.imshow(masked_region, cmap='viridis', origin='lower',
                     extent=[0, original_grid.shape[1], 0, original_grid.shape[0]])
    # 添加区域编号标注
    for idx, (x, y) in enumerate(label_positions):
        ax2.text(x, y, f'区域{idx + 1}',
                 ha='center', va='center',
                 color='white', fontsize=8,
                 bbox=dict(facecolor='black', alpha=0.5, boxstyle='round'))

    # 添加颜色条
    plt.colorbar(im1, ax=ax1, label='深度值')
    plt.colorbar(im2, ax=ax2, label='区域平均深度')

    # 绘制禁飞区
    for ax in [ax1, ax2]:
        for (x1, x2, y1, y2) in no_fly_zones:
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
                                   facecolor='red', alpha=0.3))
        ax.set_xlim(0, original_grid.shape[1])
        ax.set_ylim(0, original_grid.shape[0])
        ax.set_aspect('equal')

    ax1.set_title('原始深度分布')
    ax2.set_title('深度区域分割（带区域编号）')

    # 保存统计信息
    df = pd.DataFrame(stats)
    df.to_excel('区域统计表.xlsx', index=False, engine='openpyxl')

    plt.tight_layout()
    plt.show()


def region_growing(grid, mask, distance=1.5, depth_diff=1.0):
    """改进的区域生长算法"""
    valid_points = np.argwhere(mask)
    valid_depths = grid[mask]

    tree = KDTree(valid_points)
    neighbors = tree.query_ball_tree(tree, distance)

    visited = np.zeros(len(valid_points), dtype=bool)
    regions = []

    for i in range(len(valid_points)):
        if not visited[i]:
            stack = [i]
            visited[i] = True
            current_region = [i]

            while stack:
                current = stack.pop()
                for neighbor in neighbors[current]:
                    if not visited[neighbor]:
                        if abs(valid_depths[current] - valid_depths[neighbor]) <= depth_diff:
                            visited[neighbor] = True
                            current_region.append(neighbor)
                            stack.append(neighbor)
            regions.append(current_region)

    return valid_points, valid_depths, regions
# 其余函数保持不变（create_region_map, find_label_position, visualize_results, region_growing）

if __name__ == "__main__":
    # 输入文件
    no_fly_file = "no_fly_zones.txt"
    depth_file = "depth.txt"

    # 步骤1：加载数据
    width, height, no_fly_zones = load_no_fly_zones(no_fly_file)
    depth_grid = load_depth_data(depth_file)

    # 步骤2：生成并保存航迹
    flight_path = generate_flight_path(width, height, no_fly_zones)
    save_flight_data(flight_path,
                     "flight_path.txt",
                     )

    # 步骤3：区域分割分析
    mask = np.ones_like(depth_grid, dtype=bool)
    for (x1, x2, y1, y2) in no_fly_zones:
        # 坐标转换为矩阵索引
        rows, cols = depth_grid.shape
        x1_idx = int(round((x1 / width) * (cols - 1)))
        x2_idx = int(round((x2 / width) * (cols - 1)))
        y1_idx = int(round((y1 / height) * (rows - 1)))
        y2_idx = int(round((y2 / height) * (rows - 1)))

        mask[y1_idx:y2_idx + 1, x1_idx:x2_idx + 1] = False

    valid_points, valid_depths, regions = region_growing(depth_grid, mask)
    region_map, region_depth_map, stats, label_pos = create_region_map(
        valid_points, valid_depths, regions, depth_grid.shape)

    visualize_results(depth_grid, region_depth_map, mask, no_fly_zones, stats, label_pos)