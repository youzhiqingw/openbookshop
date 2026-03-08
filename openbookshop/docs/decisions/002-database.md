# 决策记录: 数据库选型

## 背景
需要支持开发便捷性和生产环境可扩展性

## 决策
开发使用 SQLite，生产环境兼容 MySQL

## 理由

- **开发便捷**: SQLite 无需安装，适合本地开发
- **演示简单**: 答辩时只需复制一个文件即可迁移环境
- **生产兼容**: Django ORM 抽象层保证代码兼容 MySQL

## 实施细节

- 使用 settings_dev.py (SQLite) 和 settings_prod.py (MySQL)
- 避免使用数据库特定 SQL
- 定期在 MySQL 环境测试

## 日期
2024-01-16