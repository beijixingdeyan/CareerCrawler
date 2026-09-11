import requests, json, pathlib
from bs4 import BeautifulSoup
H={'User-Agent':'Mozilla/5.0'}
c=json.loads(pathlib.Path('data/real/careers.json').read_text(encoding='utf-8'))[0]
print(c.get('career_talk_id'), c.get('company_name'))
url=f"https://jy.hnust.edu.cn/detail/career?id={c.get('career_talk_id')}"
r=requests.get(url, headers=H, timeout=10)
r.encoding='utf-8'
print(r.status_code)
soup=BeautifulSoup(r.text,'lxml')
text=soup.get_text(separator='\n', strip=True)
print('has 单位简介', '单位简介' in text)
print('has 公司简介', '公司简介' in text)
print('has 企业简介', '企业简介' in text)
for mod in soup.select('.detail-module'):
  tit=mod.select_one('.dm-tit')
  if tit:
    t=tit.get_text(strip=True)
    print('section', t, mod.get_text(strip=True)[:120].replace('\n',' '))
with open('probe_career.html','w',encoding='utf-8') as f:
  f.write(r.text)
print('saved')
