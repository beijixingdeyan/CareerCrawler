import json,pathlib
from collections import Counter
p=pathlib.Path('data/real/careers_enriched.json')
d=json.loads(p.read_text(encoding='utf-8'))
c=Counter([x.get('enterprise_background',{}).get('industry') for x in d])
industries=["制造业","教育","信息传输、软件和信息技术服务业","建筑业","批发和零售业","电力、热力、燃气及水生产和供应业","采矿业","科学研究和技术服务业","交通运输、仓储和邮政业","农、林、牧、渔业","住宿和餐饮业","文化、体育和娱乐业","金融业","水利、环境和公共设施管理业","公共管理、社会保障和社会组织","租赁和商务服务业"]
missing=[k for k in c if k not in industries]
print("missing:", missing)
print("missing sum:", sum(c[k] for k in missing))
for k,v in c.most_common():
    print(f"{k}: {v}")
