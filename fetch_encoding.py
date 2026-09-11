import requests, json
headers={"User-Agent":"Mozilla/5.0"}
url="https://jy.hnust.edu.cn/module/getcareers?start_page=1&k=&panel_name=&type=inner&day=&panel_id=&professionals=&work_city=&is_yun_career=&count=2&start=1"
r=requests.get(url, headers=headers, timeout=15)
print("encoding", r.encoding, r.apparent_encoding)
print("headers", r.headers.get('Content-Type'))
print("raw bytes start", r.content[:500])
# try decode
for enc in ['utf-8','gbk','gb2312','utf-8-sig']:
    try:
        t=r.content.decode(enc)
        print(f"--- {enc} ---", t[:800])
    except Exception as e:
        print(enc, e)
# try json
j=json.loads(r.content.decode('utf-8'))
print("company", j['data'][0]['company_name'])
