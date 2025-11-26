#!/usr/bin/env python3
"""
测试ML后端模块导入
"""
import sys
import traceback

print("测试ML后端模块导入...")
print("-" * 50)

try:
    from app.api import ml_backend
    print("✅ ml_backend模块导入成功")
    print(f"✅ router对象: {ml_backend.router}")
    print(f"✅ 路由数量: {len(ml_backend.router.routes)}")
    for route in ml_backend.router.routes:
        print(f"  - {route.methods if hasattr(route, 'methods') else 'N/A'} {route.path}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print("-" * 50)
print("测试完成！")

