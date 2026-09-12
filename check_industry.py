import json, pathlib, collections
data=json.loads(pathlib.Path('data/real/careers_enriched.json').read_text(encoding='utf-8'))
c=collections.Counter([x.get('enterprise_background',{}).get('industry') or x.get('industry') for x in data])
for k,v in c.most_common(15):
    print(f"{k}: {v}")
# also check jobfairs
try:
    import requests
    # check fair companies
    data2=json.loads(pathlib.Path('data/real/fair_30003.json').read_text(encoding='utf-8')) if pathlib.Path('data/real/fair_30003.json').exists() else []
    if data2:
        c2=collections.Counter([x.get('industry_category') for x in data2])
        print("fair 30003 industries:")
        for k,v in c2.most_common(10):
            print(f"{k}: {v}")
except Exception as e:
    print(e)
