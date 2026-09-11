import requests, json
headers={"User-Agent":"Mozilla/5.0"}
def fetch(url):
    r=requests.get(url, headers=headers, timeout=15)
    print(url, r.status_code, r.text[:2000])
    try:
        j=r.json()
        print("json keys", j.keys(), "code", j.get("code"), "data len", len(str(j.get("data"))), "data type", type(j.get("data")))
        if isinstance(j.get("data"), list):
            print("data len list", len(j["data"]))
        elif isinstance(j.get("data"), dict):
            print("data dict", j["data"])
        else:
            print("data", j["data"] and str(j["data"])[:500])
    except Exception as e:
        print("json err", e)

fetch("https://jy.hnust.edu.cn/module/getcareers?is_total=1&start=0&count=0&k=&panel_name=&type=inner&day=&panel_id=&professionals=&work_city=&is_yun_career=")
fetch("https://jy.hnust.edu.cn/module/getjobfairs?is_total=1&start=0&count=0&keyword=&panel_id=0&school_type=")
fetch("https://jy.hnust.edu.cn/module/getjobs?is_total=1&start=0&count=0&type_id=-1&k=&is_practice=0&about_major=&city_name=%E5%85%A8%E9%83%A8&degree_require=&salary_max=&salary_min=&industry=&property=&scale=")
# also try ordering
fetch("https://jy.hnust.edu.cn/module/getcareers?start_page=1&k=&panel_name=&type=inner&day=&panel_id=&professionals=&work_city=&is_yun_career=&count=15&start=1")
