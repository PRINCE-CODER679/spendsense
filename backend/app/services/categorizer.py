from typing import Dict, Optional
from app.schemas.transaction import TransactionCategory, TransactionType
from datetime import datetime


class CategorizationResult:
    def __init__(
        self,
        category: TransactionCategory,
        confidence: float,
        matched_rule: str,
        reason: str,
        source: str = "rule"
    ):
        self.category = category
        self.confidence = confidence
        self.matched_rule = matched_rule
        self.reason = reason
        self.source = source
    
    def to_dict(self) -> Dict:
        return {
            "category": self.category.value,
            "confidence": self.confidence,
            "matched_rule": self.matched_rule,
            "reason": self.reason,
            "source": self.source
        }


class TransactionCategorizer:
    # Category rules with keywords and merchants
    CATEGORY_RULES = {
        TransactionCategory.FOOD: {
            "merchants": [
                "swiggy", "zomato", "dominos", "pizza hut", "mcdonald", "mcdonalds",
                "kfc", "starbucks", "cafe", "coffee", "restaurant", "food",
                "dining", "eat", "meal", "lunch", "dinner", "breakfast",
                "burger king", "subway", "haldiram", "barbeque nation"
            ],
            "keywords": [
                "food", "restaurant", "cafe", "coffee", "meal", "dining",
                "swiggy", "zomato", "pizza", "burger", "sandwich"
            ],
            "confidence": 0.95
        },
        TransactionCategory.GROCERIES: {
            "merchants": [
                "dmart", "bigbasket", "blinkit", "zepto", "instamart",
                "reliance fresh", "more supermarket", "spencer", "foodhall",
                "grocery", "supermarket", "kirana"
            ],
            "keywords": [
                "grocery", "supermarket", "vegetables", "fruits", "milk",
                "bread", "dmart", "bigbasket", "ration"
            ],
            "confidence": 0.93
        },
        TransactionCategory.TRANSPORT: {
            "merchants": [
                "uber", "ola", "rapido", "metro", "irctc", "redbus",
                "makemytrip", "cleartrip", "yatra", "indian railways",
                "cab", "taxi", "auto", "rickshaw"
            ],
            "keywords": [
                "transport", "travel", "cab", "taxi", "uber", "ola",
                "metro", "train", "bus", "flight", "auto", "rickshaw"
            ],
            "confidence": 0.92
        },
        TransactionCategory.SHOPPING: {
            "merchants": [
                "amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa",
                "tata cliq", "croma", "reliance digital", "vivo", "samsung",
                "apple", "shopping", "mall", "store"
            ],
            "keywords": [
                "shopping", "amazon", "flipkart", "myntra", "purchase",
                "order", "clothing", "electronics", "gadgets"
            ],
            "confidence": 0.90
        },
        TransactionCategory.ENTERTAINMENT: {
            "merchants": [
                "netflix", "spotify", "prime video", "hotstar", "bookmyshow",
                "youtube premium", "sony liv", "zee5", "alt balaji",
                "movie", "cinema", "theatre"
            ],
            "keywords": [
                "entertainment", "movie", "cinema", "netflix", "spotify",
                "music", "video", "streaming", "subscription"
            ],
            "confidence": 0.94
        },
        TransactionCategory.UTILITIES: {
            "merchants": [
                "electricity", "water bill", "gas bill", "mahanagar gas",
                "tata power", "adani electricity", "bescom", "mseb",
                "utility", "power"
            ],
            "keywords": [
                "electricity", "water", "gas", "power", "utility",
                "mahanagar", "tata power", "adani"
            ],
            "confidence": 0.91
        },
        TransactionCategory.BILLS: {
            "merchants": [
                "credit card payment", "mobile bill", "internet bill",
                "broadband", "phone bill", "postpaid", "jio", "airtel",
                "vi", "bsnl", "act fibernet", "airtel fiber"
            ],
            "keywords": [
                "bill", "payment", "recharge", "mobile", "internet",
                "broadband", "phone", "credit card", "emi"
            ],
            "confidence": 0.88
        },
        TransactionCategory.HEALTHCARE: {
            "merchants": [
                "apollo", "pharmeasy", "netmeds", "1mg", "hospital",
                "clinic", "medical", "pharmacy", "doctor", "health",
                "diagnostic", "lab", "pathology"
            ],
            "keywords": [
                "medical", "pharmacy", "hospital", "doctor", "health",
                "medicine", "apollo", "pharmeasy", "netmeds", "diagnostic"
            ],
            "confidence": 0.93
        },
        TransactionCategory.EDUCATION: {
            "merchants": [
                "udemy", "coursera", "unacademy", "college", "university",
                "education", "school", "coaching", "byju", "vedantu",
                "skillshare", "pluralsight"
            ],
            "keywords": [
                "education", "course", "college", "university", "school",
                "coaching", "udemy", "coursera", "training", "learning"
            ],
            "confidence": 0.90
        },
        TransactionCategory.RENT: {
            "merchants": [
                "rent", "landlord", "housing rent", "flat rent",
                "apartment", "housing society", "maintenance"
            ],
            "keywords": [
                "rent", "landlord", "housing", "flat", "apartment",
                "maintenance", "society"
            ],
            "confidence": 0.89
        },
        TransactionCategory.TRAVEL: {
            "merchants": [
                "air india", "indigo", "spicejet", "goair", "vistara",
                "booking.com", "airbnb", "hotel", "resort", "travel",
                "trip", "vacation", "holiday"
            ],
            "keywords": [
                "travel", "hotel", "flight", "vacation", "holiday",
                "trip", "booking", "airbnb", "resort"
            ],
            "confidence": 0.91
        },
        TransactionCategory.SALARY: {
            "merchants": [
                "salary", "payroll", "employer", "company", "wages",
                "income", "paycheck"
            ],
            "keywords": [
                "salary", "payroll", "employer", "wages", "paycheck",
                "income credit"
            ],
            "confidence": 0.96
        },
        TransactionCategory.INVESTMENT: {
            "merchants": [
                "zerodha", "groww", "upstox", "mutual fund", "sip",
                "investment", "stock", "share", "trading", "demat",
                "kite", "smallcase"
            ],
            "keywords": [
                "investment", "mutual fund", "sip", "stock", "share",
                "trading", "zerodha", "groww", "upstox", "demat"
            ],
            "confidence": 0.94
        }
    }
    
    def __init__(self):
        pass
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for matching (lowercase, trim)."""
        if not text:
            return ""
        return text.strip().lower()
    
    def find_merchant_match(self, merchant: str, description: str) -> Optional[tuple]:
        """Find exact or strong merchant match."""
        normalized_merchant = self.normalize_text(merchant)
        normalized_description = self.normalize_text(description)
        
        for category, rules in self.CATEGORY_RULES.items():
            for rule_merchant in rules["merchants"]:
                normalized_rule = self.normalize_text(rule_merchant)
                
                # Exact merchant match
                if normalized_merchant == normalized_rule:
                    return (category, rules["confidence"], f"Exact merchant match: {rule_merchant}", rule_merchant)
                
                # Strong merchant keyword match in merchant
                if normalized_rule in normalized_merchant:
                    return (category, rules["confidence"] - 0.05, f"Merchant contains: {rule_merchant}", rule_merchant)
                
                # Strong merchant keyword match in description
                if normalized_rule in normalized_description:
                    return (category, rules["confidence"] - 0.08, f"Description contains: {rule_merchant}", rule_merchant)
        
        return None
    
    def find_keyword_match(self, description: str) -> Optional[tuple]:
        """Find keyword match in description."""
        normalized_description = self.normalize_text(description)
        
        for category, rules in self.CATEGORY_RULES.items():
            for keyword in rules["keywords"]:
                normalized_keyword = self.normalize_text(keyword)
                
                # Check if keyword is a separate word (not substring)
                words = normalized_description.split()
                if normalized_keyword in words:
                    return (category, rules["confidence"] - 0.15, f"Keyword match: {keyword}", keyword)
        
        return None
    
    def categorize_transaction(
        self,
        description: str,
        merchant: str,
        transaction_type: TransactionType,
        existing_category: Optional[TransactionCategory] = None,
        category_source: Optional[str] = None
    ) -> CategorizationResult:
        """
        Categorize a transaction based on description, merchant, and type.
        
        Args:
            description: Transaction description
            merchant: Extracted merchant name
            transaction_type: income or expense
            existing_category: Existing category if already set
            category_source: Source of existing category (manual, rule, default)
        
        Returns:
            CategorizationResult with category, confidence, and explanation
        """
        # Convert string category to enum if needed
        if existing_category and isinstance(existing_category, str):
            try:
                existing_category = TransactionCategory(existing_category)
            except ValueError:
                existing_category = None
        
        # If category is manually set by user, don't override
        if category_source == "manual" and existing_category:
            return CategorizationResult(
                category=existing_category,
                confidence=1.0,
                matched_rule="manual_override",
                reason="Manually set by user",
                source="manual"
            )
        
        # Special handling for salary - only for income
        if transaction_type == TransactionType.INCOME:
            normalized_desc = self.normalize_text(description)
            normalized_merchant = self.normalize_text(merchant)
            
            salary_keywords = ["salary", "payroll", "employer", "wages", "paycheck"]
            for keyword in salary_keywords:
                if keyword in normalized_desc or keyword in normalized_merchant:
                    return CategorizationResult(
                        category=TransactionCategory.SALARY,
                        confidence=0.96,
                        matched_rule=keyword,
                        reason=f"Income transaction with keyword: {keyword}",
                        source="rule"
                    )
        
        # Priority 1: Exact merchant match
        merchant_match = self.find_merchant_match(merchant, description)
        if merchant_match:
            category, confidence, reason, rule = merchant_match
            return CategorizationResult(
                category=category,
                confidence=confidence,
                matched_rule=rule,
                reason=reason,
                source="rule"
            )
        
        # Priority 2: Keyword match in description
        keyword_match = self.find_keyword_match(description)
        if keyword_match:
            category, confidence, reason, rule = keyword_match
            return CategorizationResult(
                category=category,
                confidence=confidence,
                matched_rule=rule,
                reason=reason,
                source="rule"
            )
        
        # Priority 3: Default to Other
        return CategorizationResult(
            category=TransactionCategory.OTHER,
            confidence=0.0,
            matched_rule="default",
            reason="No matching rule found",
            source="default"
        )


# Global categorizer instance
transaction_categorizer = TransactionCategorizer()
