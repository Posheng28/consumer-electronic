import json, time, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

STOCKS = {
    "3661": "世芯-KY",
    "3008": "大立光",
    "3017": "奇鋐",
    "6854": "錼創",
    "2317": "鴻海",
    "2379": "瑞昱",
}

# months 2024-09 .. 2026-05
months = []
for y in (2024, 2025, 2026):
    for m in range(1, 13):
        if y == 2024 and m < 9: continue
        if y == 2026 and m > 5: continue
        months.append(f"{y}{m:02d}01")

def roc_to_iso(s):
    p = s.split("/")
    return f"{1911+int(p[0])}-{int(p[1]):02d}-{int(p[2]):02d}"

out = {}
for code, name in STOCKS.items():
    series = []
    for ym in months:
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={ym}&stockNo={code}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
                j = json.loads(r.read().decode("utf-8"))
            if j.get("stat") == "OK" and j.get("data"):
                for row in j["data"]:
                    d = roc_to_iso(row[0])
                    close = row[6].replace(",", "")
                    try:
                        series.append([d, float(close)])
                    except ValueError:
                        pass
            print(f"{code} {ym}: {len(j.get('data',[]))} rows", flush=True)
        except Exception as e:
            print(f"{code} {ym} ERR {e}", flush=True)
        time.sleep(0.5)
    out[code] = {"name": name, "series": series}
    print(f"== {code} {name}: {len(series)} points ==", flush=True)

with open("price_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print("DONE", flush=True)
