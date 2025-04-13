# Simple RAG Service

这是一个简单的基于 RAG (Retrieval-Augmented Generation) 的文档检索服务。

## 项目结构

```
kbs/
├── app/            # Web应用相关代码
├── core/           # 核心业务逻辑
├── models/         # 数据模型
├── services/       # 服务层代码
└── app.py         # 应用入口

```

## 功能特性

- 支持上传 PDF、DOCX 和 TXT 文档
- 自动文档分段和向量化
- 基于语义相似度的文档检索
- RESTful API 接口
- 支持多种数据库（PostgreSQL、MySQL、SQLite）
- 文件自动去重和版本管理

## 配置说明

### 数据库配置

系统支持三种数据库：

1. SQLite（默认）
```bash
KBS_DB_TYPE=sqlite
KBS_DB_PATH=sbk.db
```

2. PostgreSQL
```bash
KBS_DB_TYPE=postgresql
KBS_DB_HOST=localhost
KBS_DB_PORT=5432
KBS_DB_USER=postgres
KBS_DB_PASSWORD=your_password
KBS_DB_NAME=kbs
```

3. MySQL
```bash
KBS_DB_TYPE=mysql
KBS_DB_HOST=localhost
KBS_DB_PORT=3306
KBS_DB_USER=root
KBS_DB_PASSWORD=your_password
KBS_DB_NAME=kbs
```

### 文件存储配置

```bash
# 文件存储路径
KBS_STORAGE_PATH=~/.kbs/files
# 最大文件大小（字节）
KBS_MAX_FILE_SIZE=104857600  # 100MB
# 允许的文件类型
KBS_ALLOWED_EXTENSIONS=pdf,txt,doc,docx
```

## 安装

1. 克隆项目

```bash
git clone <repository-url>
cd kbs
```

2. 创建并激活虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 安装项目

```bash
pip install -e .
```

4. 配置环境变量

复制 `.env.example` 文件为 `.env` 并根据需要修改配置：
```bash
cp .env.example .env
```

5. 启动数据库（根据选择的数据库类型）

使用 SQLite（默认）:
不需要额外配置

使用 PostgreSQL:
```bash
docker-compose up -d postgres
```

使用 MySQL:
```bash
docker-compose up -d mysql
```

6. 启动 Milvus:

```bash
docker-compose up -d milvus
```

7. 运行应用

```bash
python app.py
```

## 文件存储说明

系统会自动对上传的文件进行以下处理：

1. 计算文件的 SHA-256 哈希值
2. 使用日期和哈希值组织存储目录结构
3. 自动去重（相同哈希值的文件只会存储一次）
4. 在切片元数据中保存原始文件信息，包括：
   - 文件哈希值
   - 原始文件名
   - 存储路径
   - 上传时间
   - 文件大小