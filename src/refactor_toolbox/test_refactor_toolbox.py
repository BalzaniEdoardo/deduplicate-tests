#!/usr/bin/env python3
"""
Tool to extract, compare, and remove equivalent test functions using LibCST.
Preserves all formatting and whitespace.
"""

import libcst as cst
from typing import Dict, List, Set
import sys


class TestExtractor(cst.CSTVisitor):
    """Visitor that extracts all test functions (def test_*)"""

    def __init__(self):
        self.tests: Dict[str, cst.FunctionDef] = {}

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Visit function definitions and collect those starting with test_"""
        func_name = node.name.value
        if func_name.startswith("test_"):
            self.tests[func_name] = node


def extract_tests(file_path: str) -> Dict[str, cst.FunctionDef]:
    """Extract all test functions from a Python file"""
    with open(file_path, 'r') as f:
        source_code = f.read()

    tree = cst.parse_module(source_code)
    extractor = TestExtractor()
    tree.visit(extractor)

    return extractor.tests


def format_test_for_display(test_node: cst.FunctionDef) -> str:
    """Convert a test function node back to source code for display"""
    # Wrap the function in a module to get its code representation
    wrapper = cst.Module(body=[test_node])
    return wrapper.code

def compare_tests_interactive(tests1: Dict[str, cst.FunctionDef],
                              tests2: Dict[str, cst.FunctionDef],
                              file1_name: str,
                              file2_name: str) -> Set[str]:
    """
    Interactively compare tests and collect equivalent ones.
    Returns set of test names marked as equivalent.
    """
    equivalent_tests = set()

    # Find common test names
    common_tests = set(tests1.keys()) & set(tests2.keys())


    if not common_tests:
        print("No common test names found between the two files.")
        return equivalent_tests

    print(f"\nFound {len(common_tests)} common test name(s) to compare.\n")

    for test_name in sorted(common_tests):
        print("=" * 80)
        print(f"TEST: {test_name}")
        print("=" * 80)

        print(f"\n--- FROM {file1_name} ---")
        print(format_test_for_display(tests1[test_name]))

        print(f"\n--- FROM {file2_name} ---")
        print(format_test_for_display(tests2[test_name]))

        print("\n" + "-" * 80)
        response = input(f"Are these equivalent? (y/n): ").strip().lower()

        if response == 'y':
            equivalent_tests.add(test_name)
            print(f"✓ Marked '{test_name}' as equivalent")
        else:
            print(f"✗ Skipped '{test_name}'")

        print()

    return equivalent_tests


class TestRemover(cst.CSTTransformer):
    """Transformer that removes specific test functions while preserving formatting"""

    def __init__(self, tests_to_remove: Set[str]):
        self.tests_to_remove = tests_to_remove
        self.removed_count = 0

    def leave_FunctionDef(self,
                          original_node: cst.FunctionDef,
                          updated_node: cst.FunctionDef) -> cst.RemovalSentinel | cst.FunctionDef:
        """Remove function if it's in our removal list"""
        func_name = original_node.name.value

        if func_name in self.tests_to_remove:
            self.removed_count += 1
            return cst.RemovalSentinel.REMOVE

        return updated_node


def remove_tests_from_file(file_path: str,
                           tests_to_remove: Set[str],
                           output_path: str = None) -> str:
    """
    Remove specified tests from a file and return the modified source.
    If output_path is provided, writes to that file.
    """
    with open(file_path, 'r') as f:
        source_code = f.read()

    tree = cst.parse_module(source_code)
    remover = TestRemover(tests_to_remove)
    modified_tree = tree.visit(remover)

    modified_source = modified_tree.code

    if output_path:
        with open(output_path, 'w') as f:
            f.write(modified_source)
        print(f"\n✓ Removed {remover.removed_count} test(s) from {file_path}")
        print(f"✓ Wrote modified file to: {output_path}")

    return modified_source


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <file1.py> <file2.py>")
        print("\nThis will:")
        print("  1. Extract all test_* functions from both files")
        print("  2. Compare them interactively")
        print("  3. Remove equivalent tests from file1 and save to file1_cleaned.py")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    print(f"Extracting tests from {file1}...")
    tests1 = extract_tests(file1)
    print(f"Found {len(tests1)} test(s)")

    print(f"\nExtracting tests from {file2}...")
    tests2 = extract_tests(file2)
    print(f"Found {len(tests2)} test(s)")

    # Task 1: Compare tests interactively
    tests_to_be_removed = compare_tests_interactive(tests1, tests2, file1, file2)

    if not tests_to_be_removed:
        print("\nNo equivalent tests found. Exiting.")
        return

    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(tests_to_be_removed)} equivalent test(s) identified:")
    for test_name in sorted(tests_to_be_removed):
        print(f"  - {test_name}")

    # Task 2: Remove equivalent tests from file1
    output_file = file1.replace('.py', '_cleaned.py')
    if output_file == file1:
        output_file = file1 + '.cleaned'

    print("\n" + "=" * 80)
    print(f"TASK 2: Removing equivalent tests from {file1}")
    remove_tests_from_file(file1, tests_to_be_removed, output_file)

    print("\nDone! ✨")


if __name__ == "__main__":
    main()