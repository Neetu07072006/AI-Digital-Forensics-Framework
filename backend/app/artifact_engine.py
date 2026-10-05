import hashlib
import os
import re
from pathlib import Path

URL_PATTERN = re.compile(
    r"https?://[^\s\"'<>]+",
    re.IGNORECASE
)

IP_PATTERN = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

SUSPICIOUS_KEYWORDS = [
    "powershell",
    "cmd.exe",
    "ransomware",
    "keylogger",
    "backdoor",
    "trojan",
    "malware",
    "credential",
    "password",
    "mimikatz",
    "nc.exe",
    "netcat",
    "reverse shell",
    "bitcoin"
]

def calculate_hashes(file_path):
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            md5.update(chunk)
            sha256.update(chunk)

    return {
        "md5": md5.hexdigest(),
        "sha256": sha256.hexdigest()
    }

def extract_strings(file_path, minimum_length=4):
    with open(file_path, "rb") as file:
        data = file.read()

    text = data.decode("utf-8", errors="ignore")

    strings = re.findall(
        rf"[\x20-\x7E]{{{minimum_length},}}",
        text
    )

    return list(dict.fromkeys(strings))

def extract_artifacts(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("Evidence file not found")

    hashes = calculate_hashes(file_path)
    strings = extract_strings(file_path)

    combined_text = "\n".join(strings)

    urls = list(dict.fromkeys(
        URL_PATTERN.findall(combined_text)
    ))

    ips = list(dict.fromkeys(
        IP_PATTERN.findall(combined_text)
    ))

    emails = list(dict.fromkeys(
        EMAIL_PATTERN.findall(combined_text)
    ))

    suspicious = []

    lower_text = combined_text.lower()

    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.lower() in lower_text:
            suspicious.append(keyword)

    stat = path.stat()

    return {
        "file_name": path.name,
        "file_size": stat.st_size,
        "md5": hashes["md5"],
        "sha256": hashes["sha256"],
        "strings": strings[:500],
        "urls": urls,
        "ips": ips,
        "emails": emails,
        "suspicious_keywords": suspicious
    }