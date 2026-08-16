import litellm
import os

print("litellm version:", litellm.version)
model = os.environ.get("LITELLM_MODEL", "")
base = os.environ.get("OPENAI_BASE_URL", "")
key = os.environ.get("OPENAI_API_KEY", "")
print("LITELLM_MODEL:", model)
print("BASE_URL:", base)
print("KEY ~:", (key[:6] + "...") if key else "(empty)")

print("== 1) non-stream ==")
try:
    resp = litellm.completion(
        model=model,
        api_key=key,
        api_base=base,
        messages=[{"role": "user", "content": "回复OK两个字"}],
        max_tokens=50,
        stream=False,
    )
    content = resp.choices[0].message.content
    print("OK, len=", len(content or ""), "content=", repr((content or "")[:120]))
    print("finish_reason:", getattr(resp.choices[0], "finish_reason", None))
except Exception as e:
    print("FAIL:", type(e).__name__, str(e)[:800])

print("== 2) stream ==")
try:
    resp = litellm.completion(
        model=model,
        api_key=key,
        api_base=base,
        messages=[{"role": "user", "content": "回复OK两个字"}],
        max_tokens=50,
        stream=True,
    )
    parts = []
    for chunk in resp:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            parts.append(chunk.choices[0].delta.content)
    print("stream OK, len=", len("".join(parts)))
except Exception as e:
    print("stream FAIL:", type(e).__name__, str(e)[:800])
