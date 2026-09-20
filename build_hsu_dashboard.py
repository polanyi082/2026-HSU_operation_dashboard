"""경기대 운영 대시보드(2026-KGU_operation_dashboard)를 한신대 버전으로 변환.

    python build_hsu_dashboard.py      # kgu.html -> hsudash/index.html
"""
import io, os

SRC = "kgu.html"
OUT = os.path.join("hsudash", "index.html")

s = io.open(SRC, encoding="utf-8").read()


def cut(a, b=""):
    global s
    assert a in s, "못 찾음: " + a[:70]
    s = s.replace(a, b, 1)


# ─────────── 1. 브랜딩 · 문구 ───────────
cut("<title>소통 참여자 현황판</title>", "<title>한신대 채용박람회 참여자 현황판</title>")
cut('      <span class="mark">소통<span class="o"></span></span>\n')          # 워드마크 삭제
cut('<div class="eyebrow">경기대학교 · 제11회 직무채용박람회</div>',
    '<div class="eyebrow">2026 한신대학교 채용박람회</div>')

cut('<button class="chip" type="button" data-win="event" aria-pressed="false">행사 시간 12:30–16:40</button>',
    '<button class="chip" type="button" data-win="event" aria-pressed="false">행사 시간 10:00–17:00</button>')
cut('<input type="time" id="fromTime" value="12:30" step="900" aria-label="시작 시각">',
    '<input type="time" id="fromTime" value="10:00" step="900" aria-label="시작 시각">')
cut('<input type="time" id="toTime" value="16:40" step="900" aria-label="종료 시각">',
    '<input type="time" id="toTime" value="17:00" step="900" aria-label="종료 시각">')

cut('<button class="chip" type="button" data-aff="경기대학교" aria-pressed="false">경기대학교</button>',
    '<button class="chip" type="button" data-aff="한신대학교" aria-pressed="false">한신대학교</button>')

cut("""    주최 경기대학교 인재개발처 대학일자리플러스센터 · 제39대 우리 총학생회 &nbsp;|&nbsp;
    참여 고용노동부 · 경기도 · 수원고용복지＋센터 · 경기도일자리재단 · 수원상공회의소 · 경기경영자총협회 · 조인스잡""",
    """    주최 한신대학교 대학일자리플러스센터 &nbsp;|&nbsp; 주관 (주)엘리트코리아""")

cut('<textarea id="pasteSat" placeholder="타임스탬프&#9;1. 참여자 유형…"></textarea>',
    '<textarea id="pasteSat" placeholder="타임스탬프&#9;1. 이름을 작성해주세요…"></textarea>')

# ─────────── 2. 데이터 소스 · 행사 시간 ───────────
cut("""const SHEETS = {
  reg: "1KsWb7b5bW2nfL2smIhAezyQUmMZwsBoRKToNQAf3M0A",
  sat: "1Flp0eykT15rrmRhyVVhxUyXlo78Fu4DUQrq70f2Q59I"
};""",
    """const SHEETS = {
  reg: "1wUvGjwOobw3OF-ib1RXgDTGvTRCH2J1plnkKc92lNRE",   // 현장등록
  sat: "1Vo1gSogcpAFW1RQLvxu1BH25apatLaU8uTNEyAcK-Ok"    // 만족도 조사
};""")

cut("const EVENT_WINDOW = {from: 12*60 + 30, to: 16*60 + 40};   // 12:30 ~ 16:40",
    "const EVENT_WINDOW = {from: 10*60, to: 17*60};             // 10:00 ~ 17:00")

# ─────────── 3. 소속 라벨 ───────────
cut("// 머리글 라벨이 중복되는 구조(경기대 섹션 / 지역청년 섹션)라 등장 순서로 구분한다.",
    "// 머리글 라벨이 중복되는 구조(한신대 섹션 / 지역청년 섹션)라 등장 순서로 구분한다.")
cut('    const kgu = !at(r,C.aff).includes("지역");', '    const hsu = !at(r,C.aff).includes("지역");')
cut("    const k = kgu ? 0 : 1;", "    const k = hsu ? 0 : 1;")
cut('      ts, aff: kgu ? "경기대학교" : "지역청년",', '      ts, aff: hsu ? "한신대학교" : "지역청년",')
cut('      sid: kgu ? sid : "",', '      sid: hsu ? sid : "",')
cut('      school: kgu ? "경기대학교" : (at(r,C.school) || "―"),',
    '      school: hsu ? "한신대학교" : (at(r,C.school) || "―"),')
cut("      sidBad: kgu && !!sid && !/^\\d{9}$|^\\d{10}$/.test(sid)",
    "      sidBad: hsu && !!sid && !/^\\d{9}$|^\\d{10}$/.test(sid)")
cut('  const kgu = reg.filter(r=>r.aff==="경기대학교").length;',
    '  const hsu = reg.filter(r=>r.aff==="한신대학교").length;')
cut("  const loc = reg.length - kgu;", "  const loc = reg.length - hsu;")
cut('    ["경기대학교", kgu, "명", "", reg.length ? Math.round(kgu/reg.length*100)+"%" : ""],',
    '    ["한신대학교", hsu, "명", "", reg.length ? Math.round(hsu/reg.length*100)+"%" : ""],')

# ─────────── 4. 추이·구간표 축을 행사 시작(10:00)부터 고정 ───────────
cut("""  let start, end;
  if(state.win === "all"){
    if(!items.length) return [];
    const all = items.map(i=>bucketOf(i.ts));
    start = Math.min(...all); end = Math.max(...all);
  }else{""",
    """  let start, end;
  if(state.win === "all"){
    // 전체 보기에서도 축은 행사 시작(10:00)부터. 그보다 늦은 기록이 있으면 뒤로만 늘린다.
    start = Math.floor(EVENT_WINDOW.from / BUCKET_MIN) * BUCKET_MIN;
    end   = Math.floor(EVENT_WINDOW.to   / BUCKET_MIN) * BUCKET_MIN;
    const late = items.map(i=>bucketOf(i.ts)).filter(m=>m > end);
    if(late.length) end = Math.max(...late);
  }else{""")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("생성:", OUT, len(s), "bytes")
