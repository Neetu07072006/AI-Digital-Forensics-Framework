import os
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors


REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_forensic_report(
    case,
    evidence,
    findings,
    timeline,
    ai_investigation
):
    report_name = f"case_{case.case_id}_forensic_report.pdf"
    report_path = os.path.join(REPORT_DIR, report_name)

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elements = []

    elements.append(
        Paragraph(
            "AI Digital Forensics Framework",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "Digital Forensic Investigation Report",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 15))

    case_data = [
        ["Case ID", str(case.case_id)],
        ["Case Name", case.case_name],
        ["Investigator", case.investigator],
        ["Status", case.status],
        ["Priority", case.priority],
        [
            "Generated",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
    ]

    table = Table(case_data, colWidths=[130, 350])

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ])
    )

    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "1. Investigation Summary",
            styles["Heading2"]
        )
    )

    summary = (
        case.description
        if case.description
        else "No case description was provided."
    )

    elements.append(
        Paragraph(
            summary,
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            "2. Evidence",
            styles["Heading2"]
        )
    )

    evidence_data = [
        [
            "ID",
            "File",
            "Size",
            "SHA-256"
        ]
    ]

    for item in evidence:
        evidence_data.append([
            str(item.evidence_id),
            item.file_name,
            str(item.file_size),
            item.sha256_hash
        ])

    if len(evidence_data) == 1:
        evidence_data.append(
            ["-", "No evidence", "-", "-"]
        )

    evidence_table = Table(
        evidence_data,
        colWidths=[40, 150, 70, 220]
    )

    evidence_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ])
    )

    elements.append(evidence_table)
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "3. Threat Findings",
            styles["Heading2"]
        )
    )

    if findings:
        for finding in findings:
            elements.append(
                Paragraph(
                    f"<b>{finding.title}</b> "
                    f"[{finding.severity}] "
                    f"(Risk Score: {finding.risk_score})",
                    styles["BodyText"]
                )
            )

            elements.append(
                Paragraph(
                    finding.description,
                    styles["BodyText"]
                )
            )

            if finding.evidence_reference:
                elements.append(
                    Paragraph(
                        f"Evidence Reference: "
                        f"{finding.evidence_reference}",
                        styles["BodyText"]
                    )
                )

            elements.append(Spacer(1, 8))
    else:
        elements.append(
            Paragraph(
                "No threat findings were detected.",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            "4. Forensic Timeline",
            styles["Heading2"]
        )
    )

    if timeline:
        timeline_data = [
            [
                "Time",
                "Event",
                "Description"
            ]
        ]

        for event in timeline:
            timeline_data.append([
                str(event.event_time),
                event.title,
                event.description or ""
            ])

        timeline_table = Table(
            timeline_data,
            colWidths=[120, 150, 210]
        )

        timeline_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP")
            ])
        )

        elements.append(timeline_table)
    else:
        elements.append(
            Paragraph(
                "No timeline events were generated.",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "5. AI Investigation",
            styles["Heading2"]
        )
    )

    if ai_investigation:
        elements.append(
            Paragraph(
                f"<b>Summary:</b> "
                f"{ai_investigation.summary}",
                styles["BodyText"]
            )
        )

        elements.append(Spacer(1, 8))

        elements.append(
            Paragraph(
                f"<b>Attack Pattern:</b> "
                f"{ai_investigation.attack_pattern}",
                styles["BodyText"]
            )
        )

        elements.append(Spacer(1, 8))

        elements.append(
            Paragraph(
                f"<b>Risk Assessment:</b> "
                f"{ai_investigation.risk_assessment}",
                styles["BodyText"]
            )
        )

        elements.append(Spacer(1, 8))

        elements.append(
            Paragraph(
                f"<b>Recommendations:</b> "
                f"{ai_investigation.recommendations}",
                styles["BodyText"]
            )
        )
    else:
        elements.append(
            Paragraph(
                "No AI investigation has been generated.",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "6. Conclusion",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            "This report was generated from the forensic evidence, "
            "artifact analysis, timeline events, threat findings, "
            "and AI investigation available in the framework.",
            styles["BodyText"]
        )
    )

    document.build(elements)

    return report_path