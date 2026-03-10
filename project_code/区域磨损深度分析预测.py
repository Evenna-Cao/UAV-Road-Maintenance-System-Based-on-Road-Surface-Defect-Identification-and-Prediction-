# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
# import glob
# import matplotlib.font_manager as fm
# import os
#
# # ==================== 字体安装与配置 ====================
# # 安装SimHei字体（如果尚未安装）
# if not os.path.exists('simhei.ttf'):
#     !wget -O simhei.ttf "https://www.wfonts.com/download/data/2014/06/01/simhei/chinese.simhei.ttf"
#
# # 将字体文件添加到matplotlib字体路径
# font_path = 'simhei.ttf'
# font_prop = fm.FontProperties(fname=font_path)
#
# # 设置全局字体
# plt.rcParams['font.family'] = font_prop.get_name()
# plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#
# # 验证字体是否生效
# # print(f"当前使用字体: {plt.rcParams['font.family']}")
#
# # ==================== 上传文件 ====================
# #根据文件个数可多次执行次部分
# from google.colab import files
# uploaded = files.upload()
#
# # ==================== 分析函数 ====================
# def depth_model(t, alpha, gamma, beta , c):
#     return alpha * np.exp(-gamma * t) + beta*t +c
#
# def analyze_uploaded_files():
#     # 获取已上传的Excel文件
#     file_list = glob.glob("*.xlsx")
#
#     if not file_list:
#         raise ValueError("没有找到Excel文件，请先上传文件")
#
#     # 读取并合并数据
#     all_data = []
#     for file_path in file_list:
#         try:
#             df = pd.read_excel(file_path, sheet_name="Sheet1")
#             year = int(''.join(filter(str.isdigit, os.path.splitext(os.path.basename(file_path))[0])))
#             df['年份'] = year
#             all_data.append(df)
#             print(f"已读取: {file_path} (年份: {year})")
#         except Exception as e:
#             print(f"文件 {file_path} 读取失败: {str(e)}")
#             continue
#
#     if not all_data:
#         raise ValueError("没有有效数据可分析")
#
#     combined = pd.concat(all_data).sort_values(['区域ID', '年份'])
#
#     # 按区域分析
#     results = {}
#
#     for region_id, group in combined.groupby('区域ID'):
#         t = group['年份'].values
#         d = group['平均深度'].values
#
#         try:
#             params, _ = curve_fit(
#                 depth_model,
#                 t, d,
#                 p0=[max(d)-min(d), 0.1, min(d)],
#                 maxfev=5000
#             )
#             alpha, gamma, beta = params
#             results[region_id] = {
#                 'alpha': alpha,
#                 'gamma': gamma,
#                 'beta': beta,
#                 'function': f"d = {alpha:.3f}·e^(-{gamma:.3f}·t) + {beta:.3f}",
#                 'last_year': max(t)
#             }
#
#             # 绘制结果
#             t_plot = np.linspace(min(t), max(t)+10, 100)  # 修改预测范围为未来十年
#             plt.figure(figsize=(10, 6), dpi=100)
#             plt.plot(t, d, 'o', markersize=8, label=f'区域{region_id}观测值 (原始数据)')
#             plt.plot(t_plot, depth_model(t_plot, *params), '--',
#                      label=f'区域{region_id}拟合曲线\n{results[region_id]["function"]}')
#
#             # 图表美化
#             plt.title(f'区域{region_id}磨损深度分析与预测', fontproperties=font_prop, fontsize=14)
#             plt.xlabel('年份', fontproperties=font_prop, fontsize=12)
#             plt.ylabel('平均深度', fontproperties=font_prop, fontsize=12)
#             plt.legend(prop=font_prop)
#             plt.grid(True, linestyle=':', alpha=0.6)
#             plt.tight_layout()
#             plt.savefig(f'region_{region_id}_analysis.png')  # 保存图像
#             plt.show()
#
#         except Exception as e:
#             print(f"区域{region_id}拟合失败: {str(e)}")
#             continue
#
#     # 打印结果报告
#     print("\n" + "="*60)
#     print(" "*20 + "磨损深度分析报告".center(20))
#     print("="*60)
#
#     for rid, data in results.items():
#         print(f"\n区域 {rid}")
#         print(f" 拟合模型: {data['function']}")
#
#         # 历史数据
#         hist_data = combined[combined['区域ID'] == rid][['年份', '平均深度']]
#         print("\n 历史数据:")
#         for _, row in hist_data.iterrows():
#             print(f"  第{int(row['年份'])}年: {row['平均深度']:.3f}")
#
#         # 未来预测
#         print("\n 未来预测:")
#         for year in range(data['last_year']+1, data['last_year']+11):  # 修改预测范围为未来十年
#             pred = depth_model(year, data['alpha'], data['gamma'], data['beta'] ,data['c'])
#             print(f"  第{year}年预测值: {pred:.3f}")
#
# # ==================== 主程序 ====================
# if __name__ == "__main__":
#     print("""
#     ████████ 磨损深度分析工具 ████████
#     """)
#
#     try:
#         analyze_uploaded_files()
#         print("\n分析完成")
#     except Exception as e:
#         print(f"\n分析失败: {str(e)}")
#         print("可能原因：")
#         print("1. 未上传Excel文件")
#         print("2. 文件格式不符合要求")
#         print("3. 文件内容与示例结构不一致")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import glob
import matplotlib.font_manager as fm
import os
import warnings

warnings.filterwarnings("ignore")  # 忽略警告信息

# ==================== 字体配置 ====================
try:
    # 尝试使用系统字体（Windows系统默认包含SimHei）
    plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
except:
    # 备用字体配置
    font_path = 'arial.ttf'  # 如果中文显示异常，请替换为本地字体路径
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()


# ==================== 分析函数 ====================
def depth_model(t, alpha, gamma, beta, c):
    """磨损深度预测模型：指数衰减 + 线性趋势 + 常数项"""
    return alpha * np.exp(-gamma * t) + beta * t + c


def analyze_files(data_dir="./data"):
    """
    执行区域磨损深度分析
    参数：
        data_dir - 包含Excel文件的目录路径（默认当前目录下的data文件夹）
    """
    # 获取所有Excel文件
    file_list = glob.glob(os.path.join(data_dir, "*.xlsx"))

    if not file_list:
        raise FileNotFoundError(f"在目录 {data_dir} 中未找到Excel文件")

    # 读取并合并数据
    all_data = []
    for file_path in file_list:
        try:
            # 从文件名提取年份（示例：2023年数据.xlsx → 2023）
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

    # 按区域分析
    results = {}
    for region_id, group in combined.groupby('区域ID'):
        t = group['年份'].values.astype(float)
        d = group['平均深度'].values.astype(float)

        try:
            # 曲线拟合（初始参数需根据实际情况调整）
            params, _ = curve_fit(
                depth_model,
                t, d,
                p0=[max(d) - min(d), 0.1, (max(d) - min(d)) / 10, min(d)],
                maxfev=5000
            )

            # 保存结果
            alpha, gamma, beta, c = params
            results[region_id] = {
                '参数': params,
                '模型公式': f"d(t) = {alpha:.2f}·e^(-{gamma:.3f}t) + {beta:.3f}t + {c:.2f}",
                '最后年份': max(t)
            }

            # 可视化
            plt.figure(figsize=(10, 6))
            t_plot = np.linspace(min(t), max(t) + 10, 100)  # 预测未来10年

            # 原始数据点
            plt.scatter(t, d, s=80, edgecolors='k',
                        label=f'区域 {region_id} 观测值', zorder=3)

            # 拟合曲线
            plt.plot(t_plot, depth_model(t_plot, *params), 'r--', lw=2,
                     label=f'拟合曲线\n{results[region_id]["模型公式"]}')

            # 图表配置
            plt.title(f'区域 {region_id} 磨损深度趋势分析', fontsize=14)
            plt.xlabel('年份', fontsize=12)
            plt.ylabel('平均深度 (mm)', fontsize=12)
            plt.legend(loc='upper left', fontsize=10)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'区域_{region_id}_分析结果.png', dpi=150, bbox_inches='tight')
            plt.close()

        except Exception as e:
            print(f"区域 {region_id} 分析失败: {str(e)}")
            continue

    # 生成报告
    print("\n" + "=" * 60)
    print(f"{' 磨损深度分析报告 ':=^60}")
    print("=" * 60)

    for rid, data in results.items():
        print(f"\n▶ 区域 {rid}")
        print(f"  数学模型: {data['模型公式']}")

        # 预测未来10年
        print("\n  未来预测:")
        for year in range(int(data['最后年份']) + 1, int(data['最后年份']) + 11):
            pred = depth_model(year, *data['参数'])
            print(f"  第{year}年: {pred:.2f} mm")


# ==================== 主程序 ====================
if __name__ == "__main__":
    print("""\n
    █████████ 工业设备磨损深度分析系统 █████████
    使用说明：
    1. 将数据文件放入项目目录下的data文件夹
    2. Excel文件命名需包含年份（如：2023年数据.xlsx）
    3. 每个文件需包含Sheet1，含[区域ID]和[平均深度]列
    """)

    analyze_files()  # 默认读取./data目录
    print("\n★ 分析完成！结果已保存至当前目录")