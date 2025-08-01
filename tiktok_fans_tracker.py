import time
import csv
import os
import argparse  # 新增：用于解析命令行参数
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import font_manager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置目标主播ID（替换为你要监测的主播ID）
TIKTOK_USER_ID = "MS4wLjABAAAACdtHOv8XS_X_PTuqJ3WReO4ka7pBWg7fmzG4wjiIZVkUKFOVtbhizl9GkpdOJ-O1"
CSV_FILE = "fans_data.csv"  # 数据存储文件
IMAGE_FILE = "fans_trend.png"  # 图表存储文件


def get_fans_count(proxy=None):  # 新增：接收proxy参数
    """获取抖音主播的粉丝数量（支持代理）"""
    print(f"开始获取抖音主播 {TIKTOK_USER_ID} 的粉丝数...")
    print(f"使用代理: {proxy if proxy else '无'}")  # 打印代理状态

    chrome_options = Options()
    # 新增：配置代理（如果有代理参数）
    if proxy:
        chrome_options.add_argument(f"--proxy-server=http://100.108.141.117:3128")
    chrome_options.add_argument('--proxy-bypass-list=localhost;127.0.0.1;::1')

    # 原有浏览器配置
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)

    try:
        url = f"https://www.douyin.com/user/{TIKTOK_USER_ID}"
        print(f"访问地址: {url}")
        driver.get(url)

        print("等待页面初步加载...")
        time.sleep(5)

        print("尝试滚动页面加载更多内容")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        print("开始查找粉丝数元素...")
        wait = WebDriverWait(driver, 40)
        fans_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '粉丝')]/following-sibling::div"))
        )

        print("粉丝数元素已找到，提取文本...")
        fans_text = fans_element.text.strip()
        print(f"获取到粉丝数文本: {fans_text}")

        # 处理粉丝数格式（万/普通数字）
        if '万' in fans_text:
            fans_count = int(float(fans_text.replace('万', '')) * 10000)
        else:
            fans_count = int(fans_text)

        return fans_count

    except Exception as e:
        print(f"获取粉丝数失败: {str(e)}")

        # 调试信息保存
        try:
            print("保存截图 debug_screenshot.png...")
            driver.save_screenshot("debug_screenshot.png")
        except Exception as se:
            print(f"保存截图失败: {str(se)}")

        try:
            print("保存 HTML 到 debug_page.html...")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception as he:
            print(f"保存 HTML 失败: {str(he)}")

        return None

    finally:
        driver.quit()
        print("已关闭浏览器")


def save_to_csv(timestamp, fans_count):
    """将粉丝数据保存到CSV文件"""
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'fans_count'])
        writer.writerow([timestamp, fans_count])


def generate_chart():
    """生成粉丝数量趋势图表"""
    timestamps = []
    fans_counts = []
    
    try:
        if not os.path.exists(CSV_FILE):
            print("数据文件不存在，无法生成图表")
            return
            
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamps.append(datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'))
                fans_counts.append(int(row['fans_count']))
        
        if not timestamps:
            print("没有数据生成图表")
            return
            
        # 配置中文字体
        plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial Unicode MS"]
        plt.rcParams["axes.unicode_minus"] = False
        
        # 生成粉丝趋势图
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, fans_counts, 'bo-', markersize=6, linewidth=2)
        plt.title('抖音主播粉丝数变化趋势')
        plt.xlabel('时间')
        plt.ylabel('粉丝数量')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(IMAGE_FILE, dpi=300)
        plt.close()
        print(f"图表已保存至 {IMAGE_FILE}")
        
    except Exception as e:
        print(f"生成图表失败: {str(e)}")


def main():
    """主函数：解析参数并协调流程"""
    # 新增：解析命令行参数（接收代理）
    parser = argparse.ArgumentParser(description='抖音粉丝数跟踪工具（支持代理）')
    parser.add_argument('--proxy', type=str, help='代理服务器地址（格式：http://ip:port）')
    args = parser.parse_args()

    # 传递代理参数给获取粉丝数的函数
    fans_count = get_fans_count(proxy=args.proxy)
    if fans_count is not None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - 当前粉丝数: {fans_count}")
        save_to_csv(timestamp, fans_count)
        generate_chart()
    else:
        print("未能获取粉丝数，不更新数据")


if __name__ == "__main__":
    main()