from importlib.metadata import version
import litellm
import os
import time

print("litellm version:", version("litellm"))
model = os.environ.get("LITELLM_MODEL", "")
base = os.environ.get("OPENAI_BASE_URL", "")
key = os.environ.get("OPENAI_API_KEY", "")
print("LITELLM_MODEL:", model)

# 构造接近真实的超长 prompt
kline = []
for i in range(42):
    kline.append(f"日期:2026-0{i//8+6}-{i%28+1:02d} 开:{(9+i*0.1):.2f} 高:{(9.5+i*0.1):.2f} 低:{(8.8+i*0.1):.2f} 收:{(9.2+i*0.1):.2f} 量:{(1000000+i*10000)} 额:{(1000000000+i*10000000)} 振幅:{(0.5+i*0.1):.2f}% 涨跌幅:{(0.3+i*0.05):.2f}% 换手率:{(0.9+i*0.1):.2f}%")

system_prompt = """你是一位专业的A股分析助手。请严格按照JSON格式输出分析报告，包含字段：股票名称、股票代码、分析日期、趋势判断、支撑压力位、技术指标、风险提示、操作建议。""".strip()

prompt = f"""
请分析以下股票：
股票名称：中国铝业
股票代码：601600
分析日期：2026-08-16

【大盘背景】上证指数今日小幅震荡，成交额约8000亿，北向资金净流入。行业板块方面，有色金属涨幅居前，煤炭、钢铁跟涨。

【K线数据（近42个交易日）】
{'\n'.join(kline)}

【技术指标】MA5=9.30 MA10=9.25 MA20=9.10 MA60=8.80，MACD金叉，KDJ超买区，RSI=65。

【所属板块】有色金属、融资融券、沪股通、央企改革。

【近期消息】公司发布半年报预告，净利润同比增长30%。国际市场铝价上涨。

请从趋势判断、支撑压力位、技术指标解读、风险提示、操作建议五个维度给出分析，输出JSON格式。
""".strip()

print("prompt 长度:", len(prompt))

print("== 真实场景: non-stream max_tokens=8192 ==")
t0 = time.time()
try:
    resp = litellm.completion(
        model=model,
        api_key=key,
        api_base=base,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
        max_tokens=8192,
        temperature=0.7,
        stream=False,
    )
    content = resp.choices[0].message.content
    msg = resp.choices[0].message
    rc = getattr(msg, "reasoning_content", None) or ""
    print(f"耗时: {time.time()-t0:.1f}s")
    print("content len:", len(content or ""), "| reasoning len:", len(rc))
    print("content 前300:", repr((content or "")[:300]))
    finish = getattr(resp.choices[0], "finish_reason", None)
    print("finish_reason:", finish)
    usage = resp.usage
    print("usage:", usage)
except Exception as e:
    print(f"FAIL after {time.time()-t0:.1f}s:", type(e).__name__, str(e)[:600])

print("== 真实场景: stream max_tokens=8192 ==")
t0 = time.time()
try:
    resp = litellm.completion(
        model=model,
        api_key=key,
        api_base=base,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
        max_tokens=8192,
        temperature=0.7,
        stream=True,
        timeout=120,
    )
    parts = []
    for chunk in resp:
        if chunk.choices and chunk.choices[0].delta:
            d = chunk.choices[0].delta
            if d.content:
                parts.append(d.content)
    text = "".join(parts)
    print(f"耗时: {time.time()-t0:.1f}s, stream 内容长度: {len(text)}, 前200: {repr(text[:200])}")
except Exception as e:
    print(f"stream FAIL after {time.time()-t0:.1f}s:", type(e).__name__, str(e)[:600])
