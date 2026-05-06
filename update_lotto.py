import pandas as pd
import json
import re
from collections import defaultdict

# ── 엑셀 읽기 ────────────────────────────────────────────
df = pd.read_excel("lotto.xlsx")
print(f"총 {len(df)}회차 데이터 로드 완료")

latest_round = int(df.iloc[0]["회차"])
latest_nums = [int(df.iloc[0][f"번호{i}"]) for i in range(1, 7)]
print(f"직전 회차: {latest_round}회, 번호: {latest_nums}")

# ── 직전 회차 제외하고 분포 계산 ─────────────────────────
df_calc = df.iloc[1:]
number_cols = ["번호1","번호2","번호3","번호4","번호5","번호6"]

dist = {col: defaultdict(int) for col in number_cols}
for _, row in df_calc.iterrows():
    for col in number_cols:
        dist[col][int(row[col])] += 1

dist = {col: dict(sorted(d.items())) for col, d in dist.items()}
top = {col: {"number": max(d, key=d.get), "count": max(d.values())} for col, d in dist.items()}

total_rows = len(df_calc)
print(f"분석 회차: {total_rows}회차")

# ── HTML 업데이트 ─────────────────────────────────────────
with open("lotto_analysis.html", "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'<div class="header-badge">.*?</div>',
    f'<div class="header-badge">1~{latest_round-1}회차 · 직전 회차({latest_round}회) 제외</div>', html)
html = re.sub(r'const TOP = \{.*?\};', f'const TOP = {json.dumps(top, ensure_ascii=False)};', html, flags=re.DOTALL)
html = re.sub(r'const DIST = \{.*?\};', f'const DIST = {json.dumps(dist, ensure_ascii=False)};', html, flags=re.DOTALL)
html = re.sub(r'const LATEST_NUMS = new Set\(\[.*?\]\);', f'const LATEST_NUMS = new Set({json.dumps(latest_nums)});', html)
nums_str = "·".join(map(str, latest_nums))
html = re.sub(r'직전 회차\([\d·]+\) 번호 제외', f'직전 회차({nums_str}) 번호 제외', html)

with open("lotto_analysis.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ HTML 업데이트 완료!")
