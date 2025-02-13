def traverse_tree(node, source_code):
    # if node.type == 'function_definition':
    print(node)
    print(node.type)
    print(node.text)
    print("\n")

        # function_name_node = node.child_by_field_name('name')
        # function_name = source_code[function_name_node.start_byte:function_name_node.end_byte].decode('utf-8')
        # print(f"Function name: {function_name}")
        # 递归遍历子节点
    for child in node.children:
        traverse_tree(child, source_code)
