from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_first_proxy_from_page():
    # 设置Chrome选项（不指定binary_location）
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

    # 初始化WebDriver（依赖系统默认的默认安装路径）

    driver = webdriver.Chrome(options=chrome_options)
    try:
        url = "https://proxy.scdn.io/?type=http&country=%E4%B8%AD%E5%9B%BD&page=1&per_page=10"
        driver.get(url)
        
        # 延长等待时间，确保动态内容加载完成
        wait = WebDriverWait(driver, 15)  # 最长等待15秒
        
        # 等待"加载中..."消失
        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, "//td[contains(text(), '加载中...')]")
        ))
        
        # 等待表格数据加载完成
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#proxyTableBody tr:not([colspan])")  # 排除colspan的加载行
        ))
        
        # 获取表格主体
        proxy_table = driver.find_element(By.ID, "proxyTableBody")
        if not proxy_table:
            print("未找到id为proxyTableBody的表格")
            return None
        
        # 获取第一行有效数据
        first_tr = proxy_table.find_element(By.TAG_NAME, "tr")
        if not first_tr:
            print("表格中无任何代理行数据")
            return None
        
        # 提取IP和端口
        tds = first_tr.find_elements(By.TAG_NAME, "td")
        if len(tds) >= 2:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            
            if "." in ip and port.isdigit():
                proxy_url = f"http://{ip}:{port}"
                print(f"提取到代理：{proxy_url}")
                return proxy_url
            else:
                print(f"IP或端口格式异常：IP={ip}，端口={port}")
                return None
        else:
            print(f"有效td数量不足，当前数量：{len(tds)}")
            return None
            
    except Exception as e:
        print(f"获取代理失败：{str(e)}")
        return None
    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    get_first_proxy_from_page()
    