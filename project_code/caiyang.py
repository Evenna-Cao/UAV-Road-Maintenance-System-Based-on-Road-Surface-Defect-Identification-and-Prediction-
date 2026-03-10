import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.patches import Rectangle
import pandas as pd
import random
import matplotlib
import matplotlib.pyplot as plt

# 全局设置字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

# ================== 核心函数 ==================
def load_no_fly_zones(no_fly_file):
    """加载禁飞区信息"""
    with open(no_fly_file, 'r') as f:
        lines = f.readlines()

    width, height = map(float, lines[0].strip().split())
    no_fly_zones = [tuple(map(float, line.strip().split())) for line in lines[1:]]
    return width, height, no_fly_zones


def generate_flight_path(width, height, no_fly_zones, step=0.5, check_ratio=0.1):
    """生成并保存航迹文件"""
    path = []

    # 主扫描路径（蛇形）
    y = 0.0
    direction = 1
    while y <= height:
        x_start = 0.0 if direction == 1 else width
        x_values = np.linspace(x_start, width - x_start, int(width / step) + 1)

        # 常规采样点
        for x in x_values:
            x = round(x, 2)
            y_round = round(y, 2)
            if not any((x1 <= x <= x2) and (y1 <= y_round <= y2)
                       for (x1, x2, y1, y2) in no_fly_zones):
                path.append((x, y_round))

        # 随机检测点（按比例）
        for (x1, x2, y1, y2) in no_fly_zones:
            num_checks = int((x2 - x1) * (y2 - y1) * check_ratio)
            for _ in range(num_checks):
                x = round(random.uniform(x1, x2), 2)
                y = round(random.uniform(y1, y2), 2)
                path.append((x, y))

        y = round(y + step, 2)
        direction *= -1

    # 保存航迹文件
    np.savetxt("flight_path.txt", path, fmt="%.2f", delimiter=",")
    return np.array(path)


def validate_depth_data(flight_path, depths, no_fly_zones, threshold=2.0):
    """深度数据验证"""
    nofly_depths = []
    normal_depths = []

    for (x, y), depth in zip(flight_path, depths):
        in_nofly = any((x1 <= x <= x2) and (y1 <= y <= y2)
                       for (x1, x2, y1, y2) in no_fly_zones)
        if in_nofly:
            nofly_depths.append(depth)
        else:
            normal_depths.append(depth)

    # 基本统计验证
    if len(nofly_depths) == 0:
        raise ValueError("禁飞区没有采样点，请检查航迹规划")

    nofly_mean = np.mean(nofly_depths)
    normal_mean = np.mean(normal_depths)

    print("深度验证报告：")
    print(f"禁飞区平均深度：{nofly_mean:.2f}（{len(nofly_depths)}个点）")
    print(f"正常区平均深度：{normal_mean:.2f}（{len(normal_depths)}个点）")
    print(f"深度差异倍数：{nofly_mean / normal_mean:.1f}x")

    if nofly_mean / normal_mean < threshold:
        raise ValueError(f"禁飞区深度不足正常区域的{threshold}倍，数据异常！")


def reconstruct_depth_matrix(flight_path, depths, width, height):
    """重建深度矩阵"""
    # 获取坐标序列
    x_coords = np.unique(flight_path[:, 0])
    y_coords = np.unique(flight_path[:, 1])

    # 创建空矩阵
    depth_grid = np.full((len(y_coords), len(x_coords)), np.nan)

    # 建立坐标映射
    x_index = {x: i for i, x in enumerate(sorted(x_coords))}
    y_index = {y: i for i, y in enumerate(sorted(y_coords))}

    # 填充数据
    for (x, y), depth in zip(flight_path, depths):
        depth_grid[y_index[y], x_index[x]] = depth

    return depth_grid, x_coords, y_coords


def create_mask(grid_shape, no_fly_zones, x_coords, y_coords):
    """创建有效区域掩码"""
    rows, cols = grid_shape
    mask = np.ones(grid_shape, dtype=bool)

    # 转换为网格索引
    for (x1, x2, y1, y2) in no_fly_zones:
        col_start = np.searchsorted(x_coords, x1, side='left')
        col_end = np.searchsorted(x_coords, x2, side='right')
        row_start = np.searchsorted(y_coords, y1, side='left')
        row_end = np.searchsorted(y_coords, y2, side='right')
        mask[row_start:row_end, col_start:col_end] = False

    return mask


def process_regions(depth_grid, mask):
    """执行区域分割"""
    valid_points = np.argwhere(~np.isnan(depth_grid) & mask)
    valid_depths = depth_grid[~np.isnan(depth_grid) & mask]

    # KDTree加速邻近搜索
    tree = KDTree(valid_points)
    regions = []
    visited = np.zeros(len(valid_points), dtype=bool)

    # 区域生长算法
    for i in range(len(valid_points)):
        if not visited[i]:
            stack = [i]
            current_region = []
            while stack:
                idx = stack.pop()
                if not visited[idx]:
                    visited[idx] = True
                    current_region.append(idx)
                    # 查找邻近点（距离<=1.5个网格）
                    neighbors = tree.query_ball_point(valid_points[idx], 1.5)
                    stack.extend(neighbors)
            regions.append(current_region)

    return valid_points, valid_depths, regions


def save_results(depth_grid, x_coords, y_coords, regions, valid_points, valid_depths):
    """保存所有输出结果"""
    # 保存完整深度表
    df_depth = pd.DataFrame(
        index=np.round(y_coords, 2),
        columns=np.round(x_coords, 2),
        data=depth_grid
    )
    df_depth.to_excel("完整深度分布.xlsx", na_rep='N/A')

    # 生成区域统计
    stats = []
    region_map = np.full_like(depth_grid, -1)
    for rid, region in enumerate(regions):
        pts = valid_points[region]
        depths = valid_depths[region]
        region_map[pts[:, 0], pts[:, 1]] = rid

        stats.append({
            '区域ID': rid + 1,
            '平均深度': np.mean(depths),
            '深度标准差': np.std(depths),
            '最小深度': np.min(depths),
            '最大深度': np.max(depths),
            '区域面积': len(region),
            '中心X': x_coords[int(np.median(pts[:, 1]))],
            '中心Y': y_coords[int(np.median(pts[:, 0]))]
        })

    pd.DataFrame(stats).to_excel("区域统计表.xlsx", index=False)

    # 可视化
    plt.figure(figsize=(18, 9))

    # 原始深度分布
    plt.subplot(1, 2, 1)
    plt.imshow(depth_grid, cmap='viridis', extent=[x_coords[0], x_coords[-1], y_coords[0], y_coords[-1]])
    plt.colorbar(label='深度值')
    plt.title("原始深度分布")

    # 区域分割结果
    plt.subplot(1, 2, 2)
    plt.imshow(region_map, cmap='tab20', extent=[x_coords[0], x_coords[-1], y_coords[0], y_coords[-1]])
    plt.colorbar(label='区域ID')
    plt.title("深度区域分割")

    plt.savefig('分析结果.png', dpi=300, bbox_inches='tight')
    plt.close()


# ================== 主流程 ==================
if __name__ == "__main__":
    try:
        # 1. 加载禁飞区
        width, height, no_fly_zones = load_no_fly_zones("no_fly_zones.txt")

        # 2. 生成并保存航迹
        flight_path = generate_flight_path(width, height, no_fly_zones)
        print("航迹文件已生成：flight_path.txt")

        # 3. 加载采样数据
        depths = np.loadtxt("sampled_depths.txt")
        print(f"已加载{len(depths)}个深度采样数据")

        # 4. 深度验证
        validate_depth_data(flight_path, depths, no_fly_zones)

        # 5. 重建深度矩阵
        depth_grid, x_coords, y_coords = reconstruct_depth_matrix(flight_path, depths, width, height)

        # 6. 创建掩码
        mask = create_mask(depth_grid.shape, no_fly_zones, x_coords, y_coords)

        # 7. 区域分割
        valid_points, valid_depths, regions = process_regions(depth_grid, mask)

        # 8. 保存结果
        save_results(depth_grid, x_coords, y_coords, regions, valid_points, valid_depths)
        print("处理成功完成！输出文件：")
        print("- 完整深度分布.xlsx")
        print("- 区域统计表.xlsx")
        print("- 分析结果.png")

    except Exception as e:
        print(f"\n处理终止：{str(e)}")
        exit(1)