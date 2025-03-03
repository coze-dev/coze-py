import asyncio
import os
import time
from typing import List


def get_current_time_ms():
    return int(time.time() * 1000)


def cal_latency(latency_list: List[int]) -> str:
    if latency_list is None or len(latency_list) == 0:
        return "0"
    if len(latency_list) == 1:
        return f"{latency_list[0]}"
    res = latency_list.copy()
    res.sort()
    return "%2d" % ((sum(res[:-1]) * 1.0) / (len(res) - 1))


def test_latency(ep: str, token: str, text: str):
    from volcenginesdkarkruntime import Ark

    client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=token)
    start = get_current_time_ms()
    stream = client.chat.completions.create(
        model=ep,
        messages=[
            {"role": "user", "content": text},
        ],
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue

        if chunk.choices[0].delta.content:
            return "", chunk.choices[0].delta.content, get_current_time_ms() - start


async def main():
    ep = os.getenv("ARK_EP")
    token = os.getenv("ARK_TOKEN")
    text = os.getenv("COZE_TEXT") or "讲个笑话"

    times = 50
    text_latency = []
    for i in range(times):
        logid, text, latency = test_latency(ep, token, text)
        text_latency.append(latency)
        print(f"[latency.ark.text] {i}, latency: {cal_latency(text_latency)} ms, log: {logid}, text: {text}")


if __name__ == "__main__":
    asyncio.run(main())
