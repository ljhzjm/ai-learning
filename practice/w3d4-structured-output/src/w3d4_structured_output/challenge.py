"""验收挑战:12 条新闻 × 3 档策略,统计"合法 JSON / schema 通过 / 平均重试次数"。

验收线:tool 强制那行必须 12/12 schema 通过。
另外两档翻车不是 bug,是今天的重点——把翻车的原文抄进笔记。
"""

import sys

from w3d4_structured_output.extract_json import STRATEGIES, extract_with_retry
from w3d4_structured_output.settings import Settings

# 12 条,其中 4 条故意"缺字段"(没提金额 / 没提地点 / 日期只写"昨日" / 没提公司)
NEWS = [
    "2025年3月12日,腾讯公司创始人马化腾在深圳宣布,腾讯将向人工智能研究院投资50亿元。",
    "4月8日,字节跳动CEO梁汝波在北京与清华大学签署合作协议,捐赠2亿元用于人才培养。",
    "2024年11月5日,苹果公司CEO蒂姆·库克到访上海,与供应商立讯精密会面,未公布具体金额。",  # 缺金额
    "昨日,阿里巴巴集团董事会主席蔡崇信在杭州出席2025全球数字贸易博览会,宣布未来三年投入100亿美元。",  # 日期模糊
    "2023年9月20日,华为轮值董事长孟晚舟在深圳发布新款手机,华为终端公司未披露研发金额。",  # 缺金额
    "2025年1月1日,小米创始人雷军在北京宣布,小米汽车向北京理工大学捐赠5000万元。",
    "今日,诺贝尔物理学奖得主在斯德哥尔摩发表演讲,未提及任何商业合作。",  # 缺公司/金额
    "2025年6月18日,京东集团宣布全员涨薪,具体幅度未透露。",  # 缺人名/地点/金额
    "上周五,特斯拉CEO埃隆·马斯克在得克萨斯州试驾新款皮卡。",  # 日期模糊
    "2025年2月14日,比亚迪董事长王传福在深圳总部接待了来访的德国代表团。",  # 缺金额
    "2025年7月1日,宁德时代发布新一代电池技术,能量密度提升30%,未披露研发投入。",  # 缺人名/地点/金额
    "据外媒报道,英伟达CEO黄仁勋将于下月访问东京,会见日本半导体产业代表。",  # 日期模糊/缺金额
]


def main() -> None:
    sys.stdout.reconfigure(errors="replace")

    s = Settings()
    rows = []
    for label, fn in STRATEGIES:
        ok_json = ok_schema = total_tries = 0
        print(f"\n{'=' * 60}\n[{label}] 跑批 {len(NEWS)} 条\n{'=' * 60}")

        for i, news in enumerate(NEWS, 1):
            result, tries, first_ok = extract_with_retry(s, news, fn)
            ok_json += first_ok
            ok_schema += result is not None
            total_tries += tries
            if not result:
                print(f"  [{i}] [ERR] 3 次重试后仍失败:{news}")
            elif tries > 1 or not first_ok:
                print(f"  [{i}] [OK] 重试 {tries - 1} 次后通过:{news}")

        rows.append((label, ok_json, ok_schema, total_tries / len(NEWS)))

    print(f"\n{'=' * 60}\n[汇总] 验收标准:tool 强制 12/12\n{'=' * 60}")
    print(f"{'策略':<12}{'合法 JSON':>12}{'schema 通过':>14}{'平均重试次数':>16}")
    for label, oj, os_, avg in rows:
        print(f"{label:<12}{f'{oj}/{len(NEWS)}':>12}{f'{os_}/{len(NEWS)}':>14}{avg:>16.2f}")

    tool_ok = rows[-1][2]
    print(f"\n验收结果:{'通过 [OK]' if tool_ok == len(NEWS) else '不通过 [ERR]'}"
          f"(tool 强制 schema 通过 {tool_ok}/{len(NEWS)})")


if __name__ == "__main__":
    main()
