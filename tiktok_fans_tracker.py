import time
import csv
import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

# 配置
TIKTOK_USER_ID = "MS4wLjABAAAACdtHOv8XS_X_PTuqJ3WReO4ka7pBWg7fmzG4wjiIZVkUKFOVtbhizl9GkpdOJ-O1"
CSV_FILE = "fans_data.csv"
IMAGE_FILE = "fans_trend.png"
LOG_FILE = "error_log.txt"

def setup_driver():
    """配置浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 在GitHub Actions环境中需要明确指定二进制位置
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except WebDriverException as e:
        log_error(f"浏览器初始化失败: {str(e)}")
        return None

def log_error(message):
    """记录错误日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")
    print(message)

def get_fans_count(driver):
    """获取粉丝数量"""
    try:
        url = f"https://www.douyin.com/user/{TIKTOK_USER_ID}"
        driver.get(url)
        
        # 使用更健壮的等待策略
        wait = WebDriverWait(driver, 30)
        
        # 尝试多种定位方式
        selectors = [
            "//div[contains(@class, 'count-infos')]//span[contains(text(), '粉丝')]/../span[2]",
            "//div[contains(text(), '粉丝')]/following-sibling::div",
            "//span[contains(text(), '粉丝')]/following-sibling::span"
        ]
        
        for selector in selectors:
            try:
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                fans_text = element.text.strip()
                if fans_text:
                    break
            except (NoSuchElementException, TimeoutException):
                continue
        else:
            raise NoSuchElementException("无法定位粉丝数元素")
        
        print(f"原始粉丝文本: {fans_text}")
        
        # 处理不同格式的粉丝数
        if '万' in fans_text:
            return int(float(fans_text.replace('万', '')) * 10000)
        return int(fans_text.replace(',', ''))
        
    except Exception as e:
        log_error(f"获取粉丝数时出错: {str(e)}")
        return None

def save_to_csv(timestamp, fans_count):
    """保存数据到CSV"""
    try:
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'fans_count'])
            writer.writerow([timestamp, fans_count])
    except Exception as e:
        log_error(f"保存CSV时出错: {str(e)}")

def generate_chart():
    """生成趋势图"""
    try:
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            log_error("无有效数据可生成图表")
            return

        timestamps, fans_counts = [], []
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamps.append(datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'))
                    fans_counts.append(int(row['fans_count']))
                except ValueError as e:
                    log_error(f"解析数据行出错: {row} - {str(e)}")
                    continue

        if len(timestamps) < 2:
            log_error("数据点不足，至少需要2个点")
            return

        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, fans_counts, 'bo-', markersize=6, linewidth=2)
        plt.title('抖音粉丝趋势')
        plt.xlabel('时间')
        plt.ylabel('粉丝数')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(IMAGE_FILE, dpi=300, bbox_inches='tight')
        plt.close()
        print("图表生成成功")
        
    except Exception as e:
        log_error(f"生成图表时出错: {str(e)}")

def main():
    """主流程"""
    driver = setup_driver()
    if not driver:
        sys.exit(1)
        
    try:
        for attempt in range(3):
            print(f"尝试第 {attempt + 1} 次...")
            fans_count = get_fans_count(driver)
            if fans_count is not None:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"成功获取: {timestamp} - {fans_count} 粉丝")
                save_to_csv(timestamp, fans_count)
                generate_chart()
                break
            time.sleep(5)
        else:
            log_error("3次尝试后仍失败")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()