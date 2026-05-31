# -*- coding: utf-8 -*-
"""
Smoke test for CursorTranslate.py
Creates a fake Cursor installation and tests apply/restore workflow
"""

import os
import sys
import tempfile
import shutil
import json
import subprocess

def create_fake_cursor_installation(base_dir):
    """创建假的 Cursor 安装目录结构"""
    # 创建目录结构
    resources_app = os.path.join(base_dir, "resources", "app")
    workbench_dir = os.path.join(resources_app, "out", "vs", "code", "electron-sandbox", "workbench")
    os.makedirs(workbench_dir, exist_ok=True)

    # 创建 product.json
    product_json_path = os.path.join(resources_app, "product.json")
    product_data = {
        "name": "Cursor",
        "version": "0.0.1",
        "checksums": {
            "vs/code/electron-sandbox/workbench/workbench.html": "dGVzdGNoZWNrc3Vt"
        }
    }
    with open(product_json_path, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, indent=2)

    # 创建 workbench.html
    workbench_html_path = os.path.join(workbench_dir, "workbench.html")
    workbench_html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Cursor</title>
</head>
<body>
    <div id="workbench"></div>
</body>
</html>"""
    with open(workbench_html_path, 'w', encoding='utf-8') as f:
        f.write(workbench_html_content)

    return base_dir, product_json_path, workbench_html_path

def run_smoke_test():
    """运行 smoke test"""
    print("=" * 60)
    print("  Smoke Test for CursorTranslate.py")
    print("=" * 60)

    # 创建临时目录
    test_dir = tempfile.mkdtemp(prefix="cursor_test_")
    print(f"\n[测试] 创建临时目录: {test_dir}")

    try:
        # 创建假的 Cursor 安装
        cursor_dir, product_json_path, workbench_html_path = create_fake_cursor_installation(test_dir)
        print(f"[测试] 创建假 Cursor 安装: {cursor_dir}")

        # 读取原始文件内容
        with open(workbench_html_path, 'r', encoding='utf-8') as f:
            original_html = f.read()
        with open(product_json_path, 'r', encoding='utf-8') as f:
            original_product = f.read()

        # 测试 --apply
        print("\n[测试] 运行 --apply...")
        result = subprocess.run(
            [sys.executable, "CursorTranslate.py", "--apply", f"--cursorDir={cursor_dir}"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            print(f"[错误] --apply 失败:")
            print(result.stdout)
            print(result.stderr)
            return False

        print("[成功] --apply 执行成功")

        # 验证注入
        with open(workbench_html_path, 'r', encoding='utf-8') as f:
            injected_html = f.read()

        if "<!-- CURSOR_HANHUA_INJECTION -->" not in injected_html:
            print("[错误] 未找到注入标记")
            return False

        if "cursor_hanhua.js" not in injected_html:
            print("[错误] 未找到脚本引用")
            return False

        print("[验证] HTML 注入成功")

        # 验证 JS 文件生成
        js_path = os.path.join(os.path.dirname(workbench_html_path), "cursor_hanhua.js")
        if not os.path.exists(js_path):
            print(f"[错误] JS 文件未生成: {js_path}")
            return False

        print(f"[验证] JS 文件已生成: {js_path}")

        # 验证 JS 语法
        result = subprocess.run(
            ["node", "--check", js_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"[错误] JS 语法检查失败:")
            print(result.stderr)
            return False

        print("[验证] JS 语法正确")

        # 验证 product.json 更新
        with open(product_json_path, 'r', encoding='utf-8') as f:
            updated_product = f.read()

        if updated_product == original_product:
            print("[错误] product.json 未更新")
            return False

        print("[验证] product.json 已更新")

        # 验证备份文件
        backup_html_path = workbench_html_path + ".bak"
        backup_product_path = product_json_path + ".bak"

        if not os.path.exists(backup_html_path):
            print("[错误] workbench.html 备份未创建")
            return False

        if not os.path.exists(backup_product_path):
            print("[错误] product.json 备份未创建")
            return False

        print("[验证] 备份文件已创建")

        # 测试 --restore
        print("\n[测试] 运行 --restore...")
        result = subprocess.run(
            [sys.executable, "CursorTranslate.py", "--restore", f"--cursorDir={cursor_dir}"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            print(f"[错误] --restore 失败:")
            print(result.stdout)
            print(result.stderr)
            return False

        print("[成功] --restore 执行成功")

        # 验证恢复
        with open(workbench_html_path, 'r', encoding='utf-8') as f:
            restored_html = f.read()

        if restored_html != original_html:
            print("[错误] HTML 未正确恢复")
            print(f"原始长度: {len(original_html)}, 恢复后长度: {len(restored_html)}")
            return False

        print("[验证] HTML 已正确恢复")

        # 验证 JS 文件删除
        if os.path.exists(js_path):
            print("[错误] JS 文件未删除")
            return False

        print("[验证] JS 文件已删除")

        # 验证备份文件删除
        if os.path.exists(backup_html_path):
            print("[错误] workbench.html 备份未删除")
            return False

        if os.path.exists(backup_product_path):
            print("[错误] product.json 备份未删除")
            return False

        print("[验证] 备份文件已删除")

        print("\n" + "=" * 60)
        print("  [成功] 所有 smoke test 通过！")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[错误] Smoke test 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理临时目录
        try:
            shutil.rmtree(test_dir)
            print(f"\n[清理] 已删除临时目录: {test_dir}")
        except Exception as e:
            print(f"\n[警告] 清理临时目录失败: {e}")

if __name__ == '__main__':
    success = run_smoke_test()
    sys.exit(0 if success else 1)
