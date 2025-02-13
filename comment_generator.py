import argparse
import logging
import os
import tempfile
from typing import Tuple

from tree_sitter import Language, Node, Parser, Tree, TreeCursor

# from summarize_deepseek import generate_class_body_summary, generate_combined_summary, generate_function_summary

# 使用绝对路径加载解析器
so_file = os.path.join(os.path.abspath('build'), 'my-languages.so')
print(f"Loading parser from: {so_file}")

if not os.path.exists(so_file):
    raise FileNotFoundError(f"The .so file was not created at {so_file}")

SWIFT_LANGUAGE = Language(so_file, 'swift')


def edit_function_declarations(tree: Tree, source: bytes) -> bytes:
    #  获取 Tree 的指针
    tree_cursor: TreeCursor = tree.walk()
    class_summaries = {}
    function_summaries = []

    def process_class_declarations(cursor: TreeCursor) -> None:
        #  声明改变量为外部函数的局部变量
        nonlocal class_summaries
        node: Node = cursor.node
        if node.type == "class_declaration":
            #  如果是类
            class_name = node.child_by_field_name('name')
            logging.info(f"正在处理 类: {class_name}")

            class_summaries[node.id] = []
            class_body = next((child for child in node.children if child.type == "class_body"), None)

            if class_body:
                #  如果类体存在
                process_function_declarations(class_body)

            #  如果 class_summaries 不存在该 node.id
            if not class_summaries[node.id]:
                class_summaries[node.id] = node

        if cursor.goto_first_child():
            process_class_declarations(cursor)
            while cursor.goto_next_sibling():
                process_class_declarations(cursor)
            cursor.goto_parent()

    def process_function_declarations(class_node: Node) -> None:
        nonlocal function_summaries
        for node in class_node.children:
            #  遍历子节点，寻找方法体/属性
            if node.type in ["function_declaration", "property_declaration"]:
                name = node.child_by_field_name('name')
                logging.info(f"Processing function/property declaration: {name}")
                func_body = node.text.decode("utf8")
                print(f"func body: {func_body}")
                # summary: str = generate_function_summary(node)
                print()

                summary = "hello"
                parent = node.parent
                grandparent = parent.parent if parent else None
                if grandparent and grandparent.type == "class_declaration":
                    class_summaries[grandparent.id].append((node, summary))
                function_summaries.append((node, summary))

    process_class_declarations(tree_cursor)
    process_function_declarations(tree.root_node)

    # Combine summaries
    summaries = function_summaries

    for _, children in class_summaries.items():
        if isinstance(children, list):
            # concatenated_summary = generate_combined_summary([summary for _, summary in children])
            concatenated_summary = "generate_combined_summary 的结果"
            summaries.append((children[0][0].parent.parent, concatenated_summary))
        elif isinstance(children, Node):
            # concatenated_summary = generate_class_body_summary(children.text.decode("utf8"))
            concatenated_summary = f"这是类的数值{children.id}"
            summaries.append((children, concatenated_summary))
        else:
            logging.error(f"Unexpected type {type(children)}")

    # Sort summaries by start byte
    summaries.sort(key=lambda x: x[0].start_byte)

    # Insert summaries into the source code
    for node, summary in reversed(summaries):
        indent: str = " " * node.start_point[1]
        summary = "\n".join([f"{indent}{line}" for line in summary.split("\n")])
        summary = f"{summary[node.start_point[1]:]}\n{indent}"
        source = source[: node.start_byte] + summary.encode("utf8") + source[node.start_byte:]

    return source


def insert_summary(file_path: str, new_code: str) -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(new_code)
    os.replace(temp_file.name, file_path)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add documentation to Swift file.")
    parser.add_argument("file_path", type=str, help="Path to the Swift file.")
    return parser.parse_args()


def read_swift_file(file_path: str) -> Tuple[str, bytes]:
    with open(file_path, "r") as f:
        original: str = f.read()
    as_bytes = bytes(original, "utf8")
    return original, as_bytes


def parse_swift_source(source: bytes) -> Tree:
    """
    使用语言解析器将bytes 转换为 tree_sitter 的 Tree
    :param source: 语言代码文件的bytes
    :return: tree_sitter 的 Tree
    """

    #  创建解析器实例
    swift_parser: Parser = Parser()
    #  配置语言的 .so
    swift_parser.set_language(SWIFT_LANGUAGE)
    #  使用解析器解析并返回结果
    return swift_parser.parse(source)


def traverse_tree(node, source_code):
    # if node.type == 'function_definition':
    print(node)
    print(node.text)
    print("\n")

    # function_name_node = node.child_by_field_name('name')
    # function_name = source_code[function_name_node.start_byte:function_name_node.end_byte].decode('utf-8')
    # print(f"Function name: {function_name}")
    # 递归遍历子节点
    for child in node.children:
        traverse_tree(child, source_code)


if __name__ == "__main__":
    #  为命令行使用是的参数
    # args = parse_arguments()
    # file_path: str = args.file_path

    file_path = "example/HotPointRankView.swift"
    #  读取代码文件内容，original 为代码原文，as_bytes 将代码文件内容转换为 bytes
    original, as_bytes = read_swift_file(file_path)

    #  将 代码文件bytes 转换成 tree_sitter 的 Tree
    tree = parse_swift_source(as_bytes)
    # traverse_tree(tree.root_node, as_bytes)
    new_code = edit_function_declarations(tree, as_bytes).decode("utf8")
    print(new_code)
    # insert_summary(file_path, new_code)
