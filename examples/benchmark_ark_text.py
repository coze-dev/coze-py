import asyncio
import os
import time
from typing import List


def get_current_time_ms():
    return int(time.time() * 1000)


def cal_latency(current: int, latency_list: List[int]) -> str:
    if latency_list is None or len(latency_list) == 0:
        return "No latency data"
    if len(latency_list) == 1:
        return f"P99={latency_list[0]}ms, P90={latency_list[0]}ms, AVG={latency_list[0]}ms"

    # 对延迟数据进行排序
    sorted_latency = sorted(latency_list)
    length = len(sorted_latency)

    def fix_index(index):
        if index < 0:
            return 0
        if index >= length:
            return length - 1
        return index

    # 计算 P99
    p99_index = fix_index(round(length * 0.99) - 1)
    p99 = sorted_latency[p99_index]

    # 计算 P90
    p90_index = fix_index(round(length * 0.90) - 1)
    p90 = sorted_latency[p90_index]

    # 计算平均值
    avg = sum(sorted_latency) / length

    return f"P99={p99}ms, P90={p90}ms, AVG={avg:.2f}ms, CURRENT={current}ms"


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
            return (
                stream.response.headers["x-request-id"],
                chunk.choices[0].delta.content,
                get_current_time_ms() - start,
            )


async def main():
    ep = os.getenv("ARK_EP")
    token = os.getenv("ARK_TOKEN")
    text = os.getenv("COZE_TEXT") or "讲个笑话"

    times = 100
    text_latency = []
    for i in range(times):
        logid, first_text, latency = test_latency(ep, token, text)
        text_latency.append(latency)
        print(
            f"[latency.ark.text] {i}, latency: {cal_latency(latency, text_latency)}, log: {logid}, text: {first_text}"
        )


if __name__ == "__main__":
    asyncio.run(main())
