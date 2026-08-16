import litellm
import os

print("litellm version:", litellm.version)
model = os.environ.get("LITELLM_MODEL", "")
base = os.environ.get("OPENAI_BASE_URL", "")
key = os.environ.get("OPENAI_API_KEY", "")
print("LITELLM_MODEL:", model)
print("BASE_URL:", base)
print("KEY ~:", (key[:6] + "...") if key else "(empty)")

print("== 1) non-stream, max_tokens=500 ==")
try:
    resp = litellm.completion(
        model=model,
        api_key=key,
        api_base=base,
        messages=[{"role": "user", "content": "请用中文回复: 你好，介绍一下你自己，50字以内。"}],
        max_tokens=500,
        stream=False,
    )
    content = resp.choices[0].message.content
    print("content type:", type(content), "len:", len(content or ""))
    print("content repr:", repr((content or "")[:200]))
    msg = resp.choices[0].message
    if hasattr(msg, "model_extra"):
        print("model_extra keys:", list((msg.model_extra or {}).keys()))
    print("full message dict:", dict(msg))
except Exception as e:
    print("FAIL:", type(e).__name__, str(e)[:800])

print("== 2) stream, max_tokens=500 ==")
try:
    resp = litellm.completion(
        model=model,
        api_key=key,
        api_base=base,
        messages=[{"role": "user", "content": "请用中文回复: 你好，介绍一下你自己，50字以内。"}],
        max_tokens=500,
        stream=True,
    )
    parts = []
    for chunk in resp:
        if chunk.choices and chunk.choices[0].delta:
            d = chunk.choices[0].delta
            if d.content:
                parts.append(d.content)
    print("stream 内容长度:", len("".join(parts)), "前100:", repr("".join(parts)[:100]))
except Exception as e:
    print("stream FAIL:", type(e).__name__, str(e)[:800])
