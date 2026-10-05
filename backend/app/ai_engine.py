import json
import os
import urllib.request

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

def build_investigation_context(case, evidence, findings, timeline):
    context = {
        "case": {
            "case_id": case.case_id,
            "case_name": case.case_name,
            "description": case.description,
            "investigator": case.investigator,
            "status": case.status,
            "priority": case.priority
        },
        "evidence": [
            {
                "evidence_id": item.evidence_id,
                "file_name": item.file_name,
                "file_type": item.file_type,
                "file_size": item.file_size,
                "sha256": item.sha256_hash
            }
            for item in evidence
        ],
        "findings": [
            {
                "finding_id": item.finding_id,
                "evidence_id": item.evidence_id,
                "artifact_id": item.artifact_id,
                "type": item.finding_type,
                "severity": item.severity,
                "risk_score": item.risk_score,
                "title": item.title,
                "description": item.description,
                "reference": item.evidence_reference
            }
            for item in findings
        ],
        "timeline": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "event_time": str(event.event_time),
                "title": event.title,
                "description": event.description,
                "source": event.source,
                "severity": event.severity
            }
            for event in timeline
        ]
    }

    return json.dumps(context, indent=2, default=str)

def generate_ai_investigation(context):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "summary": "AI analysis is unavailable because GEMINI_API_KEY is not configured.",
            "attack_pattern": "Not available",
            "risk_assessment": "Manual investigation required.",
            "recommendations": "Configure the AI API key and rerun the investigation.",
            "model": "unavailable"
        }

    prompt = f"""
You are a digital forensics investigation assistant.

Analyze ONLY the forensic information supplied below.

Do not invent evidence.
Do not claim that an IP, URL, file, or artifact is malicious unless
the supplied evidence supports that conclusion.
Clearly distinguish observations from hypotheses.

Return JSON with exactly these fields:
summary
attack_pattern
risk_assessment
recommendations

The response must be concise but useful for a forensic investigator.

FORENSIC DATA:
{context}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    request = urllib.request.Request(
        GEMINI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

        text = result["candidates"][0]["content"]["parts"][0]["text"]
        analysis = json.loads(text)

        return {
            "summary": analysis.get("summary", ""),
            "attack_pattern": analysis.get("attack_pattern", ""),
            "risk_assessment": analysis.get("risk_assessment", ""),
            "recommendations": analysis.get("recommendations", ""),
            "model": "gemini-2.5-flash"
        }

    except Exception as e:
        return {
            "summary": "AI investigation could not be completed.",
            "attack_pattern": "Unavailable",
            "risk_assessment": f"AI service error: {str(e)}",
            "recommendations": "Review the deterministic forensic findings manually.",
            "model": "gemini-2.5-flash"
        }