import asyncio
import sys
import argparse
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.mongodb import mongodb
from app.services.user_service import user_service


async def migrate_data(target_email: str):
    print(f"Connecting to MongoDB database...")
    await mongodb.connect()
    db = mongodb.get_database()

    target_email_clean = target_email.lower().strip()
    user = await user_service.get_user_by_email(target_email_clean)
    if not user:
        print(f"Error: User with email '{target_email_clean}' not found!")
        print("Please register this user account first before running migration.")
        await mongodb.close()
        return

    user_id_str = str(user.id)
    print(f"Found target user: {user.email} (ID: {user_id_str})")

    # 1. Migrate transactions
    tx_query = {"$or": [{"user_id": "default_user"}, {"user_id": None}, {"user_id": {"$exists": False}}]}
    tx_count_before = await db.transactions.count_documents(tx_query)
    print(f"Found {tx_count_before} transactions matching un-assigned/default_user status.")

    if tx_count_before > 0:
        tx_result = await db.transactions.update_many(
            tx_query,
            {"$set": {"user_id": user_id_str}}
        )
        print(f"Successfully migrated {tx_result.modified_count} transactions to user ID {user_id_str}.")

    # 2. Migrate budgets
    b_query = {"$or": [{"user_id": "default_user"}, {"user_id": None}, {"user_id": {"$exists": False}}]}
    b_count_before = await db.budgets.count_documents(b_query)
    print(f"Found {b_count_before} budgets matching un-assigned/default_user status.")

    if b_count_before > 0:
        b_result = await db.budgets.update_many(
            b_query,
            {"$set": {"user_id": user_id_str}}
        )
        print(f"Successfully migrated {b_result.modified_count} budgets to user ID {user_id_str}.")

    print("\nMigration Completed Successfully! No existing data was deleted.")
    await mongodb.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate existing SpendSense default_user records to a target user.")
    parser.add_argument("--email", required=True, help="Registered email of the target user to receive existing data.")
    args = parser.parse_args()

    asyncio.run(migrate_data(args.email))
