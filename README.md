# Claude Code 状态指示灯

一个用于可视化显示 Claude Code CLI 工作状态的四色悬浮指示灯。

![状态灯演示](https://img.shields.io/badge/状态-运行中-brightgreen)

## 🎨 功能特性

- **四色状态显示**
  - 🟢 **绿色** - 完成 (done)
  - 🟣 **紫色** - 思考中 (thinking)
  - 🟠 **橙色** - 工作中 (working)
  - 🔴 **红色** - 错误 (error)

- **悬浮窗口设计** - 置顶显示，可拖动位置
- **HTTP API 控制** - 接收 Claude Code CLI 的状态推送
- **右键菜单** - 手动切换状态

## 📁 文件说明

```
指示灯.pyw          # 原版本（存在线程安全问题）
指示灯_fixed.pyw    # 修复版本（推荐）
```

## 🚀 快速开始

### 1. 启动指示灯程序

```bash
# 使用修复版本（推荐）
python 指示灯_fixed.pyw
```

程序启动后会：
- 在屏幕右上角显示一个圆形状态灯
- 启动 HTTP 服务器监听端口 `8765`
- 默认显示绿色（完成状态）

### 2. 配置 Claude Code CLI

创建或编辑 Claude Code CLI 的配置文件：

**Windows:**
```powershell
notepad %USERPROFILE%\.claude\settings.json
```

**macOS/Linux:**
```bash
mkdir -p ~/.claude
vim ~/.claude/settings.json
```

### 3. 添加 Hooks 配置

将以下内容添加到 `settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "curl -X POST http://127.0.0.1:8765 -H \"Content-Type: application/json\" -d \"{\\\"event\\\":\\\"UserPromptSubmit\\\"}\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "curl -X POST http://127.0.0.1:8765 -H \"Content-Type: application/json\" -d \"{\\\"event\\\":\\\"PreToolUse\\\"}\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "curl -X POST http://127.0.0.1:8765 -H \"Content-Type: application/json\" -d \"{\\\"event\\\":\\\"Stop\\\"}\""
          }
        ]
      }
    ]
  }
}
```

**Windows PowerShell 版本：**

```json
{
    "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"Invoke-RestMethod -Uri http://127.0.0.1:8765 -Method POST -ContentType 'application/json' -Body '{\\\"event\\\":\\\"UserPromptSubmit\\\"}'\""
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"Invoke-RestMethod -Uri http://127.0.0.1:8765 -Method POST -ContentType 'application/json' -Body '{\\\"event\\\":\\\"PreToolUse\\\"}'\""
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"Invoke-RestMethod -Uri http://127.0.0.1:8765 -Method POST -ContentType 'application/json' -Body '{\\\"event\\\":\\\"AwaitingUserConfirmation\\\"}'\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"Invoke-RestMethod -Uri http://127.0.0.1:8765 -Method POST -ContentType 'application/json' -Body '{\\\"event\\\":\\\"PreToolUse\\\"}'\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"Invoke-RestMethod -Uri http://127.0.0.1:8765 -Method POST -ContentType 'application/json' -Body '{\\\"event\\\":\\\"Stop\\\"}'\""
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"Invoke-RestMethod -Uri http://127.0.0.1:8765 -Method POST -ContentType 'application/json' -Body '{\\\"event\\\":\\\"Notification\\\"}'\""
          }
        ]
      }
    ]
  
}
}
```

## 🔌 HTTP API

指示灯程序提供简单的 HTTP API 用于状态控制：

### POST / - 设置状态

**请求格式 1 - Claude Code 事件：**
```bash
curl -X POST http://127.0.0.1:8765 \
  -H "Content-Type: application/json" \
  -d '{"event":"UserPromptSubmit"}'
```

支持的事件：
| 事件 | 状态 | 颜色 |
|------|------|------|
| `UserPromptSubmit` | thinking | 🟣 紫色 |
| `PreToolUse` | working | 🟠 橙色 |
| `Stop` | done | 🟢 绿色 |
| `Notification` | error | 🔴 红色 |

**请求格式 2 - 直接设置状态：**
```bash
curl -X POST http://127.0.0.1:8765 \
  -H "Content-Type: application/json" \
  -d '{"status":"working"}'
```

支持的状态值：`done`, `thinking`, `working`, `error`

### GET / - 查询当前状态

```bash
curl http://127.0.0.1:8765
```

返回：
```json
{"status": "working"}
```

## 🖱️ 操作说明

| 操作 | 功能 |
|------|------|
| **左键拖动** | 移动指示灯位置 |
| **右键点击** | 打开状态切换菜单 |
| **关闭窗口** | 退出程序 |

## ⚙️ 配置参数

在代码中可以修改以下参数：

```python
PORT = 8765           # HTTP 服务器端口
WIN_SIZE = 68         # 指示灯大小（像素）
ALPHA = 1.0           # 窗口透明度
```

颜色配置：
```python
COLOR_MAP = {
    "done": "#2E8B57",      # 绿色
    "thinking": "#9370DB",  # 紫色
    "working": "#FF8C00",   # 橙色
    "error": "#DC143C"      # 红色
}
```

## 🐛 故障排除

### 指示灯不变色

1. **检查程序是否运行** - 确认指示灯窗口可见
2. **检查端口占用** - 确保端口 8765 未被占用
3. **检查 Claude Code 配置** - 确认 settings.json 格式正确
4. **查看控制台输出** - 修复版本会打印状态变更日志

### 端口被占用

修改 `指示灯_fixed.pyw` 中的 `PORT` 变量，同时更新 Claude Code 配置中的端口。

### Claude Code CLI 未触发 Hooks

1. 确认 Claude Code CLI 版本支持 Hooks 功能
2. 检查 settings.json 文件路径是否正确
3. 重启 Claude Code CLI 使配置生效

## 📝 更新日志

### 修复版本 (指示灯_fixed.pyw)

- ✅ 修复线程安全问题 - 使用队列进行线程间通信
- ✅ 添加状态变更日志输出
- ✅ 优化 UI 更新机制

### 原版本 (指示灯.pyw)

- ⚠️ 存在线程安全问题 - HTTP 线程直接操作 Tkinter UI

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
