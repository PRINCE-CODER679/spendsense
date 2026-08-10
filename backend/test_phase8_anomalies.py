import asyncio
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.database.mongodb import mongodb
from app.services.anomaly_service import anomaly_service
from app.schemas.anomaly import AnomalySummary, AnomalyType, AnomalySeverity

async def test_phase8_anomalies():
    print("==================================================")
    print("RUNNING PHASE 8 ANOMALY DETECTION TEST SUITE")
    print("==================================================")

    await mongodb.connect()

    # 1. Test Anomaly Summary Service
    summary = await anomaly_service.get_anomaly_summary("default_user")
    print(f"[PASS] Anomaly Summary generated successfully:")
    print(f"   - Total Anomalies Flagged: {summary.total_anomalies}")
    print(f"   - High Severity: {summary.high_severity_count}")
    print(f"   - Medium Severity: {summary.medium_severity_count}")
    print(f"   - Low Severity: {summary.low_severity_count}")
    print(f"   - Unusual Amount Anomalies: {summary.unusual_amount_count}")
    print(f"   - New Category Anomalies: {summary.new_category_count}")
    print(f"   - Daily Spike Anomalies: {summary.daily_spike_count}")

    assert isinstance(summary, AnomalySummary)
    assert summary.total_anomalies >= 0

    # 2. Test Anomaly Items
    for item in summary.anomalies:
        print(f"   - [{item.severity.upper()}] {item.anomaly_type}: {item.title}")
        print(f"     Description: {item.description}")
        assert item.anomaly_type in [AnomalyType.UNUSUAL_AMOUNT, AnomalyType.NEW_CATEGORY, AnomalyType.DAILY_SPIKE]
        assert item.severity in [AnomalySeverity.HIGH, AnomalySeverity.MEDIUM, AnomalySeverity.LOW]

    await mongodb.close()
    print("==================================================")
    print("ALL PHASE 8 ANOMALY DETECTION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_phase8_anomalies())
