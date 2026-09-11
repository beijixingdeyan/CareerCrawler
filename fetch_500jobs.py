import requests, json, time, pathlib
BASE="https://jy.hnust.edu.cn"
H={"User-Agent":"Mozilla/5.0","X-Requested-With":"XMLHttpRequest"}
def fetch_prac(prac):
    items=[]
    for page in range(1, 35):
        start=(page-1)*15+1
        url=f"{BASE}/module/getjobs?start_page={page}&type_id=-1&k=&is_practice={prac}&about_major=&city_name=%E5%85%A8%E9%83%A8&degree_require=&salary_max=&salary_min=&industry=&property=&scale=&count=15&start={start}&_={int(time.time()*1000)}"
        r=requests.get(url, headers=H, timeout=15)
        j=r.json()
        data=j.get("data",[])
        print(f"prac {prac} page {page} -> {len(data)}")
        if not data:
            break
        items.extend(data)
        time.sleep(0.35)
        if len(items)>=500:
            break
    return items[:500]

official=fetch_prac(0)
print(f"official {len(official)}")
intern=fetch_prac(1)
print(f"intern {len(intern)}")
all_items=official+intern
# normalize
norm=[]
for x in official:
    norm.append({"source":"正式岗位","source_type":"jobs_official","publish_id":x.get("publish_id"),"title":x.get("job_name"),"company_name":x.get("company_name"),"city_name":x.get("city_name"),"salary":x.get("salary"),"salary_min":x.get("salary_min"),"salary_max":x.get("salary_max"),"publish_time":x.get("publish_time"),"raw":x})
for x in intern:
    norm.append({"source":"实习岗位","source_type":"jobs_intern","publish_id":x.get("publish_id"),"title":x.get("job_name"),"company_name":x.get("company_name"),"city_name":x.get("city_name"),"salary":x.get("salary"),"salary_min":x.get("salary_min"),"salary_max":x.get("salary_max"),"publish_time":x.get("publish_time"),"raw":x})
pathlib.Path("data/real/jobs.json").write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
pathlib.Path("data/real/jobs_raw.json").write_text(json.dumps(official+intern, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"saved {len(norm)}")
