import math
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from app.database.mongodb import mongodb
from app.schemas.anomaly import AnomalyItem, AnomalySummary, AnomalyType, AnomalySeverity


class AnomalyService:
    """Statistical rule-based anomaly detection engine (no ML dependencies)."""

    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = mongodb.get_database().transactions
        return self._collection

    async def get_historical_transactions(
        self, 
        user_id: str, 
        category: Optional[str] = None,
        exclude_transaction_id: Optional[str] = None
    ) -> List[Dict]:
        """Fetch past expense transactions for statistical evaluation."""
        try:
            query = {
                "user_id": user_id,
                "transaction_type": "expense"
            }
            if category:
                query["category"] = category

            cursor = self.collection.find(query).sort("date", -1)
            transactions = []
            async for doc in cursor:
                doc_id = str(doc["_id"])
                if exclude_transaction_id and doc_id == exclude_transaction_id:
                    continue
                doc["id"] = doc_id
                transactions.append(doc)
            return transactions
        except Exception as e:
            print(f"Warning: Failed to fetch historical transactions for anomaly service: {e}")
            return []

    async def detect_unusual_amount_anomalies(
        self, 
        user_id: str = "default_user", 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[AnomalyItem]:
        """
        Detect unusual transaction amounts based on category statistics.
        
        Rules:
        - If past transactions in category >= 4: calculate mean (μ) and standard deviation (σ).
          Flag if Z = (amount - μ) / σ > 2.0. Severity = HIGH if Z > 3.0 else MEDIUM.
        - If past transactions in category is 1-3: fallback to multiplier rule (amount > 3 * μ).
          Flag with confidence_level = "low".
        - If zero past history: skip gracefully.
        """
        if year is None or month is None:
            today = datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Get current month expense transactions
        query = {
            "user_id": user_id,
            "transaction_type": "expense",
            "date": {"$gte": start_date, "$lt": end_date}
        }

        try:
            current_txs = await self.collection.find(query).sort("date", -1).to_list(length=None)
        except Exception as e:
            print(f"Warning: Failed to fetch current month transactions: {e}")
            return []

        anomalies = []

        for tx in current_txs:
            tx_id = str(tx["_id"])
            category = tx.get("category", "Uncategorized")
            amount = tx.get("amount", 0.0)
            date_str = tx["date"].strftime("%Y-%m-%d") if isinstance(tx["date"], datetime) else str(tx["date"])[:10]
            description = tx.get("description", "Transaction")

            # Fetch past transactions in this category (excluding current tx)
            past_txs = await self.get_historical_transactions(user_id, category, exclude_transaction_id=tx_id)
            past_amounts = [t["amount"] for t in past_txs if "amount" in t]

            if len(past_amounts) == 0:
                continue

            if len(past_amounts) >= 4:
                mean = float(np.mean(past_amounts))
                std_dev = float(np.std(past_amounts))

                if std_dev > 0:
                    z_score = (amount - mean) / std_dev
                    if z_score > 2.0:
                        severity = AnomalySeverity.HIGH if z_score > 3.0 else AnomalySeverity.MEDIUM
                        multiplier = round(amount / mean, 1) if mean > 0 else 0.0

                        anomalies.append(AnomalyItem(
                            id=f"anom_amount_{tx_id}",
                            transaction_id=tx_id,
                            anomaly_type=AnomalyType.UNUSUAL_AMOUNT,
                            severity=severity,
                            title=f"Unusual {category} spend: ₹{amount:,.0f}",
                            description=f"Transaction of ₹{amount:,.0f} for '{description}' is {z_score:.1f} std deviations above your average of ₹{mean:,.0f} in {category}.",
                            category=category,
                            amount=amount,
                            average_amount=round(mean, 2),
                            z_score=round(z_score, 2),
                            multiplier=multiplier,
                            date=date_str,
                            confidence_level="high"
                        ))
                else:
                    # Constant past amounts, evaluate multiplier
                    if mean > 0 and amount > 2.5 * mean:
                        multiplier = round(amount / mean, 1)
                        anomalies.append(AnomalyItem(
                            id=f"anom_amount_{tx_id}",
                            transaction_id=tx_id,
                            anomaly_type=AnomalyType.UNUSUAL_AMOUNT,
                            severity=AnomalySeverity.MEDIUM,
                            title=f"Unusual {category} spend: ₹{amount:,.0f}",
                            description=f"Transaction of ₹{amount:,.0f} for '{description}' is {multiplier:.1f}x higher than your usual ₹{mean:,.0f} in {category}.",
                            category=category,
                            amount=amount,
                            average_amount=round(mean, 2),
                            z_score=None,
                            multiplier=multiplier,
                            date=date_str,
                            confidence_level="medium"
                        ))
            elif 1 <= len(past_amounts) < 4:
                mean = float(np.mean(past_amounts))
                if mean > 0 and amount > 3.0 * mean:
                    multiplier = round(amount / mean, 1)
                    anomalies.append(AnomalyItem(
                        id=f"anom_amount_{tx_id}",
                        transaction_id=tx_id,
                        anomaly_type=AnomalyType.UNUSUAL_AMOUNT,
                        severity=AnomalySeverity.LOW,
                        title=f"Unusual {category} spend (Low confidence): ₹{amount:,.0f}",
                        description=f"Transaction of ₹{amount:,.0f} for '{description}' is {multiplier:.1f}x higher than previous transactions (limited history).",
                        category=category,
                        amount=amount,
                        average_amount=round(mean, 2),
                        z_score=None,
                        multiplier=multiplier,
                        date=date_str,
                        confidence_level="low"
                    ))

        return anomalies

    async def detect_new_category_anomalies(
        self, 
        user_id: str = "default_user", 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[AnomalyItem]:
        """Detect transactions in categories never used before in historical data."""
        if year is None or month is None:
            today = datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Fetch categories used BEFORE this month
        try:
            prior_pipeline = [
                {"$match": {"user_id": user_id, "transaction_type": "expense", "date": {"$lt": start_date}}},
                {"$group": {"_id": "$category"}}
            ]
            prior_results = await self.collection.aggregate(prior_pipeline).to_list(length=None)
            prior_categories = set(r["_id"] for r in prior_results if r["_id"])
        except Exception as e:
            print(f"Warning: Failed to fetch prior categories: {e}")
            return []

        if not prior_categories:
            # First month of data, no prior history to establish new category
            return []

        # Current month transactions
        query = {
            "user_id": user_id,
            "transaction_type": "expense",
            "date": {"$gte": start_date, "$lt": end_date}
        }
        try:
            current_txs = await self.collection.find(query).sort("date", -1).to_list(length=None)
        except Exception as e:
            print(f"Warning: Failed to fetch current month transactions for category check: {e}")
            return []

        anomalies = []
        flagged_categories = set()

        for tx in current_txs:
            category = tx.get("category")
            if category and category not in prior_categories and category not in flagged_categories:
                flagged_categories.add(category)
                tx_id = str(tx["_id"])
                amount = tx.get("amount", 0.0)
                date_str = tx["date"].strftime("%Y-%m-%d") if isinstance(tx["date"], datetime) else str(tx["date"])[:10]
                description = tx.get("description", "Transaction")

                anomalies.append(AnomalyItem(
                    id=f"anom_newcat_{category}",
                    transaction_id=tx_id,
                    anomaly_type=AnomalyType.NEW_CATEGORY,
                    severity=AnomalySeverity.LOW,
                    title=f"First-time category spending: {category}",
                    description=f"You recorded a transaction of ₹{amount:,.0f} for '{description}' in '{category}', a category never used in prior months.",
                    category=category,
                    amount=amount,
                    average_amount=0.0,
                    z_score=None,
                    multiplier=None,
                    date=date_str,
                    confidence_level="high"
                ))

        return anomalies

    async def detect_daily_spikes(
        self, 
        user_id: str = "default_user", 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[AnomalyItem]:
        """Detect days where total expenses exceed 2.5x the average daily spend."""
        if year is None or month is None:
            today = datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        query = {
            "user_id": user_id,
            "transaction_type": "expense",
            "date": {"$gte": start_date, "$lt": end_date}
        }

        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]

        try:
            daily_totals = await self.collection.aggregate(pipeline).to_list(length=None)
        except Exception as e:
            print(f"Warning: Failed to fetch daily totals for spike detection: {e}")
            return []

        if not daily_totals:
            return []

        amounts = [d["total"] for d in daily_totals]
        avg_daily_spend = float(np.mean(amounts))

        if avg_daily_spend == 0:
            return []

        anomalies = []
        for d in daily_totals:
            total = d["total"]
            date_str = d["_id"]
            if total > 2.5 * avg_daily_spend:
                multiplier = round(total / avg_daily_spend, 1)
                anomalies.append(AnomalyItem(
                    id=f"anom_spike_{date_str}",
                    transaction_id=None,
                    anomaly_type=AnomalyType.DAILY_SPIKE,
                    severity=AnomalySeverity.MEDIUM if multiplier < 4.0 else AnomalySeverity.HIGH,
                    title=f"Daily spending spike on {date_str}",
                    description=f"Total expenses reached ₹{total:,.0f} on {date_str}, which is {multiplier}x your daily average of ₹{avg_daily_spend:,.0f}.",
                    category="Overall",
                    amount=total,
                    average_amount=round(avg_daily_spend, 2),
                    z_score=None,
                    multiplier=multiplier,
                    date=date_str,
                    confidence_level="high"
                ))

        return anomalies

    async def get_anomaly_summary(
        self, 
        user_id: str = "default_user", 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> AnomalySummary:
        """Generate structured anomaly summary and alert items."""
        if year is None or month is None:
            today = datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month

        amount_anomalies = await self.detect_unusual_amount_anomalies(user_id, year, month)
        category_anomalies = await self.detect_new_category_anomalies(user_id, year, month)
        spike_anomalies = await self.detect_daily_spikes(user_id, year, month)

        all_anomalies = amount_anomalies + category_anomalies + spike_anomalies

        # Sort anomalies by severity (high > medium > low) then date
        severity_order = {AnomalySeverity.HIGH: 0, AnomalySeverity.MEDIUM: 1, AnomalySeverity.LOW: 2}
        all_anomalies.sort(key=lambda a: (severity_order.get(a.severity, 2), a.date), reverse=False)

        high_count = sum(1 for a in all_anomalies if a.severity == AnomalySeverity.HIGH)
        med_count = sum(1 for a in all_anomalies if a.severity == AnomalySeverity.MEDIUM)
        low_count = sum(1 for a in all_anomalies if a.severity == AnomalySeverity.LOW)

        amount_count = sum(1 for a in all_anomalies if a.anomaly_type == AnomalyType.UNUSUAL_AMOUNT)
        newcat_count = sum(1 for a in all_anomalies if a.anomaly_type == AnomalyType.NEW_CATEGORY)
        spike_count = sum(1 for a in all_anomalies if a.anomaly_type == AnomalyType.DAILY_SPIKE)

        return AnomalySummary(
            total_anomalies=len(all_anomalies),
            high_severity_count=high_count,
            medium_severity_count=med_count,
            low_severity_count=low_count,
            unusual_amount_count=amount_count,
            new_category_count=newcat_count,
            daily_spike_count=spike_count,
            anomalies=all_anomalies,
            year=year,
            month=month
        )


# Global service instance
anomaly_service = AnomalyService()
