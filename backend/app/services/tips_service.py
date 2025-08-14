from uuid import UUID
from typing import List
from app.models.tip import TipInDB, TipCreate

async def create_tip(db, user_id: UUID, tip_data: TipCreate) -> dict:
    """Create a new tip for a user"""
    tip = TipInDB(
        **tip_data.model_dump(),
        user_id=str(user_id)
    )
    
    # In a real application, you would integrate with the Venmo API here
    # and get a real transaction ID. For now, we'll simulate it.
    tip.transaction_id = f"venmo_{uuid.uuid4()}"
    
    # Convert to dict for MongoDB storage
    tip_dict = tip.model_dump(by_alias=True)
    tip_dict["id"] = str(tip_dict["id"])
    
    result = await db.tips.insert_one(tip_dict)
    tip_dict["_id"] = result.inserted_id
    
    return tip_dict

async def get_user_tipping_history(db, user_id: UUID) -> List[dict]:
    """Get all tips for a user"""
    cursor = db.tips.find({"user_id": str(user_id)}).sort("created_at", -1)
    tips = await cursor.to_list(length=None)
    return tips