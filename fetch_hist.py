import json, time, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# code: (name, start_ym, end_ym)
STOCKS = {
    "3008": ("大立光", 2013, 1, 2016, 12),   # 2014 iPhone 6 鏡頭超級循環
    "2408": ("南亞科", 2016, 1, 2019, 12),   # 2017-18 記憶體超級循環 → 2019 崩
    "2327": ("國巨",   2016, 6, 2019, 12),   # 2017-18 被動元件缺貨循環 → 2019 崩
    "2377": ("微星",   2019, 6, 2023, 12),   # 2020-21 疫情 PC/電競榮景 → 2022-23 去化
}

def months(y0,m0,y1,m1):
    out=[]; y,m=y0,m0
    while (y<y1) or (y==y1 and m<=m1):
        out.append(f"{y}{m:02d}01")
        m+=1
        if m>12: m=1; y+=1
    return out

def roc_to_iso(s):
    p=s.split("/"); return f"{1911+int(p[0])}-{int(p[1]):02d}-{int(p[2]):02d}"

out={}
for code,(name,y0,m0,y1,m1) in STOCKS.items():
    series=[]
    for ym in months(y0,m0,y1,m1):
        url=f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={ym}&stockNo={code}"
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=25,context=ctx) as r:
                j=json.loads(r.read().decode("utf-8"))
            if j.get("stat")=="OK" and j.get("data"):
                for row in j["data"]:
                    try: series.append([roc_to_iso(row[0]), float(row[6].replace(",",""))])
                    except ValueError: pass
        except Exception as e:
            print(f"{code} {ym} ERR {e}",flush=True)
        time.sleep(0.45)
    out[code]={"name":name,"series":series}
    print(f"== {code} {name}: {len(series)} pts {series[0] if series else '-'} .. {series[-1] if series else '-'} ==",flush=True)

with open("hist_data.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False)
print("DONE",flush=True)
