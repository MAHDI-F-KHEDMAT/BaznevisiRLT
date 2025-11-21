# -*- coding: utf-8 -*-

import requests
import os
import re
import base64
import threading
import concurrent.futures
import socket
import time
import random
import statistics
import sys
import logging
from typing import List, Dict, Tuple, Optional, Set, Union

# --- پیکربندی اولیه لاگ (Logging) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s', # فرمت ساده‌تر برای خوانایی
    datefmt='%H:%M:%S',
    stream=sys.stdout
)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# --- ثابت‌های سراسری و پیکربندی ---
PRINT_LOCK = threading.Lock() # این قفل فقط برای نوار پیشرفت استفاده می‌شود

OUTPUT_DIR = "data"
CONFIG_URLS: List[str] = [
        "https://raw.githubusercontent.com/itsyebekhe/PSG/main/subscriptions/xray/base64/mix",
"https://raw.githubusercontent.com/Leon406/SubCrawler/refs/heads/main/sub/share/vless",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/soliSpirit/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/psgV6/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/psgMix/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/parvinXs/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/matinGh/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/mahsaXray/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/hamedP/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/gameFssociety/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/darkProxy/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/daniSamadi/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/code3Vless/normal",
"https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/amirAlter/normal",
"https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector_Py/refs/heads/main/sub/Mix/mix.txt",
"https://raw.githubusercontent.com/T3stAcc/V2Ray/refs/heads/main/Splitted-By-Protocol/vless.txt",
"https://raw.githubusercontent.com/F0rc3Run/F0rc3Run/refs/heads/main/splitted-by-protocol/vless.txt",
"https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt",
"https://raw.githubusercontent.com/LalatinaHub/Mineral/refs/heads/master/result/nodes",
"https://raw.githubusercontent.com/Flikify/Free-Node/refs/heads/main/v2ray.txt",
"https://raw.githubusercontent.com/barry-far/V2ray-Config/refs/heads/main/All_Configs_Sub.txt",
"https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/refs/heads/main/sub/vless.txt",
"https://raw.githubusercontent.com/iboxz/free-v2ray-collector/refs/heads/main/main/vless",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/vless.txt",
"https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/vless_configs.txt",
"https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/refs/heads/main/v2ray_configs.txt",
"https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/refs/heads/main/category/vless.txt",
"https://raw.githubusercontent.com/dream4network/telegram-configs-collector/refs/heads/main/protocols/vless",
"https://raw.githubusercontent.com/Pasimand/v2ray-config-agg/refs/heads/main/config.txt",
"https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/vless.html",
"https://raw.githubusercontent.com/xyfqzy/free-nodes/refs/heads/main/nodes/vless.txt",
"https://raw.githubusercontent.com/Leon406/SubCrawler/refs/heads/main/sub/share/vless",
"https://raw.githubusercontent.com/Kolandone/v2raycollector/refs/heads/main/vless.txt",
"https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/14.txt",
"https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/22.txt",
"https://raw.githubusercontent.com/Awmiroosen/awmirx-v2ray/refs/heads/main/blob/main/v2-sub.txt",
"https://raw.githubusercontent.com/Argh94/V2RayAutoConfig/refs/heads/main/configs/Vless.txt",
"https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/refs/heads/main/Protocols/vless.txt",
"https://raw.githubusercontent.com/RaitonRed/ConfigsHub/refs/heads/main/Splitted-By-Protocol/vless.txt",
"https://media.githubusercontent.com/media/gfpcom/free-proxy-list/refs/heads/main/list/vless.txt",
"https://raw.githubusercontent.com/MAHDI-F-KHEDMAT/KHANEVADEGI/refs/heads/main/data/khanevadeh_base64.txt",
"https://raw.githubusercontent.com/crackbest/V2ray-Config/refs/heads/main/config.txt",
"https://raw.githubusercontent.com/barry-far/V2ray-Config/refs/heads/main/Splitted-By-Protocol/vless.txt",
"https://raw.githubusercontent.com/giromo/Xrey-collector/refs/heads/main/All_Configs_Sub.txt",
"https://raw.githubusercontent.com/dream4network/telegram-configs-collector/refs/heads/main/splitted/mixed",
"https://raw.githubusercontent.com/Matin-RK0/ConfigCollector/refs/heads/main/subscription.txt"
]
OUTPUT_FILENAME: str = os.getenv("REALITY_OUTPUT_FILENAME", "khanevadeh") + "_base64.txt"

# --- زمان‌بندی‌ها و محدودیت‌ها ---
REQUEST_TIMEOUT: int = 15
FETCH_RETRIES: int = 4          # بهبود یافته: تعداد تلاش برای دریافت لینک‌ها
TCP_CONNECT_TIMEOUT: int = 5
NUM_TCP_TESTS: int = 11
MIN_SUCCESSFUL_TESTS_RATIO: float = 0.7
QUICK_CHECK_TIMEOUT: int = 2
MAX_CONFIGS_TO_TEST: int = 990000
# محدودیت تعداد کانفیگ خروجی نهایی حذف شد


# --- الگوهای Regex ---
SECURITY_KEYWORD: str = 'security=reality'
VLESS_PARSE_PATTERN: re.Pattern = re.compile(
    r"""
    vless://
    (?P<uuid>[a-f0-9\-]+)      # UUID
    @
    (?P<server>[^:]+)          # Server Address (can be domain or IP)
    :
    (?P<port>\d+)              # Port
    \?
    .*?                        # تمام پارامترهای دیگر (non-greedy)
    security=reality           # پارامتر کلیدی
    .*?                        # تمام پارامترهای دیگر
    pbk=(?P<pbk>[^&#]+)       # Public Key
    .*?                        # تمام پارامترهای دیگر
    (?:fp=(?P<fp>[^&#]+))?     # Fingerprint (اختیاری)
    """,
    re.IGNORECASE | re.VERBOSE
)
SEEN_IDENTIFIERS: Set[Tuple[str, int, str]] = set()

# --- توابع کمکی ---
def print_progress(iteration: int, total: int, prefix: str = '', suffix: str = '', bar_length: int = 50) -> None:
    """یک نوار پیشرفت در کنسول چاپ می‌کند."""
    with PRINT_LOCK:
        percent_str = f"{100 * (iteration / float(total)):.1f}"
        filled_length = int(bar_length * iteration // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent_str}% {suffix}')
        sys.stdout.flush()
        if iteration == total:
            sys.stdout.write('\n')

def parse_vless_config(config_str: str) -> Optional[Dict[str, Union[str, int]]]:
    """یک رشته کانفیگ VLESS Reality را پارس کرده و اجزای کلیدی آن را برمی‌گرداند."""
    match = VLESS_PARSE_PATTERN.search(config_str)
    if match:
        parts = match.groupdict()
        if all(parts.get(k) for k in ["uuid", "server", "port", "pbk"]):
            try:
                return {
                    "uuid": parts["uuid"],
                    "server": parts["server"],
                    "port": int(parts["port"]),
                    "pbk": parts["pbk"],
                    "fp": parts.get("fp") or "",
                    "original_config": config_str
                }
            except (ValueError, TypeError):
                return None
    return None

def is_base64_content(s: str) -> bool:
    """بررسی می‌کند که آیا رشته ورودی Base64 است یا خیر."""
    if not isinstance(s, str) or len(s.strip()) % 4 != 0:
        return False
    if not re.fullmatch(r"^[A-Za-z0-9+/=\s]+$", s.strip()):
        return False
    try:
        base64.b64decode(s, validate=True)
        return True
    except (base64.binascii.Error, UnicodeDecodeError):
        return False

# --- توابع اصلی برنامه ---
def fetch_subscription_content(url: str) -> Optional[str]:
    """محتوای یک URL را با منطق تلاش مجدد دریافت می‌کند."""
    for attempt in range(FETCH_RETRIES):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            logging.warning(f"تلاش {attempt + 1}/{FETCH_RETRIES} برای {url} ناموفق بود: {type(e).__name__}")
            time.sleep(1)
    logging.error(f"دریافت محتوا از {url} پس از {FETCH_RETRIES} تلاش ناموفق بود.")
    return None

def process_subscription_content(content: str, source_url: str) -> List[Dict[str, Union[str, int]]]:
    """محتوای سابسکریپشن را پردازش کرده و کانفیگ‌های VLESS Reality را استخراج می‌کند."""
    if not content:
        return []

    if is_base64_content(content):
        try:
            content = base64.b64decode(content).decode('utf-8')
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            logging.warning(f"⚠️ خطای دیکد Base64 برای {source_url}: {e}")
            return []

    valid_configs: List[Dict[str, Union[str, int]]] = []
    for line in content.splitlines():
        if SECURITY_KEYWORD in line and line.strip().startswith("vless://"):
            parsed_data = parse_vless_config(line.strip())
            if parsed_data:
                identifier = (parsed_data["server"], parsed_data["port"], parsed_data["uuid"])
                if identifier not in SEEN_IDENTIFIERS:
                    SEEN_IDENTIFIERS.add(identifier)
                    valid_configs.append(parsed_data)
    return valid_configs

def gather_configurations(links: List[str]) -> List[Dict[str, Union[str, int]]]:
    """کانفیگ‌های یکتای VLESS Reality را از لیستی از لینک‌ها جمع‌آوری می‌کند."""
    logging.info("🚀 مرحله ۱/۳: دریافت و پردازش کانفیگ‌ها...")
    all_configs: List[Dict[str, Union[str, int]]] = []
    total_links = len(links)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_subscription_content, url): url for url in links}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
            url = future_to_url[future]
            content = future.result()
            if content:
                configs = process_subscription_content(content, url)
                all_configs.extend(configs)
            print_progress(i + 1, total_links, prefix='دریافت و پردازش:', suffix='کامل شد')

    logging.info(f"✨ {len(all_configs)} کانفیگ یکتا (بر اساس منطق v2rayNG) جمع‌آوری شد.")
    return all_configs

def test_tcp_latency(host: str, port: int, timeout: int) -> Optional[float]:
    """اتصال TCP به هاست و پورت را تست کرده و در صورت موفقیت، تأخیر را به میلی‌ثانیه برمی‌گرداند."""
    start_time = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - start_time) * 1000
    except Exception:
        return None

def quick_tcp_check(config: Dict[str, Union[str, int]]) -> Optional[Dict[str, Union[str, int]]]:
    """یک تست سریع TCP انجام می‌دهد. در صورت موفقیت، کانفیگ را برمی‌گرداند."""
    if test_tcp_latency(str(config['server']), int(config['port']), QUICK_CHECK_TIMEOUT) is not None:
        return config
    return None

def measure_quality_metrics(config: Dict[str, Union[str, int]]) -> Optional[Dict[str, Union[str, int, float]]]:
    """میانگین تأخیر و جیتر را برای یک کانفیگ اندازه‌گیری می‌کند."""
    latencies: List[float] = []
    for _ in range(NUM_TCP_TESTS):
        latency = test_tcp_latency(str(config['server']), int(config['port']), TCP_CONNECT_TIMEOUT)
        if latency is not None:
            latencies.append(latency)
        time.sleep(0.1)

    if len(latencies) < (NUM_TCP_TESTS * MIN_SUCCESSFUL_TESTS_RATIO):
        return None

    latencies.sort()
    # حذف داده‌های پرت (Outliers) برای دقت بیشتر
    num_outliers_to_remove = min(2, len(latencies) // 3)
    trimmed_latencies = latencies[num_outliers_to_remove : -num_outliers_to_remove] if len(latencies) > 4 else latencies
    if not trimmed_latencies:
        return None

    avg_latency = statistics.mean(trimmed_latencies)
    jitter = statistics.stdev(trimmed_latencies) if len(trimmed_latencies) > 1 else 0
    
    config_with_quality = config.copy()
    config_with_quality['latency_ms'] = avg_latency
    config_with_quality['jitter_ms'] = jitter
    return config_with_quality

def evaluate_and_sort_configs(configs: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int, float]]]:
    """کیفیت کانفیگ‌ها را در دو مرحله ارزیابی کرده و آنها را بر اساس کیفیت مرتب می‌کند."""
    logging.info("\n🔍 مرحله ۲/۳: انجام تست سریع TCP (Fast Fail) برای کانفیگ‌ها...")
    configs_to_process = configs[:MAX_CONFIGS_TO_TEST]
    
    max_workers = min(32, (os.cpu_count() or 1) + 4)
    passed_quick_check: List[Dict[str, Union[str, int]]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_cfg = {executor.submit(quick_tcp_check, cfg): cfg for cfg in configs_to_process}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_cfg)):
            if future.result():
                passed_quick_check.append(future.result())
            print_progress(i + 1, len(configs_to_process), prefix='تست سریع:', suffix='کامل شد')

    logging.info(f"✅ {len(passed_quick_check)} کانفیگ تست سریع را با موفقیت گذراندند.")
    if not passed_quick_check:
        return []

    logging.info("\n🔍 مرحله ۳/۳: انجام تست کیفیت کامل (TCP Ping & Jitter) برای کانفیگ‌های سالم...")
    evaluated_configs: List[Dict[str, Union[str, int, float]]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_cfg = {executor.submit(measure_quality_metrics, cfg): cfg for cfg in passed_quick_check}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_cfg)):
            if future.result():
                evaluated_configs.append(future.result())
            print_progress(i + 1, len(passed_quick_check), prefix='تست کامل:', suffix='کامل شد')

    logging.info(f"✅ {len(evaluated_configs)} کانفیگ تست کیفیت کامل را با موفقیت گذراندند.")
    
    # مرتب‌سازی بر اساس جیتر و سپس تأخیر
    evaluated_configs.sort(key=lambda x: (x.get('jitter_ms', 999), x.get('latency_ms', 999)))
    return evaluated_configs

def save_results_base64(configs: List[Dict[str, Union[str, int, float]]]) -> None:
    """کانفیگ‌های ارزیابی‌شده را به ترتیب کیفیت در یک فایل Base64 ذخیره می‌کند."""
    if not configs:
        logging.info("\n😥 هیچ کانفیگ فعالی برای ذخیره یافت نشد.")
        return

    # تمام کانفیگ‌های ارزیابی‌شده را انتخاب می‌کند (بدون محدودیت)
    final_output_configs = configs 
    
    final_configs_list = []
    for i, cfg in enumerate(final_output_configs, start=1):
        # حذف نام قبلی و اضافه کردن شماره جدید
        config_without_comment = re.sub(r'#.*$', '', str(cfg['original_config'])).strip()
        # شماره‌گذاری جدید: #1، #2، #3، ...
        numbered_config = f"{config_without_comment}#{i}" 
        final_configs_list.append(numbered_config)
    
    subscription_text = "\n".join(final_configs_list)
    base64_sub = base64.b64encode(subscription_text.encode('utf-8')).decode('utf-8')
    
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(base64_sub)
        logging.info(f"\n🎉 {len(final_output_configs)} کانفیگ با شماره‌گذاری ساده در فایل ذخیره شد: {output_path}") 
        
        logging.info("🏆 ۵ کانفیگ برتر (بر اساس جیتر و تأخیر):")
        # نمایش 5 کانفیگ برتر از کل لیست
        for i, cfg in enumerate(final_output_configs[:5], start=1): 
            logging.info(
                f"  {i}. {cfg['server']}:{cfg['port']} - "
                f"تاخیر: {cfg.get('latency_ms', 0):.2f}ms, "
                f"جیتر: {cfg.get('jitter_ms', 0):.2f}ms"
            )
    except IOError as e:
        logging.error(f"❌ خطا در ذخیره فایل به {output_path}: {e}")

# --- نقطه ورود اصلی برنامه ---
def main() -> None:
    """تابع اصلی برای هماهنگی تمام مراحل."""
    start_time = time.time()
    
    all_unique_configs = gather_configurations(CONFIG_URLS)
    evaluated_and_sorted_configs = evaluate_and_sort_configs(all_unique_configs)
    
    if evaluated_and_sorted_configs:
        save_results_base64(evaluated_and_sorted_configs)
    else:
        logging.info("\n🚫 هیچ کانفیگ فعالی برای ارزیابی و ذخیره یافت نشد.")
    
    elapsed = time.time() - start_time
    logging.info(f"⏱️ کل زمان اجرا: {elapsed:.2f} ثانیه")

if __name__ == "__main__":
    main()
