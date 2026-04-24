import argparse
import json
from pathlib import Path
import pandas as pd

SEVERITY_SCORE = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

def load_csvs(data_dir: Path):
    return {
        "students": pd.read_csv(data_dir / "students.csv"),
        "payments": pd.read_csv(data_dir / "payments.csv"),
        "grades": pd.read_csv(data_dir / "grades.csv"),
        "finance": pd.read_csv(data_dir / "finance_transactions.csv"),
    }

def make_alert(alert_id, alert_type, severity, entity_id, source, rule, justification, recommended_action, owner_role):
    return {
        "alert_id": alert_id,
        "alert_type": alert_type,
        "severity": severity,
        "priority_score": SEVERITY_SCORE[severity],
        "entity_id": entity_id,
        "source_system": source,
        "rule_name": rule,
        "justification": justification,
        "status": "NEW",
        "recommended_action": recommended_action,
        "owner_role": owner_role,
        "detected_at": "2026-04-22",
        "historical_note": "Détectée automatiquement par la chaîne data; à valider par la MOA."
    }

def detect(data_dir: Path, config_path: Path):
    frames = load_csvs(data_dir)
    students = frames["students"]
    payments = frames["payments"]
    grades = frames["grades"]
    finance = frames["finance"]
    thresholds = json.loads(config_path.read_text(encoding="utf-8"))

    cost_centers = {
        "INFO": "CC-INFO",
        "FIN": "CC-FIN",
        "RH": "CC-RH",
        "MKT": "CC-MKT",
    }

    alerts = []
    counter = 1

    duplicate_groups = students.groupby("national_id").filter(lambda x: len(x) > 1)
    for national_id, group in duplicate_groups.groupby("national_id"):
        alerts.append(
            make_alert(
                f"ALT{counter:04d}",
                "DUPLICATE_REGISTRATION",
                thresholds.get("duplicate_registration_severity", "HIGH"),
                ", ".join(group["student_id"].astype(str).tolist()),
                "SCOLARITE",
                "duplicate_national_id",
                f"{len(group)} inscriptions partagent le national_id {national_id}.",
                "Vérifier l'identité réelle, fusionner ou clôturer les doublons.",
                "MOA Scolarité",
            )
        )
        counter += 1

    paid_without_trace = payments[
        (payments["payment_status"] == "PAID")
        & ((payments["receipt_id"].fillna("") == "") | (payments["amount"] <= 0))
    ]
    for _, row in paid_without_trace.iterrows():
        alerts.append(
            make_alert(
                f"ALT{counter:04d}",
                "PAID_WITHOUT_TRACE",
                thresholds.get("paid_without_receipt_severity", "HIGH"),
                row["payment_id"],
                "FINANCE",
                "paid_without_receipt_or_zero_amount",
                f"Paiement {row['payment_id']} marqué PAID avec reçu manquant ou montant nul ({row['amount']}).",
                "Contrôler pièce justificative, journal de caisse et utilisateur de saisie.",
                "MOA Finance",
            )
        )
        counter += 1

    grade_anomalies = grades[grades["grade"].isna() | (grades["grade"] < 0) | (grades["grade"] > 20)]
    for _, row in grade_anomalies.iterrows():
        severity = thresholds.get("invalid_grade_severity", "HIGH")
        if pd.isna(row["grade"]):
            severity = thresholds.get("missing_grade_severity", "MEDIUM")
            detail = "note manquante"
        else:
            detail = f"note incohérente ({row['grade']})"
        alerts.append(
            make_alert(
                f"ALT{counter:04d}",
                "GRADE_ANOMALY",
                severity,
                row["student_id"],
                "SCOLARITE",
                "missing_or_invalid_grade",
                f"{detail} pour {row['course_code']} au semestre {row['semester']}.",
                "Vérifier la saisie des notes, le procès-verbal et republier si nécessaire.",
                "MOA Pédagogie",
            )
        )
        counter += 1

    orphan_payments = payments[~payments["student_id"].isin(students["student_id"])]
    for _, row in orphan_payments.iterrows():
        alerts.append(
            make_alert(
                f"ALT{counter:04d}",
                "ORPHAN_PAYMENT",
                thresholds.get("orphan_payment_severity", "HIGH"),
                row["payment_id"],
                "FINANCE",
                "payment_without_student",
                f"Paiement {row['payment_id']} rattaché à {row['student_id']} absent du référentiel scolarité.",
                "Corriger l'identifiant étudiant ou annuler l'écriture concernée.",
                "MOE Data / Finance",
            )
        )
        counter += 1

    student_dept = students.drop_duplicates("student_id")[["student_id", "department_code"]]
    cross = finance.merge(student_dept, on="student_id", how="left")
    cross["expected_cc"] = cross["department_code"].map(cost_centers)
    cross_gap = cross[(cross["department_code"].isna()) | (cross["expected_cc"].fillna("CC-UNKNOWN") != cross["cost_center"])]
    for _, row in cross_gap.iterrows():
        alerts.append(
            make_alert(
                f"ALT{counter:04d}",
                "CROSS_SYSTEM_GAP",
                thresholds.get("cross_system_gap_severity", "HIGH"),
                row["transaction_id"],
                "FINANCE/SCOLARITE/RH",
                "cost_center_mismatch",
                f"Transaction {row['transaction_id']} sur {row['cost_center']} incompatible avec le département {row.get('department_code', None)}.",
                "Valider le mapping des centres de coûts et corriger l'alimentation des interfaces.",
                "MOE Data",
            )
        )
        counter += 1

    high_amount = finance[finance["amount"] > thresholds["high_amount_threshold"]]
    for _, row in high_amount.iterrows():
        alerts.append(
            make_alert(
                f"ALT{counter:04d}",
                "UNUSUAL_TRANSACTION",
                thresholds.get("unusual_transaction_severity", "CRITICAL"),
                row["transaction_id"],
                "FINANCE",
                "high_amount_threshold",
                f"Montant inhabituel {row['amount']} XOF au-delà du seuil {thresholds['high_amount_threshold']} XOF.",
                "Bloquer la transaction, rapprocher avec pièces comptables et valider l'autorisation.",
                "MOA Finance",
            )
        )
        counter += 1

    duplicate_tx = finance.groupby(["student_id", "transaction_date", "amount"]).filter(
        lambda x: len(x) >= thresholds["duplicate_transaction_same_day_count"]
    )
    for _, group in duplicate_tx.groupby(["student_id", "transaction_date", "amount"]):
        alerts.append(
            make_alert(
                f"ALT{counter:04d}",
                "UNUSUAL_TRANSACTION",
                thresholds.get("unusual_transaction_severity", "CRITICAL"),
                ", ".join(group["transaction_id"].astype(str).tolist()),
                "FINANCE",
                "duplicate_same_day_transaction",
                f"{len(group)} transactions dupliquées le {group.iloc[0]['transaction_date']} pour {group.iloc[0]['amount']} XOF.",
                "Rejouer l'intégration, vérifier doublons de flux et annuler les écritures en trop.",
                "MOE Data / Finance",
            )
        )
        counter += 1

    alerts_df = pd.DataFrame(alerts).sort_values(["priority_score", "alert_type"], ascending=[False, True]).reset_index(drop=True)
    return alerts_df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="data")
    parser.add_argument("--output", default="data/alerts_output.csv")
    parser.add_argument("--config", default="config/thresholds.json")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    config_path = Path(args.config)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    alerts_df = detect(data_dir, config_path)
    alerts_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"{len(alerts_df)} alertes générées dans {output_path}")

if __name__ == "__main__":
    main()
