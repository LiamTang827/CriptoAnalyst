import requests
import time

API_KEY = "CYMZu1iaH66gTyOJbBe9lOnHy5LrPGjH"
QUERY_ID = "6806719"
headers = {"X-Dune-API-Key": API_KEY}

# 执行查询
resp = requests.post(
    f"https://api.dune.com/api/v1/query/{QUERY_ID}/execute",
    headers=headers
)
execution_id = resp.json()["execution_id"]
print(f"执行中: {execution_id}")

# 等待完成
while True:
    status = requests.get(
        f"https://api.dune.com/api/v1/execution/{execution_id}/status",
        headers=headers
    ).json()
    print(f"状态: {status['state']}")
    if status["state"] == "QUERY_STATE_COMPLETED":
        break
    time.sleep(3)

# 拿全量数据（分页）
all_rows = []
offset = 0
limit = 1000

while True:
    resp = requests.get(
        f"https://api.dune.com/api/v1/execution/{execution_id}/results",
        headers=headers,
        params={"limit": limit, "offset": offset}
    ).json()
    
    rows = resp["result"]["rows"]
    all_rows.extend(rows)
    print(f"已获取: {len(all_rows)} 条")
    
    if len(rows) < limit:
        break
    offset += limit

# 保存 CSV
with open("usdt_blacklist.csv", "w") as f:
    f.write("address,time,chain\n")
    for row in all_rows:
        f.write(f"{row['_user']},{row['evt_block_time']},{row['chain']}\n")

print(f"完成，共 {len(all_rows)} 条，已保存 usdt_blacklist.csv")