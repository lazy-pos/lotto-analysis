import requests
import json
import re
import time
from collections import defaultdict

# ── 1. 최신 회차 확인 ──────────────────────────────────────
def get_latest_round():
    url = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=1"import requestsimport requests
import json
import re
import time
from collections import defaultdict
from bs4 import BeautifulSoup

# ── 세션 생성 (브라우저처럼 쿠키 유지) ────────────────────
def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })
    # 메인 페이지 먼저 방문해서 쿠키 획득
    try:
        session.get("https://www.dhlottery.co.kr/common.do?method=main", timeout=10)
    except:
        pass
    return session

# ── 단일 회차 가져오기 ────────────────────────────────────
def fetch_round(session, drw):
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drw}"
    try:
        r = session.get(url, timeout=10)
        data = r.json()
        if data.get("returnValue") == "success":
            return [data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                    data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]]
    except:
        pass
    return None

# ── 최신 회차 확인 ────────────────────────────────────────
def get_latest_round(session):
    for drw in range(1250, 1200, -1):
        nums = fetch_round(session, drw)
        if nums:
            print(f"최신 회차: {drw}")
            return drw
        time.sleep(0.3)
    return None

# ── 전체 데이터 수집 ──────────────────────────────────────
def fetch_all_data(session, latest_round):
    results = []
    print(f"{latest_round}회차 데이터 수집 시작...")
    for drw in range(1, latest_round + 1):
        nums = fetch_round(session, drw)
        if nums:
            results.append({"round": drw, "nums": nums})
        if drw % 50 == 0:
            print(f"  {drw}/{latest_round} 완료...")
            time.sleep(0.5)
        else:
            time.sleep(0.08)
    print(f"총 {len(results)}회차 수집 완료")
    return results

# ── 분포 계산 ─────────────────────────────────────────────
def calc_distributions(data, exclude_round):
    dist = [defaultdict(int) for _ in range(6)]
    for row in data:
        if row["round"] == exclude_round:
            continue
        for i, num in enumerate(row["nums"]):
            dist[i][num] += 1
    keys = ["번호1","번호2","번호3","번호4","번호5","번호6"]
    return {key: dict(sorted(dist[i].items())) for i, key in enumerate(keys)}

def calc_top(dist):
    return {key: {"number": max(counts, key=counts.get), "count": max(counts.values())}
            for key, counts in dist.items()}

# ── HTML 업데이트 ─────────────────────────────────────────
def update_html(html_path, latest_round, latest_nums, dist, top, total_rows):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'<div class="header-badge">.*?</div>',
        f'<div class="header-badge">1~{latest_round-1}회차 · 직전 회차({latest_round}회) 제외</div>', html)
    html = re.sub(r'const TOP = \{.*?\};', f'const TOP = {json.dumps(top, ensure_ascii=False)};', html, flags=re.DOTALL)
    html = re.sub(r'const DIST = \{.*?\};', f'const DIST = {json.dumps(dist, ensure_ascii=False)};', html, flags=re.DOTALL)
    html = re.sub(r'const LATEST_NUMS = new Set\(\[.*?\]\);', f'const LATEST_NUMS = new Set({json.dumps(latest_nums)});', html)
    nums_str = '·'.join(map(str, latest_nums))
    html = re.sub(r'직전 회차\([\d·]+\) 번호 제외', f'직전 회차({nums_str}) 번호 제외', html)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML 업데이트 완료! {latest_round}회차, 직전 번호: {latest_nums}")

# ── MAIN ──────────────────────────────────────────────────
if __name__ == "__main__":
    import subprocess
    subprocess.run(["pip", "install", "requests", "beautifulsoup4", "-q"])

    print("세션 생성 중...")
    session = create_session()

    print("최신 회차 확인 중...")
    latest_round = get_latest_round(session)
    if not latest_round:
        print("❌ 최신 회차 확인 실패")
        exit(1)

    all_data = fetch_all_data(session, latest_round)
    if not all_data:
        print("❌ 데이터 수집 실패")
        exit(1)

    latest_nums = all_data[-1]["nums"]
    dist = calc_distributions(all_data, latest_round)
    top = calc_top(dist)
    update_html("lotto_analysis.html", latest_round, latest_nums, dist, top, latest_round - 1)

import json
import re
import time
from collections import defaultdict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# ── 1. 최신 회차 확인 ──────────────────────────────────────
def get_latest_round():
    for drw in range(1250, 1200, -1):
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drw}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            data = r.json()
            if data.get("returnValue") == "success":
                print(f"최신 회차 확인: {drw}")
                return drw
        except Exception as e:
            print(f"{drw}회차 확인 실패: {e}")
        time.sleep(0.3)
    return None

# ── 2. 전체 회차 데이터 가져오기 ───────────────────────────
def fetch_all_data(latest_round):
    results = []
    print(f"총 {latest_round}회차 데이터 수집 중...")
    for drw in range(1, latest_round + 1):
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drw}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            data = r.json()
            if data.get("returnValue") == "success":
                results.append({
                    "round": drw,
                    "nums": [
                        data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                        data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]
                    ]
                })
        except Exception as e:
            print(f"{drw}회차 오류: {e}")
        if drw % 100 == 0:
            print(f"  {drw}회차 완료...")
            time.sleep(1)
        else:
            time.sleep(0.1)
    print(f"총 {len(results)}회차 수집 완료")
    return results

# ── 3. 분포 계산 ───────────────────────────────────────────
def calc_distributions(data, exclude_round):
    dist = [defaultdict(int) for _ in range(6)]
    for row in data:
        if row["round"] == exclude_round:
            continue
        for i, num in enumerate(row["nums"]):
            dist[i][num] += 1

    keys = ["번호1","번호2","번호3","번호4","번호5","번호6"]
    result = {}
    for i, key in enumerate(keys):
        result[key] = dict(sorted(dist[i].items()))
    return result

def calc_top(dist):
    top = {}
    for key, counts in dist.items():
        best_num = max(counts, key=counts.get)
        top[key] = {"number": best_num, "count": counts[best_num]}
    return top

# ── 4. HTML 업데이트 ───────────────────────────────────────
def update_html(html_path, latest_round, latest_nums, dist, top, total_rows):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(
        r'<div class="header-badge">.*?</div>',
        f'<div class="header-badge">1~{latest_round-1}회차 · 직전 회차({latest_round}회) 제외</div>',
        html
    )

    top_js = json.dumps(top, ensure_ascii=False)
    html = re.sub(r'const TOP = \{.*?\};', f'const TOP = {top_js};', html, flags=re.DOTALL)

    dist_js = json.dumps(dist, ensure_ascii=False)
    html = re.sub(r'const DIST = \{.*?\};', f'const DIST = {dist_js};', html, flags=re.DOTALL)

    latest_set = f'new Set({json.dumps(latest_nums)})'
    html = re.sub(r'const LATEST_NUMS = new Set\(\[.*?\]\);', f'const LATEST_NUMS = {latest_set};', html)

    nums_str = '·'.join(map(str, latest_nums))
    html = re.sub(
        r'직전 회차\([\d·]+\) 번호 제외',
        f'직전 회차({nums_str}) 번호 제외',
        html
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML 업데이트 완료! (최신: {latest_round}회차, 직전 번호: {latest_nums})")

# ── MAIN ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("동행복권 API에서 데이터 수집 시작...")
    latest_round = get_latest_round()
    if latest_round is None:
        print("❌ 최신 회차를 찾을 수 없습니다.")
        exit(1)

    all_data = fetch_all_data(latest_round)
    if not all_data:
        print("❌ 데이터 수집 실패")
        exit(1)

    latest_nums = all_data[-1]["nums"]
    print(f"직전 회차({latest_round}) 번호: {latest_nums}")

    dist = calc_distributions(all_data, latest_round)
    top = calc_top(dist)
    total_rows = latest_round - 1

    update_html("lotto_analysis.html", latest_round, latest_nums, dist, top, total_rows)

    # 최신 회차는 큰 수부터 시도
    for drw in range(1250, 1200, -1):
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drw}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("returnValue") == "success":
            return drw
    return None

# ── 2. 전체 회차 데이터 가져오기 ───────────────────────────
def fetch_all_data(latest_round):
    results = []
    print(f"총 {latest_round}회차 데이터 수집 중...")
    for drw in range(1, latest_round + 1):
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drw}"
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            if data.get("returnValue") == "success":
                results.append({
                    "round": drw,
                    "nums": [
                        data["drwtNo1"], data["drwtNo2"], data["drwtNo3"],
                        data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]
                    ]
                })
        except:
            pass
        if drw % 100 == 0:
            print(f"  {drw}회차 완료...")
            time.sleep(0.5)
    return results

# ── 3. 분포 계산 ───────────────────────────────────────────
def calc_distributions(data, exclude_round):
    """직전 회차 제외하고 분포 계산"""
    dist = [defaultdict(int) for _ in range(6)]  # 6자리
    for row in data:
        if row["round"] == exclude_round:
            continue
        for i, num in enumerate(row["nums"]):
            dist[i][num] += 1

    keys = ["번호1","번호2","번호3","번호4","번호5","번호6"]
    result = {}
    for i, key in enumerate(keys):
        result[key] = dict(sorted(dist[i].items()))
    return result

def calc_top(dist):
    top = {}
    for key, counts in dist.items():
        best_num = max(counts, key=counts.get)
        top[key] = {"number": best_num, "count": counts[best_num]}
    return top

# ── 4. HTML 업데이트 ───────────────────────────────────────
def update_html(html_path, latest_round, latest_nums, dist, top, total_rows):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 헤더 배지
    html = re.sub(
        r'<div class="header-badge">.*?</div>',
        f'<div class="header-badge">1~{latest_round-1}회차 · 직전 회차({latest_round}회) 제외</div>',
        html
    )

    # TOP 데이터
    top_js = json.dumps(top, ensure_ascii=False)
    html = re.sub(r'const TOP = \{.*?\};', f'const TOP = {top_js};', html, flags=re.DOTALL)

    # DIST 데이터
    dist_js = json.dumps(dist, ensure_ascii=False)
    html = re.sub(r'const DIST = \{.*?\};', f'const DIST = {dist_js};', html, flags=re.DOTALL)

    # 직전 회차 번호
    latest_set = f'new Set({json.dumps(latest_nums)})'
    html = re.sub(r'const LATEST_NUMS = new Set\(\[.*?\]\);', f'const LATEST_NUMS = {latest_set};', html)

    # 분석 회차 수
    html = re.sub(r'<div class="stat-value">\d+,?\d+</div>\s*<div class="stat-label">분석 회차</div>',
                  f'<div class="stat-value">{total_rows:,}</div>\n      <div class="stat-label">분석 회차</div>', html)

    # 직전 회차 번호 표시 (picker subtitle)
    nums_str = '·'.join(map(str, latest_nums))
    html = re.sub(
        r'직전 회차\([\d·]+\) 번호 제외',
        f'직전 회차({nums_str}) 번호 제외',
        html
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML 업데이트 완료! (최신: {latest_round}회차, 직전 번호: {latest_nums})")

# ── MAIN ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("동행복권 API에서 데이터 수집 시작...")
    latest_round = get_latest_round()
    print(f"최신 회차: {latest_round}")

    all_data = fetch_all_data(latest_round)
    latest_nums = all_data[-1]["nums"]  # 직전 회차 번호
    print(f"직전 회차({latest_round}) 번호: {latest_nums}")

    dist = calc_distributions(all_data, latest_round)
    top = calc_top(dist)
    total_rows = latest_round - 1  # 직전 회차 제외

    update_html("lotto_analysis.html", latest_round, latest_nums, dist, top, total_rows)
