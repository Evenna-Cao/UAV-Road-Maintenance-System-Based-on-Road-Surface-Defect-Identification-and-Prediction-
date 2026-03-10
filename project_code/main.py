import matplotlib
import matplotlib.pyplot as plt

# 全局设置字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.patches import Rectangle
import pandas as pd


def load_data(depth_file, no_fly_file):
    """加载数据并生成网格矩阵"""
    depth_grid = np.loadtxt(depth_file)
    rows, cols = depth_grid.shape

    no_fly_zones = np.loadtxt(no_fly_file)
    if no_fly_zones.ndim == 1:
        no_fly_zones = no_fly_zones.reshape(1, -1)

    mask = np.ones_like(depth_grid, dtype=bool)
    for zone in no_fly_zones:
        x1, x2, y1, y2 = map(int, zone)
        mask[y1:y2 + 1, x1:x2 + 1] = False

    return depth_grid, mask, no_fly_zones


def find_label_position(points):
    """确保标签位置在区域内"""
    # 使用区域点集构建KDTree
    tree = KDTree(points)

    # 计算几何中心
    center = np.mean(points, axis=0)

    # 寻找距离中心最近的区域点
    dist, idx = tree.query(center)
    return points[idx]


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


def visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats, label_positions):
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
        for zone in no_fly_zones:
            x1, x2, y1, y2 = zone
            ax.add_patch(Rectangle((x1, y1), x2 - x1 + 1, y2 - y1 + 1,
                                   facecolor='red', alpha=0.3))
        ax.set_xlim(0, original_grid.shape[1])
        ax.set_ylim(0, original_grid.shape[0])
        ax.set_aspect('equal')

    ax1.set_title('原始深度分布')
    ax2.set_title('深度区域分割（带区域编号）')

    # 保存统计信息到Excel
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


if __name__ == "__main__":
    # 输入文件
    depth_file = "depth.txt"
    no_fly_file = "no_fly_zones.txt"

    # 加载数据
    original_grid, mask, no_fly_zones = load_data(depth_file, no_fly_file)

    # 参数设置
    distance_threshold = 1.5  # 增大此值合并更大区域
    depth_diff_threshold = 1.0  # 增大此值允许更大深度差异

    # 执行区域分割
    valid_points, valid_depths, regions = region_growing(
        original_grid, mask,
        distance=distance_threshold,
        depth_diff=depth_diff_threshold
    )

    # 生成填色矩阵和统计信息
    region_map, region_depth_map, stats, label_pos = create_region_map(
        valid_points, valid_depths, regions, original_grid.shape
    )

    # 可视化并保存结果
    visualize_filled_results(original_grid, region_depth_map, mask, no_fly_zones, stats, label_pos)
