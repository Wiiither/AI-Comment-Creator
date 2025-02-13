from tree_sitter import Language, Parser
import os
import subprocess

def run_command(command):
    """执行命令并打印输出"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Command output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        raise

# 创建 build 目录
if not os.path.exists("build"):
    os.makedirs("build")

#  克隆 Swift 语言解析器仓库
#  TODO: 这里的地址是固定的，需要找个方法或者配置去获取（或者直接克隆到工程里）
if not os.path.exists("tree-sitter-swift"):
    print("克隆语言解析器仓库...")
    run_command("git clone https://github.com/alex-pinkus/tree-sitter-swift.git")

try:
    print("Building language parser...")
    # 构建语言解析器
    Language.build_library(
        # 使用绝对路径
        os.path.join(os.path.abspath('build'), 'my-languages.so'),
        [os.path.abspath('tree-sitter-swift')]
    )
except Exception as e:
    print(f"Error building language parser: {e}")
    raise

# 使用绝对路径加载解析器
so_file = os.path.join(os.path.abspath('build'), 'my-languages.so')
print(f"Loading parser from: {so_file}")

if not os.path.exists(so_file):
    raise FileNotFoundError(f"The .so file was not created at {so_file}")

SWIFT_LANGUAGE = Language(so_file, 'swift')
parser = Parser()
parser.set_language(SWIFT_LANGUAGE)

# Swift 测试代码
code = """
    let name = "hello"
"""

tree = parser.parse(bytes(code, 'utf8'))
root_node = tree.root_node
print(root_node.sexp())
