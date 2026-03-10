import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import glob
import matplotlib.font_manager as fm
import os
import warnings
import random
import math

warnings.filterwarnings("ignore")

# ==================== 字体配置 ====================
try:
    plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
except:
    font_path = 'arial.ttf'
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()


# ==================== 模型定义 ====================
def model_non_paved(t, alpha, gamma, beta, c):
    """非铺装路面模型：指数衰减 + 线性趋势"""
    return alpha * np.exp(-gamma * t) + beta * t + c


def model_paved(t, A, k, fre0, K_base):
    """铺装路面模型：蒙特卡洛积分模型"""
    return K_base * (A * (1 - np.exp(-k * t)) / k + K_base * fre0 * t)

    # ==================== 模型选择器 ====================


def get_model_config(data_dir):
    """根据目录名称选择模型"""
    if "非铺装路面" in data_dir:
        return {
            "model_type": "non_paved",
            "model_func": model_non_paved,
            "fit_params": {
                "p0": lambda d: [max(d) - min(d), 0.1, (max(d) - min(d)) / 10, min(d)],
                "param_names": ["alpha", "gamma", "beta", "c"]
            }
        }
    elif "铺装路面" in data_dir:
        return {
            "model_type": "paved",
            "model_func": model_paved,
            "fit_params": {
                "p0": lambda d: [1000, 0.1, 500, 1e-5],  # 示例初始值
                "param_names": ["A", "k", "fre0", "K_base"]
            }
        }
    else:
        raise ValueError("目录名称必须包含'非铺装路面'或'铺装路面'")


# ==================== 分析核心 ====================
def analyze_files(data_dir="./data"):
    # 获取模型配置
    config = get_model_config(data_dir)

    # 加载数据
    file_list = glob.glob(os.path.join(data_dir, "*.xlsx"))
    if not file_list:
        raise FileNotFoundError(f"在目录 {data_dir} 中未找到Excel文件")

    all_data = []
    for file_path in file_list:
        try:
            filename = os.path.basename(file_path)
            year = int(''.join(filter(str.isdigit, filename)))
            df = pd.read_excel(file_path, sheet_name="Sheet1")
            df['年份'] = year
            all_data.append(df)
            print(f"✓ 成功加载: {filename} (年份: {year})")
        except Exception as e:
            print(f"× 文件 {filename} 加载失败: {str(e)}")
            continue

    combined = pd.concat(all_data).sort_values(['区域ID', '年份'])
    results = {}

    # 按区域分析
    for region_id, group in combined.groupby('区域ID'):
        t = group['年份'].values.astype(float)
        d = group['平均深度'].values.astype(float)
        t_relative = t - min(t)  # 转换为相对时间

        try:
            if config["model_type"] == "non_paved":
                # 标准曲线拟合
                params, _ = curve_fit(
                    config["model_func"],
                    t, d,
                    p0=config["fit_params"]["p0"](d),
                    maxfev=5000
                )
            elif config["model_type"] == "paved":
                # 蒙特卡洛参数搜索
                params = monte_carlo_fit(t_relative, d, config)

            # 保存结果
            results[region_id] = process_results(region_id, t, d, params, config)

        except Exception as e:
            print(f"区域 {region_id} 分析失败: {str(e)}")
            continue

    # 生成报告
    print("\n" + "=" * 60)
    print(f"{' 磨损深度分析报告 ':=^60}")
    print("=" * 60)

    for rid, data in results.items():
        print(f"\n▶ 区域 {rid}")
        print(f"  模型类型: {config['model_type']}")
        print(f"  数学模型: {data['模型公式']}")

        # 预测未来10年
        print("\n  未来预测:")
        for year in range(int(data['最后年份']) + 1, int(data['最后年份']) + 11):
            if config["model_type"] == "non_paved":
                pred = config["model_func"](year, *data['参数'])
            else:
                pred = config["model_func"](
                    year - data['基准年份'], *data['参数']
                )
            print(f"  第{year}年: {pred:.2f} mm")


# ==================== 蒙特卡洛拟合 ====================
def monte_carlo_fit(t, d, config, iterations=1000):
    """铺装路面专用拟合方法"""
    best_params = None
    min_error = float('inf')

    # 参数搜索范围（可根据实际调整）
    search_ranges = {
        'A': (500, 1500),
        'k': (0.05, 0.2),
        'fre0': (300, 700),
        'K_base': (1e-6, 1e-4)
    }

    for _ in range(iterations):
        params = [
            random.uniform(*search_ranges[name])
            for name in config["fit_params"]["param_names"]
        ]
        try:
            pred = config["model_func"](t, *params)
            error = np.mean((pred - d) ** 2)
            if error < min_error:
                min_error = error
                best_params = params
        except:
            continue

    return best_params


# ==================== 结果处理 ====================
def process_results(region_id, t, d, params, config):
    """统一处理结果格式"""
    result = {
        '参数': params,
        '基准年份': min(t),
        '最后年份': max(t)
    }

    if config["model_type"] == "non_paved":
        alpha, gamma, beta, c = params
        result['模型公式'] = (
            f"d(t) = {alpha:.2f}·e^(-{gamma:.3f}t) + {beta:.3f}t + {c:.2f}"
        )
    else:
        A, k, fre0, K_base = params
        result['模型公式'] = (
            f"d(t) = {K_base:.2e}[{A:.0f}(1-e^(-{k:.3f}t))/{k:.3f} + {fre0:.1f}t]"
        )

    # 生成预测曲线
    plt.figure(figsize=(10, 6))
    t_plot = np.linspace(min(t), max(t) + 10, 100)

    if config["model_type"] == "non_paved":
        plt.plot(t_plot, config["model_func"](t_plot, *params), 'r--', lw=2)
    else:
        plt.plot(t_plot, config["model_func"](t_plot - min(t), *params), 'r--', lw=2)

    plt.scatter(t, d, s=80, edgecolors='k')
    plt.title(f'区域 {region_id} 分析结果 ({config["model_type"]})')
    plt.savefig(f'区域_{region_id}_分析结果.png')
    plt.close()

    return result


# ==================== 主程序 ====================
if __name__ == "__main__":
    print("""\n
     路面磨损深度分析系统 
    1. 准备数据目录，名称必须包含"铺装路面"或"非铺装路面"
    2. Excel文件命名需包含年份（如：2023年数据.xlsx）
    3. 每个文件需包含Sheet1，含[区域ID]和[平均深度]列
    """)

    # 自动识别数据目录
    data_dirs = [d for d in os.listdir() if os.path.isdir(d) and "data" in d]

    for data_dir in data_dirs:
        print(f"\n正在分析目录: {data_dir}")
        try:
            analyze_files(data_dir)
        except Exception as e:
            print(f"分析失败: {str(e)}")

    print("\n★ 全部分析完成！结果已保存至当前目录")