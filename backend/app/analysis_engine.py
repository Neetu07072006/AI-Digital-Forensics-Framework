import ipaddress
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = {
    "powershell": 25,
    "cmd.exe": 20,
    "ransomware": 40,
    "keylogger": 40,
    "backdoor": 40,
    "trojan": 40,
    "malware": 35,
    "mimikatz": 50,
    "reverse shell": 50,
    "nc.exe": 45,
    "netcat": 45,
    "credential": 25,
    "password": 15,
    "bitcoin": 20
}

SUSPICIOUS_URL_KEYWORDS = [
    "login",
    "verify",
    "account",
    "password",
    "credential",
    "update",
    "secure"
]

PRIVATE_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8")
]

def is_private_ip(value):
    try:
        address = ipaddress.ip_address(value)
        return any(address in network for network in PRIVATE_IP_RANGES)
    except ValueError:
        return False

def analyze_artifacts(artifacts):
    findings = []

    for artifact in artifacts:
        value = artifact.artifact_value
        lower_value = value.lower()

        if artifact.artifact_type == "IP":
            if not is_private_ip(value):
                findings.append({
                    "artifact_id": artifact.artifact_id,
                    "finding_type": "SUSPICIOUS_IP",
                    "severity": "Medium",
                    "risk_score": 30,
                    "title": "External IP Address Detected",
                    "description": (
                        f"External IP address {value} was identified "
                        "in the forensic artifact."
                    ),
                    "evidence_reference": value
                })

        if artifact.artifact_type == "URL":
            parsed = urlparse(value)

            if parsed.scheme == "http":
                findings.append({
                    "artifact_id": artifact.artifact_id,
                    "finding_type": "INSECURE_URL",
                    "severity": "Low",
                    "risk_score": 15,
                    "title": "Unencrypted HTTP URL Detected",
                    "description": (
                        f"The artifact contains an HTTP URL: {value}"
                    ),
                    "evidence_reference": value
                })

            for keyword in SUSPICIOUS_URL_KEYWORDS:
                if keyword in lower_value:
                    findings.append({
                        "artifact_id": artifact.artifact_id,
                        "finding_type": "SUSPICIOUS_URL",
                        "severity": "High",
                        "risk_score": 40,
                        "title": "Suspicious URL Pattern Detected",
                        "description": (
                            f"The URL contains suspicious keyword "
                            f"'{keyword}': {value}"
                        ),
                        "evidence_reference": value
                    })
                    break

        if artifact.artifact_type in [
            "STRING",
            "SUSPICIOUS_KEYWORD",
            "EMAIL"
        ]:
            for keyword, score in SUSPICIOUS_KEYWORDS.items():
                if keyword in lower_value:
                    severity = "Critical" if score >= 45 else "High"

                    findings.append({
                        "artifact_id": artifact.artifact_id,
                        "finding_type": "SUSPICIOUS_INDICATOR",
                        "severity": severity,
                        "risk_score": score,
                        "title": "Suspicious Indicator Detected",
                        "description": (
                            f"The artifact contains suspicious indicator "
                            f"'{keyword}'."
                        ),
                        "evidence_reference": value
                    })

    return findings

def calculate_case_risk(findings):
    if not findings:
        return {
            "risk_score": 0,
            "risk_level": "Informational"
        }

    score = sum(
        finding["risk_score"]
        for finding in findings
    )

    score = min(score, 100)

    if score >= 80:
        level = "Critical"
    elif score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    elif score > 0:
        level = "Low"
    else:
        level = "Informational"

    return {
        "risk_score": score,
        "risk_level": level
    }