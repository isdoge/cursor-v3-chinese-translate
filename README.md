# Cursor V3 Chinese Translate

> Cursor V3 中文增强翻译脚本。通过注入前端翻译脚本，并按需补丁少量 Electron 原生菜单资源，补全 Cursor 自定义 UI、设置页、插件页、MCP、欢迎页和输入框右键菜单等官方 VS Code 中文语言包覆盖不到的英文内容。

## 主要特性

- **增强 Cursor UI 汉化**：覆盖设置页、插件页、MCP、Agent、Composer、欢迎页、动态状态文本等 Cursor 自定义界面。
- **轻量 DOM 翻译**：翻译文本节点以及 `title`、`aria-label`、`placeholder`、`aria-placeholder`、`aria-description` 等属性，监听后加载内容。
- **性能保护**：动态翻译队列去重、分帧处理，队列过大时合并为兜底重扫，减少卡顿和漏翻。
- **高风险区域跳过**：默认跳过编辑器、终端、webview、iframe 等区域，避免影响代码编辑、终端输出和嵌入内容。
- **不替换官方语言包**：不覆盖 VS Code 官方中文语言包，只补充 Cursor 自定义 UI 中未覆盖的英文内容。
- **少量原生菜单汉化**：对白名单内 Electron 原生菜单、输入框右键菜单、托盘菜单词条进行资源替换，例如 `Undo`、`Redo`、`Cut`、`Paste`、`Select All`。
- **可恢复**：自动备份并恢复 `workbench.html`、`product.json`，以及存在且需要更新时的 `out/main.js`、`out/nls.messages.json`。

## 环境要求

- Python 3
- 本地已安装 Cursor
- 对 Cursor 安装目录具有写入权限

项目仅使用 Python 标准库，不依赖第三方 Python 包。

## 快速使用

> 运行 `--apply` 或 `--restore` 前，请先完全关闭 Cursor。原生菜单资源修改后必须完整重启 Cursor 才会生效。

应用汉化：

```bash
python CursorTranslate.py --apply
```

恢复原始文件并清理本工具生成的备份：

```bash
python CursorTranslate.py --restore
```

保留备份文件：

```bash
python CursorTranslate.py --restore --keep-backups
```

指定 Cursor 安装目录：

```bash
python CursorTranslate.py --apply --cursorDir="D:\Tools\cursor"
python3 CursorTranslate.py --apply --cursorDir="/Applications/Cursor.app"
python3 CursorTranslate.py --apply --cursorDir="/Applications/Cursor.app/Contents/Resources/app"
```

查看帮助：

```bash
python CursorTranslate.py --help
```

## 默认路径

### Cursor 安装目录

- Windows 用户级安装：`%LocalAppData%\Programs\cursor`
- Windows 系统级安装：`C:\Program Files\cursor`
- macOS：`/Applications/Cursor.app` 或 `~/Applications/Cursor.app`
- Linux：`/usr/share/cursor`、`/opt/Cursor`、`/opt/cursor`

`--cursorDir` 可以指向 Cursor 安装根目录，也可以直接指向 `resources/app`；macOS 下也支持指向 `Cursor.app`、`Cursor.app/Contents` 或 `Cursor.app/Contents/Resources/app`。

## 翻译词典

默认词典文件：

```text
cursor_translate_dic.txt
```

词典每行使用 `=>` 分隔原文和译文：

```text
"Settings" => "设置"
"Open project" => "打开项目"
"Prevent \"Connection failed\" errors" => "防止出现“Connection failed”错误"
```

以下内容会被忽略：

- 空行
- 以 `#` 开头的行
- 以 `//` 开头的行

当前词典主要覆盖：

- Cursor 设置页、欢迎页、顶部栏和常见菜单
- Agent / Composer / Chat 动态状态和工具调用时间线
- 插件 Marketplace、MCP、索引、网络、钩子、自动运行相关设置
- 少量 Electron 原生菜单、输入框右键菜单、托盘菜单白名单词条

如果仍有英文，截图后把准确原文补进 `cursor_translate_dic.txt`，再重新执行 `--apply` 并重启 Cursor。

## 词条候选提取

从 Cursor 打包源码中提取可能需要翻译的候选文案：

```bash
python CursorTranslate.py --extract-source-strings --limit=200
```

该命令只打印候选结果，不修改词典，也不写入 Cursor 安装目录。不要把结果全量加入词典；源码里会包含内部状态、错误码、命令 ID、快捷键、模型名和服务名。只补确认会显示在 Cursor 自定义 UI 中的文案。

## 旧版本清理

清理早期版本可能写入的 `languagepacks.json`、`cursor-local-zh-cn` 和相关缓存：

```bash
python CursorTranslate.py --cleanup-legacy
```

该命令会检查文件标记，只清理确认由本工具创建的文件。

## 修改范围

应用时可能修改以下 Cursor 安装目录文件：

- `out/vs/code/electron-sandbox/workbench/workbench.html`
- `product.json`
- `out/main.js`（存在且有匹配词条时，仅替换白名单内原生菜单字符串）
- `out/nls.messages.json`（存在且有匹配词条时，仅替换白名单内原生菜单字符串）

恢复时默认删除当前备份和历史轮转备份，例如：

- `workbench.html.bak`
- `product.json.bak`
- `main.js.bak`
- `nls.messages.json.bak`
- `workbench.html.bak.20260531123456`

如需保留备份，请使用 `--restore --keep-backups`。

## 常见问题

### 仍有部分英文没有翻译

常见原因：Cursor 新版本增加了文案、原文与词典不完全一致、文本被拆成多个 DOM 节点、或属于未加入白名单的原生菜单项。

处理方式：补充准确原文到 `cursor_translate_dic.txt`，重新执行 `--apply` 并完整重启 Cursor。不要把 VS Code 内置设置项大面积加入词典。

### 输入框右键菜单仍是英文

输入框右键菜单属于 Electron/Chromium 原生菜单，不在 DOM 中。当前脚本只处理白名单内少量高频原生菜单词条。

如果未生效，请确认：

1. 已完全关闭 Cursor 后执行 `--apply`
2. 执行过程中没有权限错误
3. 已完整重启 Cursor，而不是只刷新窗口
4. 当前 Cursor 版本的原生资源中存在对应英文词条

### Cursor 更新后汉化失效

Cursor 更新可能覆盖 `workbench.html` 或原生菜单资源，重新执行：

```bash
python CursorTranslate.py --apply
```

### Cursor 提示安装损坏

脚本会更新 `product.json` 校验值。若之前手动修改过文件，可尝试：

```bash
python CursorTranslate.py --restore
python CursorTranslate.py --apply
```

### 找不到 `workbench.html`

使用 `--cursorDir` 指定实际安装目录，或直接指定 `resources/app` 目录。

## 安全说明

- 脚本不读取 Cursor 登录信息、本地 token 或本地数据库。
- 脚本不访问网络，也不会上传本地文件。
- 修改安装目录前会自动备份关键文件。
- 原生资源只替换白名单内菜单字符串，不对打包资源做全量翻译。
- 编辑器、终端、webview、iframe 等高风险区域默认跳过，避免影响代码和嵌入内容。

该项目会修改 Cursor 安装目录内文件，请自行评估风险，并建议保留备份。
