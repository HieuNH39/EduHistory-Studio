"""Chạy tools/kling_prompts.py song song theo tập (mạng là nút thắt, không phải CPU)."""
import sys, os, glob
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__)); import kling_prompts as K
ids = [os.path.basename(p)[:-5] for p in sorted(glob.glob(f"{K.ROOT}/data/scripts/L*.json"))]
con = [m for m in ids if not os.path.exists(f"{K.ROOT}/data/kling/{m}.json")]
print("còn", len(con), "tập", flush=True)
with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as ex:
    for m, _ in zip(con, ex.map(K.main, con)): pass
print("XONG", flush=True)
