import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from matplotlib.patches import Rectangle
import pandas as pd
import random
import heapq
import matplotlib
import matplotlib.pyplot as plt

# 全局设置字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

# ================== A*算法核心模块 ==================
class PathPlanner:
    class Node:
        """A*算法节点类"""

        def __init__(self, x, y, parent=None):
            self.x = x
            self.y = y
            self.parent = parent
            self.g = 0  # 实际代价
            self.h = 0  # 启发式代价
            self.f = 0  # 总代价

        def __lt__(self, other):
            return self.f < other.f

    def __init__(self, grid_size=0.5):
        self.grid_size = grid_size
        self.movements = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]  # 8方向移动

    def heuristic(self, a, b):
        """改进启发函数：对角线距离优先"""
        dx = abs(a.x - b.x)
        dy = abs(a.y - b.y)
        return 1.414 * min(dx, dy) + abs(dx - dy)

    def calculate_threat(self, x, y, no_fly_zones, threat_weights):
        """计算位置威胁度"""
        threat = 0
        for (x1, x2, y1, y2), weight in zip(no_fly_zones, threat_weights):
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            distance = np.hypot(x - center_x, y - center_y)
            threat += weight / (distance + 1e-6)
        return threat

    def astar(self, start, goal, no_fly_zones, threat_weights):
        """改进A*路径规划"""
        open_list = []
        closed_set = set()

        start_node = self.Node(*start)
        goal_node = self.Node(*goal)
        heapq.heappush(open_list, start_node)

        while open_list:
            current = heapq.heappop(open_list)

            if (current.x, current.y) == (goal_node.x, goal_node.y):
                path = []
                while current:
                    path.append((current.x, current.y))
                    current = current.parent
                return path[::-1]

            closed_set.add((current.x, current.y))

            for dx, dy in self.movements:
                x = current.x + dx * self.grid_size
                y = current.y + dy * self.grid_size

                # 碰撞检测与边界检查
                if any((x1 <= x <= x2) and (y1 <= y <= y2) for (x1, x2, y1, y2) in no_fly_zones):
                    continue
                if x < 0 or x > goal_node.x or y < 0 or y > goal_node.y:
                    continue

                # 威胁度代价计算
                threat_cost = self.calculate_threat(x, y, no_fly_zones, threat_weights)

                node = self.Node(x, y, current)
                node.g = current.g + np.hypot(dx, dy) * (1 + 0.3 * threat_cost)
                node.h = self.heuristic(node, goal_node)
                node.f = node.g + node.h

                if (node.x, node.y) in closed_set:
                    continue

                # 更新开放列表
                if not any(n.x == node.x and n.y == node.y and n.f <= node.f for n in open_list):
                    heapq.heappush(open_list, node)

        return None  # 无可行路径

    def path_smoothing(self, path):
        """路径插值优化"""
        if not path:
            return []

        optimized = []
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            steps = int(np.hypot(x2 - x1, y2 - y1) / self.grid_size)
            for t in np.linspace(0, 1, max(2, steps)):
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                optimized.append((round(x, 2), round(y, 2)))
        return optimized


# ================== 系统核心模块 ==================
def load_no_fly_zones(no_fly_file):
    """加载禁飞区信息"""
    with open(no_fly_file, 'r') as f:
        lines = f.readlines()

    width, height = map(float, lines[0].strip().split())
    no_fly_zones = [tuple(map(float, line.strip().split())) for line in lines[1:]]
    return width, height, no_fly_zones


def generate_flight_path(width, height, no_fly_zones):
    """改进路径规划主函数"""
    planner = PathPlanner(grid_size=0.5)

    # 生成全局路径
    start = (0.0, 0.0)
    goal = (width, height)
    threat_weights = [1 + (x2 - x1) * (y2 - y1) / (width * height) for (x1, x2, y1, y2) in no_fly_zones]

    global_path = planner.astar(start, goal, no_fly_zones, threat_weights)
    if not global_path:
        raise RuntimeError("无法找到可行路径，请检查禁飞区设置")

    # 路径优化与采样
    optimized_path = planner.path_smoothing(global_path)

    # 添加随机检测点（禁飞区10%密度）
    for (x1, x2, y1, y2) in no_fly_zones:
        num_checks = int((x2 - x1) * (y2 - y1) * 0.1)
        for _ in range(num_checks):
            x = round(random.uniform(x1, x2), 2)
            y = round(random.uniform(y1, y2), 2)
            optimized_path.append((x, y))

    np.savetxt("flight_path.txt", optimized_path, fmt="%.2f", delimiter=",")
    return np.array(optimized_path)


# 后续模块保持不变（validate_depth_data, reconstruct_depth_matrix, create_mask, process_regions, save_results）
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