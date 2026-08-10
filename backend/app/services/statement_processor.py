import pandas as pd
import hashlib
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from io import BytesIO
from app.schemas.transaction import TransactionType, TransactionCategory, TransactionSource
from app.services.categorizer import transaction_categorizer


class StatementProcessor:
    # Column mapping for different bank statement formats
    COLUMN_ALIASES = {
        'date': ['date', 'transaction date', 'txn date', 'value date', 'posting date', 'transaction_date', 'txn_date', 'value_date', 'posting_date'],
        'description': ['description', 'narration', 'details', 'transaction details', 'transaction description', 'narration', 'particulars', 'remarks'],
        'debit': ['debit', 'withdrawal', 'withdrawals', 'dr', 'debit amount', 'withdrawal amount', 'outflow'],
        'credit': ['credit', 'deposit', 'deposits', 'cr', 'credit amount', 'deposit amount', 'inflow'],
        'amount': ['amount', 'transaction amount', 'txn amount', 'transaction_amount', 'txn_amount']
    }
    
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        pass
    
    def validate_file(self, filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """Validate file type and size."""
        if not filename:
            return False, "No file provided"
        
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type. Please upload CSV or XLSX. Got: {file_ext}"
        
        if file_size == 0:
            return False, "The uploaded file is empty"
        
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size is {self.MAX_FILE_SIZE / (1024*1024)}MB"
        
        return True, None
    
    def read_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Read CSV or XLSX file."""
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(BytesIO(file_content))
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            if df.empty:
                raise ValueError("File contains no data")
            
            return df
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")
    
    def normalize_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detect and normalize column names."""
        # Convert column names to lowercase and strip whitespace
        df.columns = df.columns.str.strip().str.lower()
        
        column_mapping = {}
        found_columns = set()
        
        # Try to map columns to our standard names
        for standard_name, aliases in self.COLUMN_ALIASES.items():
            for col in df.columns:
                if col in aliases or col.replace('_', ' ') in aliases or col.replace(' ', '_') in aliases:
                    column_mapping[col] = standard_name
                    found_columns.add(standard_name)
                    break
        
        # Check if we have at least date and description
        if 'date' not in found_columns:
            raise ValueError("Could not detect 'Date' column. Please ensure your file has a date column.")
        
        if 'description' not in found_columns:
            raise ValueError("Could not detect 'Description' column. Please ensure your file has a description column.")
        
        # Check if we have amount information (either amount column or debit/credit columns)
        if 'amount' not in found_columns and 'debit' not in found_columns and 'credit' not in found_columns:
            raise ValueError("Could not detect amount information. Please ensure your file has Amount, Debit, or Credit columns.")
        
        return column_mapping
    
    def parse_date(self, date_value) -> Optional[datetime]:
        """Parse date from various formats."""
        if pd.isna(date_value):
            return None
        
        try:
            # Try pandas date parsing first
            if isinstance(date_value, str):
                date_value = date_value.strip()
            
            parsed_date = pd.to_datetime(date_value, errors='coerce')
            
            if pd.isna(parsed_date):
                return None
            
            return parsed_date.to_pydatetime()
        except Exception:
            return None
    
    def parse_amount(self, amount_value) -> Optional[float]:
        """Parse amount from various formats."""
        if pd.isna(amount_value):
            return None
        
        try:
            # Remove currency symbols and commas
            if isinstance(amount_value, str):
                amount_value = amount_value.replace(',', '').replace('₹', '').replace('$', '').replace('€', '').strip()
            
            amount = float(amount_value)
            
            if amount == 0:
                return None
            
            return abs(amount)  # Always return positive amount
        except Exception:
            return None
    
    def determine_transaction_type(self, debit: Optional[float], credit: Optional[float], amount: Optional[float]) -> TransactionType:
        """Determine if transaction is income or expense."""
        # If we have separate debit/credit columns
        if debit is not None and debit > 0:
            return TransactionType.EXPENSE
        if credit is not None and credit > 0:
            return TransactionType.INCOME
        
        # If we have a single amount column with sign
        if amount is not None:
            # Try to determine from original value (before abs)
            # This is handled in the main processing function
            return TransactionType.EXPENSE  # Default to expense, will be corrected if needed
        
        return TransactionType.EXPENSE  # Default
    
    def clean_description(self, description: str) -> str:
        """Clean transaction description."""
        if pd.isna(description) or not description:
            return "Unknown Transaction"
        
        # Convert to string and strip
        desc = str(description).strip()
        
        # Remove extra whitespace
        desc = ' '.join(desc.split())
        
        # Remove special characters but keep useful info
        # Keep alphanumeric, spaces, and common punctuation
        import re
        desc = re.sub(r'[^\w\s\-.,/@#]', '', desc)
        
        return desc.upper() if desc else "Unknown Transaction"
    
    def extract_merchant(self, description: str) -> str:
        """Extract merchant from description."""
        if not description or description == "Unknown Transaction":
            return "Unknown"
        
        # Simple extraction: take first word or first few words
        words = description.split()
        
        if not words:
            return "Unknown"
        
        # Common patterns to identify merchant
        # If description has numbers, merchant is usually before the number
        for i, word in enumerate(words):
            if word.isdigit() and i > 0:
                return ' '.join(words[:i])
        
        # If no numbers, take first 2-3 words
        if len(words) >= 3:
            return ' '.join(words[:3])
        elif len(words) >= 2:
            return ' '.join(words[:2])
        else:
            return words[0]
    
    def create_transaction_fingerprint(self, date: datetime, amount: float, description: str, transaction_type: str) -> str:
        """Create a unique fingerprint for duplicate detection."""
        fingerprint_str = f"{date.isoformat()}|{amount}|{description}|{transaction_type}"
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def process_row(self, row: pd.Series, column_mapping: Dict[str, str], original_df: pd.DataFrame) -> Dict:
        """Process a single row into transaction format."""
        # Get values using column mapping
        date_value = row.get(column_mapping.get('date', 'date'))
        description_value = row.get(column_mapping.get('description', 'description'))
        debit_value = row.get(column_mapping.get('debit', 'debit'))
        credit_value = row.get(column_mapping.get('credit', 'credit'))
        amount_value = row.get(column_mapping.get('amount', 'amount'))
        
        # Parse date
        parsed_date = self.parse_date(date_value)
        if not parsed_date:
            return None
        
        # Parse amounts
        parsed_debit = self.parse_amount(debit_value)
        parsed_credit = self.parse_amount(credit_value)
        parsed_amount = self.parse_amount(amount_value)
        
        # Determine final amount and type
        final_amount = None
        final_type = TransactionType.EXPENSE
        
        if parsed_amount is not None:
            # Check if original amount value was negative
            if isinstance(amount_value, (int, float)) and amount_value < 0:
                final_type = TransactionType.EXPENSE
            elif isinstance(amount_value, str) and amount_value.startswith('-'):
                final_type = TransactionType.EXPENSE
            elif isinstance(amount_value, str) and amount_value.startswith('+'):
                final_type = TransactionType.INCOME
            else:
                # Default to expense for positive amounts
                final_type = TransactionType.EXPENSE
            final_amount = parsed_amount
        elif parsed_debit is not None:
            final_amount = parsed_debit
            final_type = TransactionType.EXPENSE
        elif parsed_credit is not None:
            final_amount = parsed_credit
            final_type = TransactionType.INCOME
        else:
            return None  # No valid amount found
        
        # Clean description
        cleaned_description = self.clean_description(description_value)
        
        # Extract merchant
        merchant = self.extract_merchant(cleaned_description)
        
        # Categorize transaction
        categorization_result = transaction_categorizer.categorize_transaction(
            description=cleaned_description,
            merchant=merchant,
            transaction_type=final_type
        )
        
        # Create transaction
        transaction = {
            'date': parsed_date,
            'amount': final_amount,
            'transaction_type': final_type,
            'description': cleaned_description,
            'merchant': merchant,
            'category': categorization_result.category,
            'payment_method': 'Bank',
            'notes': '',
            'source': TransactionSource.IMPORTED,
            'fingerprint': self.create_transaction_fingerprint(parsed_date, final_amount, cleaned_description, final_type.value),
            'category_confidence': categorization_result.confidence,
            'category_source': categorization_result.source,
            'category_reason': categorization_result.reason,
            'is_duplicate': False,
            'error': None
        }
        
        return transaction
    
    def process_statement(self, file_content: bytes, filename: str, existing_fingerprints: set = None) -> Dict:
        """Process entire bank statement."""
        if existing_fingerprints is None:
            existing_fingerprints = set()
        
        # Validate file
        is_valid, error = self.validate_file(filename, len(file_content))
        if not is_valid:
            return {
                'success': False,
                'error': error,
                'total_rows': 0,
                'valid_rows': 0,
                'invalid_rows': 0,
                'duplicate_rows': 0,
                'transactions': [],
                'errors': []
            }
        
        # Read file
        try:
            df = self.read_file(file_content, filename)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_rows': 0,
                'valid_rows': 0,
                'invalid_rows': 0,
                'duplicate_rows': 0,
                'transactions': [],
                'errors': [str(e)]
            }
        
        total_rows = len(df)
        
        # Normalize columns
        try:
            column_mapping = self.normalize_columns(df)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_rows': total_rows,
                'valid_rows': 0,
                'invalid_rows': total_rows,
                'duplicate_rows': 0,
                'transactions': [],
                'errors': [str(e)]
            }
        
        # Process each row
        transactions = []
        errors = []
        file_fingerprints = set()
        
        for idx, row in df.iterrows():
            try:
                transaction = self.process_row(row, column_mapping, df)
                
                if transaction is None:
                    errors.append(f"Row {idx + 2}: Could not process - missing required data")
                    continue
                
                # Check for duplicates within the file
                if transaction['fingerprint'] in file_fingerprints:
                    transaction['is_duplicate'] = True
                    transaction['error'] = 'Duplicate within file'
                
                # Check for duplicates with existing transactions
                if transaction['fingerprint'] in existing_fingerprints:
                    transaction['is_duplicate'] = True
                    transaction['error'] = 'Duplicate with existing transaction'
                
                file_fingerprints.add(transaction['fingerprint'])
                transactions.append(transaction)
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        valid_rows = len([t for t in transactions if not t['is_duplicate']])
        invalid_rows = len(errors)
        duplicate_rows = len([t for t in transactions if t['is_duplicate']])
        
        return {
            'success': True,
            'error': None,
            'total_rows': total_rows,
            'valid_rows': valid_rows,
            'invalid_rows': invalid_rows,
            'duplicate_rows': duplicate_rows,
            'transactions': transactions,
            'errors': errors
        }


statement_processor = StatementProcessor()
