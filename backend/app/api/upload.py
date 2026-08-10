from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.statement_processor import statement_processor
from app.services.transaction_service import transaction_service
from app.schemas.upload import StatementPreviewResponse, ConfirmImportRequest, ConfirmImportResponse
from app.schemas.transaction import TransactionCreate

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/statement", response_model=StatementPreviewResponse)
async def preview_statement(file: UploadFile = File(...)):
    """Preview uploaded bank statement before import."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Get existing transaction fingerprints for duplicate detection
        existing_fingerprints = set()
        try:
            existing_transactions, _ = await transaction_service.get_transactions(limit=10000)
            existing_fingerprints = {t.fingerprint if hasattr(t, 'fingerprint') else '' for t in existing_transactions}
        except Exception:
            # If we can't get existing transactions, continue without duplicate check
            pass
        
        # Process the statement
        result = statement_processor.process_statement(
            file_content=file_content,
            filename=file.filename,
            existing_fingerprints=existing_fingerprints
        )
        
        return StatementPreviewResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process statement: {str(e)}")


@router.post("/confirm", response_model=ConfirmImportResponse)
async def confirm_import(request: ConfirmImportRequest):
    """Confirm and import transactions from preview."""
    try:
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for transaction_data in request.transactions:
            # Skip duplicates and invalid transactions
            if transaction_data.is_duplicate or transaction_data.error:
                skipped_count += 1
                continue
            
            try:
                # Convert to TransactionCreate format
                transaction_create = TransactionCreate(
                    amount=transaction_data.amount,
                    transaction_type=transaction_data.transaction_type,
                    description=transaction_data.description,
                    merchant=transaction_data.merchant,
                    category=transaction_data.category,
                    date=transaction_data.date,
                    payment_method=transaction_data.payment_method,
                    notes=transaction_data.notes,
                    source=transaction_data.source,
                    fingerprint=transaction_data.fingerprint,
                    category_confidence=getattr(transaction_data, 'category_confidence', None),
                    category_source=getattr(transaction_data, 'category_source', None),
                    category_reason=getattr(transaction_data, 'category_reason', None)
                )
                
                # Create transaction with fingerprint and categorization data
                await transaction_service.create_transaction(
                    transaction_create,
                    fingerprint=transaction_data.fingerprint
                )
                imported_count += 1
            
            except Exception as e:
                errors.append(f"Failed to import transaction: {str(e)}")
                skipped_count += 1
        
        return ConfirmImportResponse(
            success=True,
            imported=imported_count,
            skipped=skipped_count,
            errors=errors
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import transactions: {str(e)}")
