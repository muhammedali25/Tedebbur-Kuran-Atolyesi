"""Hizalama ayarı: sözcük ağırlığı ve izin verilen grup boyutları.
Ölçüt yalnız âyet atıflı FA↔AK çiftleri (atıflar hizalamaya verilmez: dürüst ölçüm).
Hız için sözlük bir kez öğrenilir, denemeler yalnız altın çifti olan mektuplarda yapılır.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import *
import align_eval_core as E

D = sys.argv[1]
T, U, GOLD, ORDER = E.setup(D)
keys = [k for k in ORDER if GOLD[k]["ak"] or GOLD[k]["ar"]]
print("altın çifti olan mektup:", len(keys), flush=True)
t0 = time.time()
AL = {k: {"U": U[k], **{l: align(U[k]["fa"], U[k][l]) for l in ("ar", "ak", "hk") if U[k]["fa"] and U[k][l]}} for k in ORDER}
dics = {l: learn_dict(T, AL, l) for l in ("ar", "ak")}
print("uzunluk + sözlük hazır", int(time.time() - t0), "sn", flush=True)
AL2 = {}
for k in ORDER:
    AL2[k] = {"U": U[k]}
    for l in ("ar", "ak"):
        if U[k]["fa"] and U[k][l]: AL2[k][l] = align(U[k]["fa"], U[k][l], Sim(U[k]["fa"], U[k][l], l, dics[l]))
dics = {l: learn_dict(T, AL2, l) for l in ("ar", "ak")}
print("sözlük #2 hazır", int(time.time() - t0), "sn", flush=True)
for w in tuple(float(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["4", "6", "9", "13"])):
    for mv_name, mv in (("6'ya kadar", MV_X),):
        e = n = tot = 0
        for k in keys:
            if not GOLD[k]["ak"]: continue
            b = align(U[k]["fa"], U[k]["ak"], Sim(U[k]["fa"], U[k]["ak"], "ak", dics["ak"]), w_lex=w, moves=mv)
            x, y = E.score(b, GOLD[k]["ak"]); e += x; n += y; tot += len(GOLD[k]["ak"])
        print(f"  sözcük ağırlığı {w:4} · grup {mv_name:10}: FA↔AK tam %{100*e/tot:.1f} · ±1 %{100*n/tot:.1f}", flush=True)
