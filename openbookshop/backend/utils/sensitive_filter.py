"""DFA（确定有限状态自动机）敏感词过滤器"""


# 默认敏感词列表（实际项目可从数据库或文件加载）
DEFAULT_SENSITIVE_WORDS = [
    '垃圾', '骗子', '诈骗', '刷单', '黄赌毒',
    '违禁', '盗版', '假货', '欺诈', '侮辱',
    '暴力', '色情', '赌博', '毒品', '违法',
]


class DFAFilter:
    """DFA敏感词过滤器"""

    def __init__(self, words=None):
        self._trie = {}
        self._end_key = '\x00'
        words = words or DEFAULT_SENSITIVE_WORDS
        for word in words:
            self.add_word(word)

    def add_word(self, word: str):
        """向字典树添加敏感词"""
        node = self._trie
        for char in word:
            node = node.setdefault(char, {})
        node[self._end_key] = True

    def contains(self, text: str) -> bool:
        """检测文本是否包含敏感词，返回 True/False"""
        for i in range(len(text)):
            node = self._trie
            j = i
            while j < len(text) and text[j] in node:
                node = node[text[j]]
                if self._end_key in node:
                    return True
                j += 1
        return False

    def filter(self, text: str, replace_char: str = '*') -> str:
        """将文本中的敏感词替换为指定字符"""
        result = list(text)
        i = 0
        while i < len(text):
            node = self._trie
            j = i
            matched_end = -1
            while j < len(text) and text[j] in node:
                node = node[text[j]]
                if self._end_key in node:
                    matched_end = j
                j += 1
            if matched_end >= 0:
                for k in range(i, matched_end + 1):
                    result[k] = replace_char
                i = matched_end + 1
            else:
                i += 1
        return ''.join(result)


# 全局单例
sensitive_filter = DFAFilter()
