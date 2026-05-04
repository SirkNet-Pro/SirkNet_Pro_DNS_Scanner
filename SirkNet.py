#!/usr/bin/env python3
import asyncio
import dns.message
import dns.query
import dns.rdatatype
import dns.edns
import time
from typing import Tuple, List
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

console = Console()

TIMEOUT = 1.8

MAX_CONCURRENT_PHASE1 = 300
MAX_CONCURRENT_PHASE2 = 200
MAX_CONCURRENT_PHASE3 = 100
TEST_RETRIES_PHASE3 = 4
LARGE_QUERY_SIZE = 200
MAX_ACCEPTABLE_LOSS = 0
MAX_AVG_RTT_MS = 350

def banner():
    console.print(Panel.fit(
        "[bold cyan]SirkNet Pro Dns Scanner[/bold cyan]\n[white]Developed by APT IRAN[/white]\n\n[green]Telegram:[/green] https://t.me/+6EzmY-eAkLFkZWYy",
        border_style="blue"
    ))

def build_small_query(domain):
    return dns.message.make_query(domain, dns.rdatatype.A)

def build_large_query(domain, target_size=LARGE_QUERY_SIZE):
    labels = []
    remaining = max(1, target_size - 60)
    while remaining > 0:
        chunk_size = min(63, remaining)
        labels.append("a" * chunk_size)
        remaining -= chunk_size
    long_name = ".".join(labels) + "." + domain
    msg = dns.message.make_query(long_name, dns.rdatatype.A)
    msg.use_edns(edns=0, payload=4096, options=[dns.edns.GenericOption(12, b"")])
    return msg

async def quick_small_test(ip, port, domain):
    loop = asyncio.get_running_loop()
    q = build_small_query(domain)
    try:
        await loop.run_in_executor(None, lambda: dns.query.udp(q, ip, port=port, timeout=TIMEOUT))
        return True
    except:
        return False

async def large_query_test(ip, port, domain):
    loop = asyncio.get_running_loop()
    q = build_large_query(domain)
    try:
        await loop.run_in_executor(None, lambda: dns.query.udp(q, ip, port=port, timeout=TIMEOUT))
        return True
    except:
        return False

async def stability_test(ip, port, domain):
    successes = 0
    rtts = []
    small_q = build_small_query(domain)
    large_q = build_large_query(domain)
    loop = asyncio.get_running_loop()

    for _ in range(TEST_RETRIES_PHASE3):
        start = time.time()
        try:
            await loop.run_in_executor(None, lambda: dns.query.udp(small_q, ip, port=port, timeout=TIMEOUT))
            await loop.run_in_executor(None, lambda: dns.query.udp(large_q, ip, port=port, timeout=TIMEOUT))
            successes += 1
            rtts.append((time.time() - start) * 1000)
        except:
            pass

    loss = ((TEST_RETRIES_PHASE3 - successes) / TEST_RETRIES_PHASE3) * 100
    if successes == 0:
        return False, 0.0, loss

    avg_rtt = sum(rtts) / len(rtts)
    is_valid = (loss <= MAX_ACCEPTABLE_LOSS) and (avg_rtt <= MAX_AVG_RTT_MS)
    return is_valid, avg_rtt, loss

def make_table(title, done, total, passed, speed):
    table = Table(title=title)
    table.add_column("Processed", justify="center")
    table.add_column("Passed", justify="center")
    table.add_column("Speed (IP/s)", justify="center")
    table.add_row(f"{done}/{total}", str(passed), f"{speed:.1f}")
    return table

async def run_phase(title, targets, test_func, concurrent_limit, domain):
    semaphore = asyncio.Semaphore(concurrent_limit)
    start_time = time.time()
    stats = {"done": 0, "passed": 0}

    async def worker(ip, port):
        async with semaphore:
            result = await test_func(ip, port, domain)
            return (ip, port), result

    tasks = [asyncio.create_task(worker(ip, port)) for ip, port in targets]

    with Live(console=console, refresh_per_second=4) as live:
        for future in asyncio.as_completed(tasks):
            (ip, port), result = await future
            stats["done"] += 1
            if result:
                stats["passed"] += 1

            elapsed = time.time() - start_time
            speed = stats["done"] / elapsed if elapsed > 0 else 0

            live.update(make_table(title, stats["done"], len(targets), stats["passed"], speed))

    survivors = [t for i, t in enumerate(targets) if i < stats["passed"]]
    console.print(f"[green][✓][/green] {title} finished | Passed: {stats['passed']}")
    return survivors

async def main():
    banner()

    input_file = console.input("[cyan]Enter IP list file:[/cyan] ").strip()
    output_file = console.input("[cyan]Enter output file:[/cyan] ").strip()
    domain = console.input("[cyan]Enter test domain:[/cyan] ").strip()

    try:
        with open(input_file, "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except:
        console.print("[red]File not found[/red]")
        return

    targets = []
    for line in lines:
        if ":" in line:
            try:
                ip, port_str = line.rsplit(":", 1)
                port = int(port_str)
            except:
                continue
        else:
            ip, port = line, 53
        targets.append((ip, port))

    console.print(f"\n[bold yellow]Loaded {len(targets)} IPs[/bold yellow]")
    console.print(f"[bold yellow]Domain:[/bold yellow] {domain}")

    with open(output_file, "w"):
        pass

    phase1 = await run_phase("Phase 1 - Quick Check", targets, quick_small_test, MAX_CONCURRENT_PHASE1, domain)
    phase2 = await run_phase("Phase 2 - Large Query", phase1, large_query_test, MAX_CONCURRENT_PHASE2, domain)

    console.print("\n[bold magenta]Phase 3 - Stability Test[/bold magenta]")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PHASE3)
    stats = {"done": 0, "valid": 0}

    async def worker(ip, port):
        async with semaphore:
            return (ip, port), await stability_test(ip, port, domain)

    tasks = [asyncio.create_task(worker(ip, port)) for ip, port in phase2]

    with Live(console=console, refresh_per_second=4) as live:
        for future in asyncio.as_completed(tasks):
            (ip, port), (is_valid, avg_rtt, loss) = await future
            stats["done"] += 1

            if is_valid:
                stats["valid"] += 1
                addr = f"{ip}:{port}" if port != 53 else ip
                with open(output_file, "a") as f:
                    f.write(addr + "\n")
                console.print(f"[green]VALID[/green] {addr} | {avg_rtt:.1f}ms")

            live.update(make_table("Phase 3", stats["done"], len(phase2), stats["valid"], stats["done"]))

    console.print(Panel.fit(
        f"[green]Finished[/green]\nValid IPs: {stats['valid']}\nSaved in: {output_file}",
        border_style="green"
    ))

if __name__ == "__main__":
    asyncio.run(main())