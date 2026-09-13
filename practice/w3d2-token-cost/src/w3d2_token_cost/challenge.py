"""验收挑战:3 段未参与校准的新文本,预测成本 vs 真实成本,误差 < 20%。

提示:用开放式的长答问题(如"详细介绍一下……"),模型才会把 max_tokens 预算用满,
输出 token 的估算(max_out)才和实际对得上。
"""

from w3d2_token_cost.cost import estimate_cost
from w3d2_token_cost.settings import Settings

# 短/中/长三段新文本(没参与 calibrate.py 的校准样本),都是开放式的"长答"题
TEXTS = [
    "请详细介绍一下杭州的西湖。",
    "请详细介绍一下人工智能应用开发工程师需要掌握的技能,包括后端工程与模型应用两个方面。",
    "请详细介绍一下 token 估算与计价的方法:中文按字数乘系数、英文按字符数除四、线性拟合求斜率与截距、价格页单位是每百万 tokens,以及多轮对话的缓存命中更便宜。",
]

MAX_OUT = 50  # 输出预算;开放式问题下模型会尽量用满


def main() -> None:
    s = Settings()
    ok = True
    for text in TEXTS:
        est, actual = estimate_cost(s, text, max_out=MAX_OUT)
        err = (est - actual) / actual * 100
        if abs(err) >= 20:
            ok = False
        tag = "[OK]" if abs(err) < 20 else "[ERR]"
        print(f"{tag} 误差 {err:+6.1f}%  预估 ¥{est:.5f} / 实际 ¥{actual:.5f}  「{text[:16]}...」")
    print("挑战通过!误差全部 < 20%" if ok else "有文本误差 >= 20%:加长样本重跑 calibrate.py 再校准")


if __name__ == "__main__":
    main()
