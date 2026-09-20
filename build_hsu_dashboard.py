"""경기대 운영 대시보드(2026-KGU_operation_dashboard)를 한신대 버전으로 변환."""
import io, os, sys

SRC = "kgu.html"
OUT = os.path.join("hsudash", "index.html")

s = io.open(SRC, encoding="utf-8").read()


def cut(a, b):
    global s
    assert a in s, "못 찾음: " + a[:70]
    s = s.replace(a, b, 1)


def cut_all(a, b):
    global s
    assert a in s, "못 찾음: " + a[:70]
    s = s.replace(a, b)


# ─────────── 1. 브랜딩 · 문구 ───────────
cut("<title>소통 참여자 현황판</title>", "<title>한신대 채용박람회 참여자 현황판</title>")
cut('<span class="mark">소통<span class="o"></span></span>',
    '<span class="mark">한신<span class="o"></span></span>')
cut('<div class="eyebrow">경기대학교 · 제11회 직무채용박람회</div>',
    '<div class="eyebrow">한신대학교 · 2026 채용박람회</div>')

cut('<button class="chip" type="button" data-win="event" aria-pressed="false">행사 시간 12:30–16:40</button>',
    '<button class="chip" type="button" data-win="event" aria-pressed="false">행사 시간 10:00–16:30</button>')
cut('<input type="time" id="fromTime" value="12:30" step="900" aria-label="시작 시각">',
    '<input type="time" id="fromTime" value="10:00" step="900" aria-label="시작 시각">')
cut('<input type="time" id="toTime" value="16:40" step="900" aria-label="종료 시각">',
    '<input type="time" id="toTime" value="16:30" step="900" aria-label="종료 시각">')

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
    "const EVENT_WINDOW = {from: 10*60, to: 16*60 + 30};        // 10:00 ~ 16:30")

# ─────────── 3. 소속 라벨 ───────────
cut('      ts, aff: kgu ? "경기대학교" : "지역청년",', '      ts, aff: hsu ? "한신대학교" : "지역청년",')
cut('    const kgu = !at(r,C.aff).includes("지역");', '    const hsu = !at(r,C.aff).includes("지역");')
cut("    const k = kgu ? 0 : 1;", "    const k = hsu ? 0 : 1;")
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

# ─────────── 4. 만족도 파서 — 문항별 응답까지 읽는다 ───────────
cut("""// 만족도 시트에서는 응답 인원만 센다. 문항별 세부 내역은 다루지 않는다.
function parseSat(input){
  const rows = Array.isArray(input) ? input : toRows(input);
  if(rows.length < 2) return [];
  const tsCol = colFinder(rows[0])("타임스탬프");
  return rows.slice(1)
    .map(r => parseTs(at(r, tsCol)))
    .filter(Boolean)
    .map(ts => ({ts}))
    .sort((a,b)=>b.ts-a.ts);
}""",
"""/* 만족도 시트: 인원 + 문항별 점수 + 부스 선택 + 자유응답.
   척도 보기는 '매우만족 ~ 매우불만족' 5단계. */
const SAT_Q = [
  {key:"q1", find:"전반적인만족도는",   label:"전반적 만족도"},
  {key:"q2", find:"주제와내용은",       label:"주제·내용 적합성"},
  {key:"q3", find:"강사에대한",         label:"강사 만족도"},
  {key:"q4", find:"추천의향",           label:"지인 추천 의향"}
];
const SCALE = [
  {label:"매우만족", score:5}, {label:"만족", score:4}, {label:"보통", score:3},
  {label:"불만족", score:2},  {label:"매우불만족", score:1}
];
function scoreOf(v){
  const t = String(v||"").replace(/\\s+/g,"");
  if(!t) return null;
  if(/^[1-5]$/.test(t)) return +t;
  // '매우불만족'이 '불만족'을 포함하므로 긴 보기부터 맞춘다.
  for(const s of [...SCALE].sort((a,b)=>b.label.length-a.label.length)){
    if(t.includes(s.label)) return s.score;
  }
  return null;
}
/* 구글 폼 복수선택은 ', '로 이어 붙는데 부스 이름 자체에도 쉼표가 있다.
   보기는 모두 '기업명_직무' 꼴이라, '_' 없는 조각은 앞 항목에 되붙인다. */
function splitBooths(v){
  const parts = String(v||"").split(/,\\s*/).filter(Boolean);
  const out = [];
  for(const p of parts){
    if(p.includes("_") || !out.length) out.push(p);
    else out[out.length-1] += ", " + p;
  }
  return out.map(x=>x.trim()).filter(Boolean);
}
function parseSat(input){
  const rows = Array.isArray(input) ? input : toRows(input);
  if(rows.length < 2) return [];
  const head = rows[0], find = colFinder(head);
  const C = {
    ts: find("타임스탬프"), name: find("이름"), sid: find("학번"),
    dept: find("학부"), grade: find("학년"), sex: find("성별"),
    booth: find("가장좋았던부스"), why: find("그이유는"), free: find("참여소감")
  };
  SAT_Q.forEach(q => { C[q.key] = find(q.find); });
  const out = [];
  for(const r of rows.slice(1)){
    const ts = parseTs(at(r,C.ts));
    if(!ts) continue;
    const rec = {
      ts, name: at(r,C.name), sid: at(r,C.sid), dept: at(r,C.dept) || "―",
      grade: at(r,C.grade) || "―", sex: at(r,C.sex) || "―",
      booths: splitBooths(at(r,C.booth)),
      why: at(r,C.why), free: at(r,C.free)
    };
    SAT_Q.forEach(q => {
      rec[q.key] = at(r,C[q.key]);
      rec[q.key+"_s"] = scoreOf(rec[q.key]);
    });
    out.push(rec);
  }
  return out.sort((a,b)=>b.ts-a.ts);
}""")

# ─────────── 5. 만족도 상세 섹션 HTML ───────────
cut("""  <section class="band">
    <div class="band-head">
      <h2>참여자 명단</h2>""",
"""  <section class="band">
    <div class="band-head">
      <h2>만족도 문항별 결과</h2>
      <span class="note" id="satScoreNote"></span>
      <span class="rule"></span>
    </div>
    <div class="kpis" id="satKpis"></div>
    <div class="grid two" style="margin-top:14px">
      <div class="panel"><h3>전반적 만족도 분포</h3><div class="bars" id="distQ1"></div></div>
      <div class="panel"><h3>주제·내용 적합성 분포</h3><div class="bars" id="distQ2"></div></div>
      <div class="panel"><h3>강사 만족도 분포</h3><div class="bars" id="distQ3"></div></div>
      <div class="panel"><h3>지인 추천 의향 분포</h3><div class="bars" id="distQ4"></div></div>
      <div class="panel" style="grid-column:1/-1">
        <h3>가장 좋았던 부스</h3>
        <p class="cap">복수 선택 · 선택 횟수 기준</p>
        <div class="bars" id="distBooth"></div>
      </div>
      <div class="panel"><h3>응답자 학부·전공 상위 8</h3><div class="bars" id="distSatDept"></div></div>
      <div class="panel"><h3>응답자 학년</h3><div class="bars" id="distSatGrade"></div></div>
    </div>
  </section>

  <section class="band">
    <div class="band-head">
      <h2>참여 소감 · 주관식 응답</h2>
      <span class="note" id="freeNote"></span>
      <span class="rule"></span>
    </div>
    <div class="panel"><div id="freeList"></div></div>
  </section>

  <section class="band">
    <div class="band-head">
      <h2>참여자 명단</h2>""")

# ─────────── 6. 만족도 상세 렌더 ───────────
cut("""  renderRoster(reg);
  document.getElementById("satNote").textContent =
    sat.length ? sat.length + "명 응답" : "응답 없음";""",
"""  renderRoster(reg);
  renderSatDetail(sat);
  document.getElementById("satNote").textContent =
    sat.length ? sat.length + "명 응답" : "응답 없음";""")

cut("""function renderStatus(){""",
"""function renderSatDetail(sat){
  // 문항별 평균 — 척도로 읽히는 응답만 계산에 넣는다.
  const tiles = SAT_Q.map(q=>{
    const vals = sat.map(r=>r[q.key+"_s"]).filter(v=>v!=null);
    const avg = vals.length ? (vals.reduce((a,b)=>a+b,0)/vals.length) : null;
    const good = vals.filter(v=>v>=4).length;
    return [q.label, avg==null ? "―" : avg.toFixed(2), avg==null ? "" : "/5",
            vals.length ? "긍정 " + Math.round(good/vals.length*100) + "% · " + vals.length + "명" : "응답 없음"];
  });
  document.getElementById("satKpis").innerHTML = tiles.map(t=>`
    <div class="kpi">
      <div class="k-lab">${esc(t[0])}</div>
      <div class="k-val num">${esc(t[1])}<span class="unit">${esc(t[2])}</span></div>
      <div class="k-sub">${esc(t[3])}</div>
    </div>`).join("");

  const allVals = sat.flatMap(r=>SAT_Q.map(q=>r[q.key+"_s"]).filter(v=>v!=null));
  document.getElementById("satScoreNote").textContent = allVals.length
    ? "4개 문항 종합 평균 " + (allVals.reduce((a,b)=>a+b,0)/allVals.length).toFixed(2) + "점 / 5점"
    : "척도 응답 없음";

  // 분포는 보기 순서(매우만족→매우불만족)를 지켜서 보여준다.
  SAT_Q.forEach((q,i)=>{
    const counts = new Map();
    sat.forEach(r=>{ const v=(r[q.key]||"").trim(); if(v) counts.set(v,(counts.get(v)||0)+1); });
    const ordered = SCALE.map(s=>[s.label, counts.get(s.label)||0]).filter(p=>p[1]>0);
    const extra = [...counts.entries()].filter(([k])=>!SCALE.some(s=>s.label===k));
    const total = sat.filter(r=>(r[q.key]||"").trim()).length;
    renderBars("distQ"+(i+1), ordered.concat(extra), total);
  });

  const boothCounts = new Map();
  sat.forEach(r=>r.booths.forEach(b=>boothCounts.set(b,(boothCounts.get(b)||0)+1)));
  const booths = [...boothCounts.entries()].sort((a,b)=>b[1]-a[1]);
  renderBars("distBooth", booths, sat.length);
  renderBars("distSatDept", tally(sat,"dept").slice(0,8), sat.length);
  renderBars("distSatGrade", tally(sat,"grade"), sat.length);

  // 주관식: 부스 선택 이유와 참여 소감을 한 줄씩
  const notes = [];
  sat.forEach(r=>{
    if(r.why)  notes.push({ts:r.ts, kind:"부스 선택 이유", who:r.dept, text:r.why});
    if(r.free) notes.push({ts:r.ts, kind:"참여 소감",      who:r.dept, text:r.free});
  });
  const host = document.getElementById("freeList");
  document.getElementById("freeNote").textContent = notes.length ? notes.length + "건" : "응답 없음";
  host.innerHTML = notes.length ? notes.map(n=>`
    <div class="bar-row" style="align-items:flex-start;gap:12px">
      <span class="b-lab" style="width:150px;flex:none">
        <span class="tag${n.kind==="참여 소감"?" alt":""}">${esc(n.kind)}</span>
        <span class="mono" style="font-size:11px"> ${esc(hhmm(n.ts))}</span>
      </span>
      <span style="flex:1;white-space:pre-wrap;line-height:1.65">${esc(n.text)}
        <span style="color:var(--line-2)"> — ${esc(n.who)}</span></span>
    </div>`).join("") : '<div class="empty">주관식 응답이 아직 없습니다.</div>';
}

function renderStatus(){""")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("생성:", OUT, len(s), "bytes")
