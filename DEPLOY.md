# 社区医院门诊管理系统 - 部署指南

## 快速开始（10分钟部署）

### 第一步：安装MySQL（如果未安装）

#### Windows系统
1. 下载MySQL安装包：https://dev.mysql.com/downloads/mysql/
2. 运行安装程序，选择"Developer Default"
3. 设置root密码（记住这个密码！）
4. 完成安装并启动MySQL服务

#### 验证MySQL安装
打开命令行，运行：
```bash
mysql --version
```

### 第二步：安装Python依赖

打开PowerShell，进入项目目录：

```powershell
cd "C:\Users\lihua\Desktop\数据库大作业实验\hospital_system"

# 安装依赖
pip install -r requirements.txt
```

如果下载速度慢，可使用国内镜像：
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第三步：创建数据库

#### 方法1: 使用命令行（推荐）

```powershell
# 登录MySQL
mysql -u root -p
# 输入你设置的密码

# 在MySQL中执行
source database/schema.sql;
exit;
```

#### 方法2: 使用MySQL Workbench
1. 打开MySQL Workbench
2. 连接到本地数据库
3. 打开 `database/schema.sql` 文件
4. 点击执行（⚡图标）

### 第四步：配置数据库连接

编辑 `app.py` 文件的第18-24行：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # 你的MySQL用户名
    'password': '你的密码',    # 你的MySQL密码
    'database': 'hospital_management',
    'charset': 'utf8mb4'
}
```

### 第五步：启动应用

```powershell
python app.py
```

看到以下信息表示成功：
```
 * Running on http://127.0.0.1:5000
 * Running on http://你的IP:5000
```

### 第六步：访问系统

打开浏览器，访问：
```
http://localhost:5000
```

## 功能测试指南

### 测试流程1：患者预约到就诊完整流程

#### 1. 患者预约（5分钟）
- 访问首页，点击"患者服务"
- 填写信息：
  - 姓名：张三
  - 电话：13800138000
  - 科室：选择"内科"
  - 日期：选择今天或明天
  - 时间：09:00
- 提交预约，记录预约编号

#### 2. 前台登记（3分钟）
- 返回首页，点击"前台系统"
- 切换到"患者登记"标签
- 填写信息：
  - 姓名：张三
  - 电话：13800138000
  - 性别：男
  - 科室：内科
  - 诊室：选择任一诊室
  - 预约编号：填写刚才的编号
- 提交登记

#### 3. 查看就诊（2分钟）
- 切换到"就诊管理"标签
- 查看患者张三的就诊记录

#### 4. 费用结算（3分钟）
- 切换到"费用结算"标签
- 输入刚才的就诊编号
- 点击"加载就诊信息"
- 填写费用：
  - 总费用：200
  - 医保支付：120
  - 支付方式：医保卡
- 点击"确认收费"

### 测试流程2：管理员数据查询

#### 1. 收入统计（3分钟）
- 返回首页，点击"管理后台"
- 切换到"收入统计"标签
- 选择日期范围和统计类型
- 查看统计结果

#### 2. 患者查询（2分钟）
- 切换到"患者查询"标签
- 输入"张三"或手机号
- 查看患者详细信息

#### 3. 排班管理（5分钟）
- 切换到"排班管理"标签
- 创建新排班：
  - 医生：选择"张医生"
  - 诊室：内科1诊室
  - 日期：明天
  - 时间：08:00 - 12:00
- 提交并查看排班列表

## 录制功能演示视频

### 推荐工具
- **Windows**: 使用OBS Studio（免费）或系统自带的Xbox Game Bar（Win+G）
- **屏幕录制**: Bandicam、Camtasia

### 演示脚本（建议5-10分钟）

#### 开场（30秒）
- 展示系统首页
- 介绍三个模块

#### 患者功能演示（2分钟）
- 在线预约流程
- 预约查询功能

#### 前台功能演示（3分钟）
- 患者登记
- 就诊管理
- 费用结算

#### 管理功能演示（3分钟）
- 数据统计
- 患者查询
- 排班管理

#### 收尾（30秒）
- 总结核心功能
- 展示数据库表结构（可选）

## 常见问题解决

### 问题1: `pip install` 失败

**解决方案**：
```powershell
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: MySQL连接报错

**可能原因**：
1. MySQL服务未启动
2. 用户名密码错误
3. 数据库未创建

**解决方案**：
```powershell
# 检查MySQL服务状态
Get-Service MySQL*

# 如果未运行，启动服务
Start-Service MySQL80  # 服务名可能不同

# 重新创建数据库
mysql -u root -p < database\schema.sql
```

### 问题3: 端口5000被占用

**解决方案**：
修改 `app.py` 最后一行：
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # 改为8080或其他端口
```

### 问题4: 页面样式显示异常

**解决方案**：
- 清除浏览器缓存（Ctrl+Shift+Delete）
- 使用Chrome或Edge浏览器
- 检查是否正确访问 http://localhost:5000

### 问题5: 中文乱码

**解决方案**：
确保MySQL字符集正确：
```sql
ALTER DATABASE hospital_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 上传到GitHub

### 1. 创建GitHub仓库

1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 输入仓库名：hospital-management-system
4. 选择 Public
5. 点击 "Create repository"

### 2. 初始化Git并推送

```powershell
cd "C:\Users\lihua\Desktop\数据库大作业实验\hospital_system"

# 初始化Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Hospital Management System"

# 关联远程仓库（替换为你的GitHub用户名）
git remote add origin https://github.com/你的用户名/hospital-management-system.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 3. 添加.gitignore文件

创建 `.gitignore` 文件，排除敏感信息：
```
__pycache__/
*.pyc
*.pyo
.env
.vscode/
*.log
```

## 生成可执行文件（可选）

如果需要打包成独立程序：

```powershell
# 安装PyInstaller
pip install pyinstaller

# 打包应用
pyinstaller --onefile --add-data "templates;templates" --add-data "database;database" app.py
```

生成的exe文件在 `dist` 目录中。

## 云端部署（可选）

### 部署到Heroku
1. 注册Heroku账号
2. 安装Heroku CLI
3. 创建 `Procfile` 文件：
```
web: python app.py
```

### 部署到阿里云/腾讯云
参考各平台的Python Web应用部署文档。

## 技术支持

如遇到其他问题：
1. 查看控制台错误信息
2. 检查MySQL日志
3. 参考Flask官方文档

---

**祝您部署顺利！**
