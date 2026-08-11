from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse, TransactionListResponse
from app.services.transaction_service import transaction_service
from app.services.categorizer import transaction_categorizer
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        # For manual transactions, set category_source to manual
        if transaction.source.value == "manual":
            transaction.category_source = "manual"
        
        created_transaction = await transaction_service.create_transaction(
            transaction,
            user_id=str(current_user.id),
            fingerprint=transaction.fingerprint
        )
        return TransactionResponse(
            id=created_transaction.id,
            user_id=created_transaction.user_id,
            amount=created_transaction.amount,
            transaction_type=created_transaction.transaction_type,
            description=created_transaction.description,
            merchant=created_transaction.merchant,
            category=created_transaction.category,
            date=created_transaction.date,
            payment_method=created_transaction.payment_method,
            notes=created_transaction.notes,
            source=created_transaction.source,
            fingerprint=created_transaction.fingerprint,
            category_confidence=created_transaction.category_confidence,
            category_source=created_transaction.category_source,
            category_reason=created_transaction.category_reason,
            created_at=created_transaction.created_at,
            updated_at=created_transaction.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")


@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = Query("date", regex="^(date|amount)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user)
):
    try:
        parsed_start_date = datetime.fromisoformat(start_date) if start_date else None
        parsed_end_date = datetime.fromisoformat(end_date) if end_date else None
        
        sort_order_int = -1 if sort_order == "desc" else 1
        
        transactions, total = await transaction_service.get_transactions(
            user_id=str(current_user.id),
            skip=skip,
            limit=limit,
            search=search,
            category=category,
            transaction_type=transaction_type,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            sort_by=sort_by,
            sort_order=sort_order_int
        )
        
        return TransactionListResponse(
            transactions=[
                TransactionResponse(
                    id=t.id,
                    user_id=t.user_id,
                    amount=t.amount,
                    transaction_type=t.transaction_type,
                    description=t.description,
                    merchant=t.merchant,
                    category=t.category,
                    date=t.date,
                    payment_method=t.payment_method,
                    notes=t.notes,
                    source=t.source,
                    fingerprint=t.fingerprint,
                    category_confidence=t.category_confidence,
                    category_source=t.category_source,
                    category_reason=t.category_reason,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                ) for t in transactions
            ],
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transactions: {str(e)}")


@router.get("/categories/summary")
async def get_category_summary(current_user: User = Depends(get_current_user)):
    """Get total spending grouped by category for the logged in user (expense transactions only)"""
    try:
        transactions, _ = await transaction_service.get_transactions(user_id=str(current_user.id), limit=10000)
        
        # Filter expense transactions only
        expense_transactions = [t for t in transactions if t.transaction_type.value == "expense"]
        
        # Group by category
        category_totals = {}
        for transaction in expense_transactions:
            category = transaction.category.value
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += transaction.amount
        
        return category_totals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category summary: {str(e)}")


@router.post("/recategorize")
async def recategorize_transactions(current_user: User = Depends(get_current_user)):
    """Re-run categorization on logged-in user's transactions with category_source != 'manual'"""
    try:
        user_id_str = str(current_user.id)
        transactions, total = await transaction_service.get_transactions(user_id=user_id_str, limit=10000)
        
        processed = 0
        updated = 0
        unchanged = 0
        
        for transaction in transactions:
            if transaction.category_source == "manual":
                unchanged += 1
                continue
            
            processed += 1
            
            categorization_result = transaction_categorizer.categorize_transaction(
                description=transaction.description,
                merchant=transaction.merchant,
                transaction_type=transaction.transaction_type,
                existing_category=transaction.category,
                category_source=transaction.category_source
            )
            
            if categorization_result.category != transaction.category:
                update_data = {
                    "category": categorization_result.category,
                    "category_confidence": categorization_result.confidence,
                    "category_source": categorization_result.source,
                    "category_reason": categorization_result.reason
                }
                await transaction_service.update_transaction(transaction.id, update_data, user_id=user_id_str)
                updated += 1
            else:
                unchanged += 1
        
        return {
            "processed": processed,
            "updated": updated,
            "unchanged": unchanged
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recategorize transactions: {str(e)}")


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):
    transaction = await transaction_service.get_transaction(transaction_id, user_id=str(current_user.id))
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(
        id=transaction.id,
        user_id=transaction.user_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        description=transaction.description,
        merchant=transaction.merchant,
        category=transaction.category,
        date=transaction.date,
        payment_method=transaction.payment_method,
        notes=transaction.notes,
        source=transaction.source,
        fingerprint=transaction.fingerprint,
        category_confidence=transaction.category_confidence,
        category_source=transaction.category_source,
        category_reason=transaction.category_reason,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        if transaction_update.category is not None:
            transaction_update.category_source = "manual"
        
        updated_transaction = await transaction_service.update_transaction(
            transaction_id,
            transaction_update,
            user_id=str(current_user.id)
        )
        if not updated_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return TransactionResponse(
            id=updated_transaction.id,
            user_id=updated_transaction.user_id,
            amount=updated_transaction.amount,
            transaction_type=updated_transaction.transaction_type,
            description=updated_transaction.description,
            merchant=updated_transaction.merchant,
            category=updated_transaction.category,
            date=updated_transaction.date,
            payment_method=updated_transaction.payment_method,
            notes=updated_transaction.notes,
            source=updated_transaction.source,
            fingerprint=updated_transaction.fingerprint,
            category_confidence=updated_transaction.category_confidence,
            category_source=updated_transaction.category_source,
            category_reason=updated_transaction.category_reason,
            created_at=updated_transaction.created_at,
            updated_at=updated_transaction.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update transaction: {str(e)}")


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        success = await transaction_service.delete_transaction(transaction_id, user_id=str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete transaction: {str(e)}")
