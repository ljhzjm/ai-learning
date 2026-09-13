def estimate_tokens_zh(text: str) -> int:
    """中文:字数 × 系数(初版 1.5,校准后回填)。"""
    return int(len(text) * 0.705 + 4.20)


def estimate_tokens_en(text: str) -> int:
    """英文:字符数 ÷ 4(字符数法,长词也不慌)。"""
    return int(len(text) / 4)