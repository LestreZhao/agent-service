# Oracle客户端安装指南

## macOS安装Oracle Instant Client

### 方法1：使用Homebrew（推荐）

```bash
# 安装Oracle Instant Client
brew install instantclient-basic
brew install instantclient-sqlplus

# 设置环境变量（添加到 ~/.zshrc 或 ~/.bash_profile）
export ORACLE_HOME=/opt/homebrew/lib/instantclient
export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH
export PATH=$ORACLE_HOME:$PATH
```

### 方法2：手动下载安装

1. 访问Oracle官网下载页面：
   https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html

2. 下载以下文件：
   - `instantclient-basic-macos.x64-21.12.0.0.0dbru.zip`
   - `instantclient-sqlplus-macos.x64-21.12.0.0.0dbru.zip`

3. 解压到 `/opt/oracle/instantclient_21_12/`

4. 设置环境变量：
```bash
export ORACLE_HOME=/opt/oracle/instantclient_21_12
export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH
export PATH=$ORACLE_HOME:$PATH
```

### 验证安装

```bash
# 检查库文件
ls -la $ORACLE_HOME/libclntsh.dylib

# 测试连接（需要配置数据库连接信息）
python3 -c "import cx_Oracle; print('Oracle client installed successfully')"
```

## 环境变量配置

将以下内容添加到 `~/.zshrc` 文件：

```bash
# Oracle Instant Client
export ORACLE_HOME=/opt/homebrew/lib/instantclient  # 或实际安装路径
export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH
export PATH=$ORACLE_HOME:$PATH
```

然后重新加载：
```bash
source ~/.zshrc
```

## 数据库连接配置

创建 `.env` 文件：
```bash
ORACLE_HOST=your_oracle_host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your_service_name
ORACLE_USERNAME=your_username
ORACLE_PASSWORD=your_password
```

## 故障排除

### 常见问题

1. **libclntsh.dylib找不到**
   - 确认Oracle Instant Client已正确安装
   - 检查DYLD_LIBRARY_PATH环境变量
   - 重启终端或重新加载环境变量

2. **权限问题**
   ```bash
   sudo chown -R $(whoami) /opt/oracle/
   chmod +x /opt/oracle/instantclient_*/
   ```

3. **版本兼容性**
   - 确保下载的是适合您系统架构的版本（Intel x64 或 Apple Silicon）
   - cx_Oracle版本与Oracle客户端版本兼容

### 测试连接

```python
import os
import cx_Oracle

# 检查环境变量
print("ORACLE_HOME:", os.getenv('ORACLE_HOME'))
print("DYLD_LIBRARY_PATH:", os.getenv('DYLD_LIBRARY_PATH'))

# 测试基本功能
try:
    # 这会测试cx_Oracle是否能找到客户端库
    print("Oracle client version:", cx_Oracle.clientversion())
    print("✅ Oracle客户端安装成功")
except Exception as e:
    print(f"❌ Oracle客户端问题: {e}")
``` 