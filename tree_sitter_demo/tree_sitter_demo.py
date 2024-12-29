import os.path

from tree_sitter import Language, Parser, Node, Tree

#  tree-sitter 使用 0.21.x 版本
#  新版本的貌似只能够通过 pypi 对应的语言库进行处理
#  然而还有需要语言并不支持，如 Swift
#  https://github.com/tree-sitter/py-tree-sitter/discussions/241

#  start
#  创建 build 目录
if not os.path.exists("build"):
    os.makedirs("build")

# 克隆 Swift 语言解析器仓库（使用社区维护的版本）
if not os.path.exists("tree-sitter-swift"):
    os.system("git clone https://github.com/alex-pinkus/tree-sitter-swift.git")

SWIFT_LANGUAGE = Language('build/my-languages.so', 'swift')
parser = Parser()
parser.set_language(SWIFT_LANGUAGE)
