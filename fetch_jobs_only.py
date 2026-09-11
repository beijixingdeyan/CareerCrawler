import requests, json, time, math, pathlib
BASE="https://jy.hnust.edu.cn"
H={"User-Agent":"Mozilla/5.0"}
def get_total():
    r=requests.get(f"{BASE}/module/getjobs?is_total=1&start=0&count=0&type_id=-1&k=&is_practice=0&about_major=&city_name=%E5%85%A8%E9%83%A8&degree_require=&salary_max=&salary_min=&industry=&property=&scale=", headers=H, timeout=15)
    return int(r.text.strip())
total=get_total()
print("total",total)
# fetch with count 15
all_items=[]
count=15
pages= math.ceil(500/count)  # limit to 500 due to API window
for page in range(1, pages+1):
    start=(page-1)*count+1
    url=f"{BASE}/module/getjobs?start_page={page}&type_id=-1&k=&is_practice=0&about_major=&city_name=%E5%85%A8%E9%83%A8&degree_require=&salary_max=&salary_min=&industry=&property=&scale=&count={count}&start={start}&_={int(time.time()*1000)}"
    r=requests.get(url, headers=H, timeout=15)
    j=r.json()
    data=j.get("data",[])
    print(f"page {page} -> {len(data)}")
    all_items.extend(data)
    time.sleep(0.3)
    if len(data)==0:
        break
print(f"fetched {len(all_items)}")
# fetch intern as well
for page in range(1, pages+1):
    start=(page-1)*count+1
    url=f"{BASE}/module/getjobs?start_page={page}&type_id=-1&k=&is_practice=1&about_major=&city_name=%E5%85%A8%E9%83%A8&degree_require=&salary_max=&salary_min=&industry=&property=&scale=&count={count}&start={start}&_={int(time.time()*1000)}"
    r=requests.get(url, headers=H, timeout=15)
    j=r.json()
    data=j.get("data",[])
    print(f"intern page {page} -> {len(data)}")
    all_items.extend(data)
    time.sleep(0.3)
    if len(data)==0:
        break
print(f"total with intern {len(all_items)}")
pathlib.Path("data/real/jobs_full.json").write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved")
