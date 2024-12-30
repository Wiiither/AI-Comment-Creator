### 什么是 Tree-sitter?
Tree-sitter 是一个用于构建解析器的工具，主要用于语法高亮、代码折叠和其他代码编辑器功能。它能够快速地解析源代码并生成抽象语法树（AST），使得开发者可以更容易地分析和操作代码。

Tree-sitter 的主要特点包括：
1. 增量解析：它支持增量解析，这意味着当代码发生变化时，只需重新解析受影响的部分，而不是整个文件，从而提高性能。
2. 多语言支持：Tree-sitter 支持多种编程语言，开发者可以为不同的语言创建解析器。
3. 高效的语法定义：使用一种简单的语法定义语言，开发者可以轻松地定义语言的语法规则。
4. 与编辑器集成：Tree-sitter 可以与文本编辑器（如 Neovim、Atom 等）集成，提供实时的语法高亮和代码分析功能。

总之，Tree-sitter 是一个强大的工具，适用于需要解析和分析代码的各种应用场景。

### 使用的 tree-sitter 的版本


### 如果出现类似 type object 'tree_sitter.Language' has no attribute 'build_library' 的错误
将 tree-sitter 的版本降级到 0.21.3 即可

https://github.com/tree-sitter/py-tree-sitter/discussions/241