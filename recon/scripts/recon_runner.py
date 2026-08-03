#!/usr/bin/env python3
"""Master Recon Runner — runs full recon pipeline on a target domain.

Usage:
    python3 recon_runner.py example.com --output output/example.com
    python3 recon_runner.py example.com --subdomains-only
    python3 recon_runner.py example.com --urls-only
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE_DIR / "tools"
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts"

GO_BIN = "/home/wasim/go/bin"


def run_cmd(cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=300,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def ensure_output_dir(domain: str) -> Path:
    out = OUTPUT_DIR / domain
    out.mkdir(parents=True, exist_ok=True)
    return out


def subdomain_enum(domain: str, out_dir: Path) -> Path:
    """Run subfinder + amass for subdomain enumeration."""
    subdomains_file = out_dir / "subdomains.txt"
    print(f"\n[*] Enumerating subdomains for {domain}...")
    
    # subfinder
    sf_output = out_dir / "subfinder.txt"
    with open(sf_output, "w", encoding="utf-8") as f:
        subprocess.run(
            [f"{GO_BIN}/subfinder", "-d", domain, "-silent"],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
    
    # amass
    amass_output = out_dir / "amass.txt"
    with open(amass_output, "w", encoding="utf-8") as f:
        subprocess.run(
            [f"{GO_BIN}/amass", "enum", "-d", domain, "-o", str(amass_output)],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
        )
    
    # Combine and deduplicate
    all_subs = set()
    for f in [sf_output, amass_output]:
        if f.exists():
            all_subs.update(line.strip() for line in f.read_text().splitlines() if line.strip())
    
    subdomains_file.write_text("\n".join(sorted(all_subs)) + "\n", encoding="utf-8")
    print(f"[+] Found {len(all_subs)} unique subdomains -> {subdomains_file}")
    return subdomains_file


def probe_http(subdomains_file: Path, out_dir: Path) -> Path:
    """Probe subdomains for HTTP/HTTPS services."""
    alive_file = out_dir / "alive.txt"
    print(f"\n[*] Probing HTTP services...")
    
    with open(alive_file, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            [f"{GO_BIN}/httpx", "-silent", "-status-code", "-title", "-tech-detect", "-l", str(subdomains_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, _ = proc.communicate(timeout=300)
        f.write(stdout)
    
    if alive_file.exists():
        lines = [line.strip() for line in alive_file.read_text().splitlines() if line.strip()]
        alive_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[+] {len(lines)} alive hosts -> {alive_file}")
    return alive_file


def crawl_urls(alive_file: Path, out_dir: Path) -> Path:
    """Crawl alive hosts for URLs."""
    urls_file = out_dir / "urls.txt"
    print(f"\n[*] Crawling URLs with katana...")
    
    with open(urls_file, "w", encoding="utf-8") as f:
        subprocess.run(
            [f"{GO_BIN}/katana", "-list", str(alive_file), "-silent", "-depth", "3", "-timeout", "10"],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
        )
    
    if urls_file.exists():
        lines = [line.strip() for line in urls_file.read_text().splitlines() if line.strip()]
        urls_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[+] {len(lines)} URLs found -> {urls_file}")
    return urls_file


def discover_historical_urls(domain: str, out_dir: Path) -> Path:
    """Discover historical URLs from Wayback Machine and Common Crawl."""
    hist_file = out_dir / "historical_urls.txt"
    print(f"\n[*] Discovering historical URLs for {domain}...")
    
    # waybackurls
    wb_output = out_dir / "wayback.txt"
    with open(wb_output, "w", encoding="utf-8") as f:
        try:
            subprocess.run([f"{GO_BIN}/waybackurls", domain], stdout=f, stderr=subprocess.PIPE, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            print(f"  [!] waybackurls timed out")
    
    # gau
    gau_output = out_dir / "gau.txt"
    with open(gau_output, "w", encoding="utf-8") as f:
        try:
            subprocess.run([f"{GO_BIN}/gau", "--subs", domain], stdout=f, stderr=subprocess.PIPE, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            print(f"  [!] gau timed out")
    
    # Combine
    all_urls = set()
    for f in [wb_output, gau_output]:
        if f.exists():
            all_urls.update(line.strip() for line in f.read_text().splitlines() if line.strip())
    
    hist_file.write_text("\n".join(sorted(all_urls)) + "\n", encoding="utf-8")
    print(f"[+] {len(all_urls)} historical URLs -> {hist_file}")
    return hist_file


def extract_parameters(urls_file: Path, out_dir: Path) -> Path:
    """Extract unique parameters from URLs."""
    params_file = out_dir / "parameters.txt"
    print(f"\n[*] Extracting parameters...")
    
    with open(urls_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    with open(out_dir / "urls_for_unfurl.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls))
    
    result = subprocess.run(
        f"cat {out_dir / 'urls_for_unfurl.txt'} | {GO_BIN}/unfurl keys",
        shell=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    params = sorted(set(line.strip() for line in result.stdout.splitlines() if line.strip()))
    params_file.write_text("\n".join(params), encoding="utf-8")
    print(f"[+] {len(params)} unique parameters -> {params_file}")
    return params_file


def port_scan(domain: str, out_dir: Path) -> Path:
    """Quick port scan with naabu."""
    ports_file = out_dir / "ports.txt"
    print(f"\n[*] Scanning ports for {domain}...")
    
    with open(ports_file, "w", encoding="utf-8") as f:
        subprocess.run(
            [f"{GO_BIN}/naabu", "-host", domain, "-top-ports", "100", "-silent"],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
        )
    
    if ports_file.exists():
        lines = [line.strip() for line in ports_file.read_text().splitlines() if line.strip()]
        ports_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[+] {len(lines)} open ports -> {ports_file}")
    return ports_file


def run_nuclei(urls_file: Path, out_dir: Path) -> Path:
    """Run nuclei vulnerability scanner (if installed)."""
    nuclei_file = out_dir / "nuclei_results.txt"
    print(f"\n[*] Running nuclei on URLs...")
    
    with open(nuclei_file, "w", encoding="utf-8") as f:
        subprocess.run(
            [f"{GO_BIN}/nuclei", "-l", str(urls_file), "-silent", "-severity", "low,medium,high,critical"],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True,
            timeout=600,
        )
    
    if nuclei_file.exists():
        lines = [line.strip() for line in nuclei_file.read_text().splitlines() if line.strip()]
        nuclei_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[+] {len(lines)} potential vulnerabilities -> {nuclei_file}")
    return nuclei_file


def generate_summary(domain: str, out_dir: Path):
    """Generate a summary report."""
    summary_file = out_dir / "summary.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [f"Recon Summary for {domain}", f"Generated: {timestamp}", "=" * 50]
    
    for fname in ["subdomains.txt", "alive.txt", "urls.txt", "historical_urls.txt", "parameters.txt", "ports.txt", "nuclei_results.txt"]:
        fpath = out_dir / fname
        if fpath.exists():
            count = len([l for l in fpath.read_text().splitlines() if l.strip()])
            lines.append(f"{fname}: {count} entries")
    
    summary_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[+] Summary -> {summary_file}")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Master Recon Runner")
    parser.add_argument("domain", help="Target domain (e.g., example.com)")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--subdomains-only", action="store_true")
    parser.add_argument("--urls-only", action="store_true")
    parser.add_argument("--skip-nuclei", action="store_true")
    args = parser.parse_args()

    domain = args.domain.strip().lower()
    out_dir = ensure_output_dir(domain)
    
    print(f"=== Recon Pipeline: {domain} ===")
    
    if not args.urls_only:
        subs = subdomain_enum(domain, out_dir)
        alive = probe_http(subs, out_dir)
        port_scan(domain, out_dir)
    
    if not args.subdomains_only:
        if not args.urls_only:
            urls = crawl_urls(alive, out_dir)
        else:
            urls = Path(args.output) if args.output else out_dir / "urls.txt"
        hist = discover_historical_urls(domain, out_dir)
        
        # Combine all URLs
        all_urls_file = out_dir / "all_urls.txt"
        all_urls = set()
        for f in [urls, hist]:
            if f.exists():
                all_urls.update(line.strip() for line in f.read_text().splitlines() if line.strip())
        all_urls_file.write_text("\n".join(sorted(all_urls)), encoding="utf-8")
        print(f"\n[+] {len(all_urls)} total URLs -> {all_urls_file}")
        
        extract_parameters(all_urls_file, out_dir)
        
        if not args.skip_nuclei:
            run_nuclei(all_urls_file, out_dir)
    
    generate_summary(domain, out_dir)
    print(f"\n=== Recon complete. Results in {out_dir} ===")


if __name__ == "__main__":
    main()
