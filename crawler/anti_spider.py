"""
反爬策略中间件（requests 版）
提供：UA 轮换、随机延迟、退避重试、验证码检测
"""
import random
import time
from typing import Optional

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def random_delay(a=0.8, b=2.0):
    time.sleep(random.uniform(a, b))

def should_backoff(resp) -> bool:
    return resp.status_code in (429, 503, 504)

def is_captcha(text: str) -> bool:
    low = text.lower()
    return "验证码" in text or "captcha" in low or "人机验证" in text
