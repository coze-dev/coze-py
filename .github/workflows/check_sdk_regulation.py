#!/usr/bin/env python3
"""
SDK 规范性检查脚本

这个脚本用于检查 SDK 代码是否符合预定义的规范。
设计为可扩展的架构，便于添加新的检查规则。

当前实现的规则：
1. 枚举的 key 必须全部大写，可以包含下划线
"""

import argparse
import ast
import json
import os
import sys
from typing import Any, Dict, List


class RegulationRule:
    """规范性规则基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.violations: List[Dict[str, Any]] = []

    def check(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """检查单个文件的规范性，返回规范性问题列表"""
        raise NotImplementedError

    def get_violations(self) -> List[Dict[str, Any]]:
        """获取所有规范性问题"""
        return self.violations

    def clear_violations(self):
        """清除规范性问题"""
        self.violations.clear()


class EnumNamingRule(RegulationRule):
    """枚举命名规范检查规则"""

    def __init__(self):
        super().__init__(name="enum_naming", description="枚举的 key 必须全部大写，可以包含下划线，且必须使用大写字母")

        # 需要忽略的旧代码枚举成员
        self.ignored_members = [
            "KVVariable",
            "ListVariable",
            "VariableChannelCustom",
            "VariableChannelSystem",
            "VariableChannelLocation",
            "VariableChannelFeishu",
            "VariableChannelAPP",
        ]

    def check(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是枚举类
                if self._is_enum_class(node):
                    violations.extend(self._check_enum_members(file_path, node))

        self.violations.extend(violations)
        return violations

    def _is_enum_class(self, node: ast.ClassDef) -> bool:
        """检查是否是枚举类"""
        # 检查基类是否包含 Enum
        for base in node.bases:
            if isinstance(base, ast.Name):
                # 处理直接导入的枚举类
                if base.id in ["Enum", "IntEnum", "DynamicStrEnum"]:
                    return True
            elif isinstance(base, ast.Attribute):
                # 处理 str, Enum 这种情况
                if isinstance(base.value, ast.Name) and base.attr == "Enum":
                    return True
                # 处理 DynamicStrEnum 这种情况
                elif base.attr in ["DynamicStrEnum", "IntEnum"]:
                    return True
                # 处理 cozepy.model.DynamicStrEnum 这种情况
                elif isinstance(base.value, ast.Attribute) and base.attr in ["DynamicStrEnum", "IntEnum"]:
                    return True
        return False

    def _check_enum_members(self, file_path: str, enum_class: ast.ClassDef) -> List[Dict[str, Any]]:
        """检查枚举成员的命名规范"""
        violations = []

        for node in enum_class.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        member_name = target.id
                        # 检查是否在忽略列表中
                        if member_name in self.ignored_members:
                            continue
                        if not self._is_valid_enum_member_name(member_name):
                            violations.append(
                                {
                                    "file": file_path,
                                    "line": node.lineno,
                                    "column": node.col_offset,
                                    "enum_class": enum_class.name,
                                    "member_name": member_name,
                                    "message": f"枚举成员 '{member_name}' 不符合命名规范，必须全部大写，可以包含下划线",
                                }
                            )

        return violations

    def _is_valid_enum_member_name(self, name: str) -> bool:
        """检查枚举成员名称是否符合规范"""
        # 排除私有成员和特殊方法
        if name.startswith("_"):
            return True

        # 检查是否全部大写，可以包含下划线和数字
        # 规则：必须全部大写，只能包含字母、数字和下划线
        if not name.isupper():
            return False

        # 检查是否只包含字母、数字和下划线
        for char in name:
            if not (char.isalnum() or char == "_"):
                return False

        # 检查是否至少包含一个字母
        if not any(char.isalpha() for char in name):
            return False

        return True


class SDKRegulationChecker:
    """SDK 规范性检查器"""

    def __init__(self):
        self.rules: List[RegulationRule] = []
        self.total_violations = 0

        # 注册默认规则
        self._register_default_rules()

    def _register_default_rules(self):
        """注册默认的规范性规则"""
        self.add_rule(EnumNamingRule())

    def add_rule(self, rule: RegulationRule):
        """添加新的规范性规则"""
        self.rules.append(rule)

    def check_file(self, file_path: str) -> Dict[str, Any]:
        """检查单个文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            file_violations = {}
            for rule in self.rules:
                rule_violations = rule.check(file_path, tree)
                if rule_violations:
                    file_violations[rule.name] = rule_violations

            return file_violations

        except SyntaxError as e:
            return {"syntax_error": {"message": f"语法错误: {e.msg}", "line": e.lineno, "column": e.offset}}
        except Exception as e:
            return {"error": {"message": f"检查文件时发生错误: {str(e)}"}}

    def check_directory(
        self, directory: str, include_patterns: List[str] = None, exclude_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """检查整个目录"""
        if include_patterns is None:
            include_patterns = ["*.py"]
        if exclude_patterns is None:
            exclude_patterns = [
                "__pycache__",
                ".git",
                ".venv",
                "venv",
                "node_modules",
                "tests/",
                "examples/",
                "scripts/",
            ]

        results = {}
        total_violations = 0

        for root, dirs, files in os.walk(directory):
            # 排除不需要的目录
            dirs[:] = [d for d in dirs if d not in exclude_patterns]

            for file in files:
                if any(file.endswith(pattern.replace("*", "")) for pattern in include_patterns):
                    file_path = os.path.join(root, file)
                    file_results = self.check_file(file_path)

                    if file_results:
                        results[file_path] = file_results
                        # 统计违规数量
                        for rule_name, violations in file_results.items():
                            if isinstance(violations, list):
                                total_violations += len(violations)

        self.total_violations = total_violations
        return results

    def print_report(self, results: Dict[str, Any], output_format: str = "text"):
        """打印检查报告"""
        if output_format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            self._print_text_report(results)

    def _print_text_report(self, results: Dict[str, Any]):
        """打印文本格式的报告"""
        print("=" * 80)
        print("SDK 规范性检查报告")
        print("=" * 80)

        if not results:
            print("✅ 未发现规范性问题")
            return

        total_files = len(results)
        total_violations = 0

        for file_path, file_results in results.items():
            print(f"\n📁 文件: {file_path}")

            for rule_name, violations in file_results.items():
                if rule_name in ["syntax_error", "error"]:
                    print(f"  ❌ {rule_name}: {violations['message']}")
                    total_violations += 1
                elif isinstance(violations, list):
                    print(f"  ⚠️  {rule_name}: {len(violations)} 个违规")
                    total_violations += len(violations)

                    for violation in violations:
                        print(f"    - 第 {violation['line']} 行: {violation['message']}")

        print("\n" + "=" * 80)
        print(f"总结: 检查了 {total_files} 个文件，发现 {total_violations} 个规范性问题")
        print("=" * 80)

        if total_violations > 0:
            print("❌ 检查失败，请修复上述规范性问题")
            sys.exit(1)
        else:
            print("✅ 所有检查通过")


def main():
    parser = argparse.ArgumentParser(description="SDK 规范性检查工具")
    parser.add_argument("path", nargs="?", default="cozepy", help="要检查的路径 (默认: cozepy)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式 (默认: text)")
    parser.add_argument("--include", nargs="*", default=["*.py"], help="包含的文件模式 (默认: *.py)")
    parser.add_argument(
        "--exclude", nargs="*", default=["__pycache__", ".git", ".venv", "venv", "node_modules"], help="排除的目录模式"
    )

    args = parser.parse_args()

    # 创建检查器
    checker = SDKRegulationChecker()

    # 执行检查
    if os.path.isfile(args.path):
        results = {args.path: checker.check_file(args.path)}
    else:
        results = checker.check_directory(args.path, args.include, args.exclude)

    # 打印报告
    checker.print_report(results, args.format)


if __name__ == "__main__":
    main()
