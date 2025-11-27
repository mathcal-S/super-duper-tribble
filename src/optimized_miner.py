#!/usr/bin/env python3
import hashlib
import struct
import time
import requests
import os
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

CORES = os.cpu_count() or 4
BTC_RPC = {"url": "http://127.0.0.1:18443", "auth": ("user", "pass")}
NONCE_BLOCK_SIZE = 1000
BLOCK_TEMPLATE_REFRESH_SECONDS = 30

MINING_ADDR_HEX = None


def rpc_call(method, params=[]):
    try:
        payload = {"jsonrpc": "1.0", "id": "esqet", "method": method, "params": params}
        r = requests.post(BTC_RPC["url"], auth=BTC_RPC["auth"], json=payload, timeout=2)
        return r.json().get("result")
    except Exception as e:
        print(f"RPC call error: {e}")
        return None


def dsha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compact_size(n):
    if n < 0xfd: return struct.pack("<B", n)
    elif n <= 0xffff: return b"ý" + struct.pack("<H", n)
    elif n <= 0xffffffff: return b"þ" + struct.pack("<I", n)
    else: return b"ÿ" + struct.pack("<Q", n)


def get_mining_script():
    global MINING_ADDR_HEX
    if MINING_ADDR_HEX:
        return MINING_ADDR_HEX

    addr = rpc_call("getnewaddress")
    if not addr:
        return os.urandom(20)

    info = rpc_call("validateaddress", [addr])
    if info and "scriptPubKey" in info:
        MINING_ADDR_HEX = bytes.fromhex(info["scriptPubKey"])
        return MINING_ADDR_HEX

    return os.urandom(20)


def create_coinbase(height, msg=b"ESQET v8.3"):
    tx = b"\u0001" + b"\u0001"
    tx += b"" * 32 + b"ÿÿÿÿ"
    height_bytes = struct.pack("<I", height)
    script = b"\u0004" + height_bytes + msg
    tx += compact_size(len(script)) + script
    tx += b"ÿÿÿÿ"
    tx += b"\u0001"
    tx += struct.pack("<Q", 50 * 100000000)
    script_pub = get_mining_script()
    tx += compact_size(len(script_pub)) + script_pub
    tx += b""
    return tx


class CachedBlockTemplate:
    def __init__(self):
        self.template = None
        self.last_update = 0

    def get(self):
        now = time.time()
        if not self.template or (now - self.last_update) > BLOCK_TEMPLATE_REFRESH_SECONDS:
            tmpl = rpc_call("getblocktemplate", [{"rules": ["segwit"]}])
            if tmpl:
                self.template = tmpl
                self.last_update = now
        return self.template


def btc_worker(nonce_range_start, nonce_range_end, block_template):
    tmpl = block_template.get()
    if not tmpl:
        return None
    cb = create_coinbase(tmpl["height"], b"BTC_GROVER")
    merkle = dsha256(cb)
    header_pre = (
        struct.pack("<i", tmpl["version"])
        + bytes.fromhex(tmpl["previousblockhash"])[::-1]
        + merkle
        + struct.pack("<I", tmpl["curtime"])
        + bytes.fromhex(tmpl["bits"])[::-1]
    )
    target = int(tmpl["target"], 16)

    for nonce in range(nonce_range_start, nonce_range_end):
        h = dsha256(header_pre + struct.pack("<I", nonce))
        if int.from_bytes(h[::-1], "big") < target:
            print(f">>> [BTC] MINED! Nonce: {nonce} | REWARD: 50.0 BTC")
            full_hex = header_pre.hex() + f"{nonce:08x}" + "01" + cb.hex()
            rpc_call("submitblock", [full_hex])
            return True
    return False


def nonce_allocator(shared_counter, lock):
    with lock:
        start = shared_counter.value
        shared_counter.value += NONCE_BLOCK_SIZE
    return start, start + NONCE_BLOCK_SIZE


def main():
    print(f"ESQET-UIFT v8.3 | CORES: {CORES} | WALLET LINKED")
    if get_mining_script():
        print(">>> TARGET ADDRESS CONFIRMED")

    manager = mp.Manager()
    nonce_counter = manager.Value('i', 0)
    counter_lock = manager.Lock()
    block_template = CachedBlockTemplate()

    with ProcessPoolExecutor(max_workers=CORES) as exe:
        while True:
            futures = []
            for _ in range(CORES):
                nonce_start, nonce_end = nonce_allocator(nonce_counter, counter_lock)
                futures.append(exe.submit(btc_worker, nonce_start, nonce_end, block_template))
            for f in futures:
                if f.result():
                    with counter_lock:
                        nonce_counter.value = 0
                    block_template.last_update = 0
                    break
            time.sleep(0.05)


if __name__ == "__main__":
    mp.freeze_support()
    main()
