# 抖音主播粉丝数跟踪工具

这个项目使用GitHub Actions定时获取指定抖音主播的粉丝数量，并生成粉丝增长趋势图。

## 功能特点

- 自动定时获取抖音主播粉丝数
- 将数据存储在CSV文件中
- 生成粉丝增长趋势图
- 完全自动化运行，无需人工干预

## 使用方法

1. Fork本仓库
2. 编辑`tiktok_fans_tracker.py`文件，将`TIKTOK_USER_ID`替换为目标主播的ID
3. 启用GitHub Actions（在仓库的Actions标签页中）
4. 系统会自动按预定时间运行，并更新数据和图表

## 数据展示

旺仔小乔最新粉丝数趋势图：

![粉丝趋势图](fans_trend.png)

## 定时设置

每天执行一次，可以在`.github/workflows/tiktok-fans-tracker.yml`文件中修改定时设置。
