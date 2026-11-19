import json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__))
# 학년: --grade N (기본 6). 6학년은 옛 자리(tools/plan.json, tools/out), 나머지는 tools/gN/plan.json, tools/gN/out
G = int(sys.argv[sys.argv.index('--grade')+1]) if '--grade' in sys.argv else 6
BASE = S if G == 6 else os.path.join(S, f'g{G}')
OUT = os.path.join(S, '..', 'data', f'g{G}-2.js')
plan = json.load(open(os.path.join(BASE, 'plan.json'), encoding='utf-8'))
order = [k for k in plan.keys() if not k.startswith('_')]
SOURCE = plan.get('_source', f'2026학년도 2학기 {G}학년 평가 기본계획')
problems, subjects, allsent = [], [], {}
END = re.compile(r'(함|임|음|됨|짐|김|림|힘|봄|춤|움|냄|큼|줌|둠|씀|름|함\)|보임|뛰어남|돋보임|기대됨|나타남|드러남|높음|좋음|있음|없음|많음)\.$')
for subj in order:
    p = os.path.join(BASE, 'out', subj + '.json')
    if not os.path.exists(p):
        problems.append(f'{subj}: 파일 없음'); continue
    got = json.load(open(p, encoding='utf-8'))
    items = []
    for it in plan[subj]:
        v = got.get(it['code'])
        if not v:
            problems.append(f"{subj} {it['code']}: 없음"); continue
        lv = []
        for L in range(3):
            arr = [x.strip() for x in v.get(str(L), [])]
            if len(arr) != 10: problems.append(f"{subj} {it['code']} {L}: {len(arr)}개")
            heads = {}
            for x in arr:
                if not (x.endswith('.') and len(x)>1 and 0xAC00<=ord(x[-2])<=0xD7A3 and (ord(x[-2])-0xAC00)%28 in (16,10)): problems.append(f"{subj} {it['code']} {L} 끝말: {x[-12:]}")
                if not (30 <= len(x) <= 130): problems.append(f"{subj} {it['code']} {L} 길이 {len(x)}: {x[:20]}")
                h = x[:8]
                if h in heads: problems.append(f"{subj} {it['code']} {L} 첫머리 겹침: {h}")
                heads[h] = 1
                if x in allsent: problems.append(f"{subj} {it['code']} {L} 중복: {x[:25]}")
                allsent[x] = 1
                if L == 0 and '도움을 받아' in x: problems.append(f"{subj} {it['code']} ◎에 도움: {x[:25]}")
                if L == 2 and '뛰어' in x: problems.append(f"{subj} {it['code']} △에 뛰어남: {x[:25]}")
            lv.append(arr)
        items.append({'code': it['code'], 'area': it['area'], 'std': it['std'], 'c': it['c'], 'v': lv})
    subjects.append({'name': subj, 'items': items})
print('문장 수', len(allsent))
print('문제', len(problems)); print('\n'.join(problems[:80]))
if '--write' in sys.argv:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = {'title': f'{G}학년 2학기', 'grade': G, 'source': SOURCE, 'subjects': subjects}
    open(OUT, 'w', encoding='utf-8').write(f'(window.PY_ALL = window.PY_ALL || {{}})[{G}] = window.PY_DATA = ' + json.dumps(data, ensure_ascii=False, indent=0) + ';\n')
    print('저장', OUT)
