# 抖音主播粉丝数跟踪工具

这是一个自动化获取抖音主播粉丝数量的工具，支持定时任务、数据存储和趋势可视化。

## 功能特点

- 自动定时获取抖音主播粉丝数
- 数据持久化存储（CSV格式）
- 生成粉丝增长趋势图
- 支持代理服务器访问
- 灵活的部署方式（GitHub Actions / 本地 / NAS Docker）

## 快速开始

### 方式一：GitHub Actions（推荐）

1. Fork本仓库
2. 编辑 `tiktok_fans_tracker.py`，修改 `TIKTOK_USER_ID` 为目标主播的抖音用户ID
3. 启用GitHub Actions（仓库 → Actions → I understand my workflows）
4. 系统每天自动执行并更新数据

### 方式二：本地运行

```bash
# 安装依赖
pip install selenium pandas matplotlib

# 运行（无代理）
python tiktok_fans_tracker.py

# 运行（带代理）
python tiktok_fans_tracker.py --proxy=http://ip:port
```

### 方式三：NAS Docker 部署

在群晖（Synology）或其它 NAS 上运行 Docker 容器。

#### 前置准备

1. **开启SSH服务**：控制面板 → 终端机和SNMP → 启用SSH
2. **安装Docker**：套件中心 → 安装 Docker 套件
3. **下载Chrome浏览器镜像**：
   ```bash
   ssh user@your-nas-ip
   docker pull browserless/chrome
   ```

#### 创建容器

```bash
# 创建数据目录（用于持久化存储数据）
mkdir -p /volume1/docker/tiktok-tracker/data

# 构建并运行容器
docker run -d \
  --name tiktok-tracker \
  --restart=always \
  -v /volume1/docker/tiktok-tracker/data:/app/data \
  -e TIKTOK_USER_ID="你的抖音用户ID" \
  -e PROXY="" \
  -p 8080:8080 \
  browserless/chrome \
  --timeout=60000
```

#### 使用定时任务（推荐）

为避免容器长期运行，建议使用宿主机的 cron 定时任务：

```bash
# 编辑定时任务
crontab -e

# 添加定时任务（每天凌晨2点执行）
0 2 * * * docker exec tiktok-tracker python /app/tiktok_fans_tracker.py --proxy=$PROXY >> /volume1/docker/tiktok-tracker/data/tracker.log 2>&1
```

#### 数据目录说明

```
/volume1/docker/tiktok-tracker/data/
├── fans_data.csv      # 粉丝数据
├── fans_trend.png     # 趋势图
└── tracker.log        # 运行日志
```

### 配置说明

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `TIKTOK_USER_ID` | 抖音用户ID（从用户主页URL获取） | `MS4wLjABAAA...` |
| `PROXY` | 代理服务器地址（可选） | `http://ip:port` |

### 获取抖音用户ID

1. 打开抖音网页版（www.douyin.com）
2. 进入目标主播主页
3. 复制浏览器地址栏中的用户ID（通常在 `/user/` 后面的长字符串）

## 项目结构

```
├── tiktok_fans_tracker.py    # 主程序
├── get_proxy.py              # 代理获取脚本
├── fans_data.csv             # 粉丝数据存储
├── fans_trend.png            # 趋势图
├── .github/workflows/        # GitHub Actions 配置
│   └── tiktok-fans-tracker.yml
└── README.md
```

## 定时设置（GitHub Actions）

在 `.github/workflows/tiktok-fans-tracker.yml` 中修改 cron 表达式：

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 每天凌晨0点执行
```

## 数据展示

工具会自动生成粉丝增长趋势图和数据表格，支持部署到 GitHub Pages 展示。

## 注意事项

- 抖音页面结构可能会更新，如果获取失败请检查 XPath 选择器
- 建议使用代理避免 IP 被封禁
- 首次运行会自动创建数据文件
