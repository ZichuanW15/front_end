"""
Asset value history service: Query history and allow administrators to manually adjust values.
"""

from app import db
from app.models import AssetValueHistory, Asset, User
from datetime import datetime
from typing import Optional, List, Dict, Any



class AssetValueService:
    """Service class for asset value history operations."""
    # 1) Query the history of an asset over a period of time (in ascending order of time)
    @staticmethod
    def list_history(
        asset_id: int,
        dt_from: Optional[datetime] = None,
        dt_to: Optional[datetime] = None,
    ) -> List[AssetValueHistory]:
        q = AssetValueHistory.query.filter(AssetValueHistory.asset_id == asset_id)
        if dt_from:
            q = q.filter(AssetValueHistory.recorded_at >= dt_from)
        if dt_to:
            q = q.filter(AssetValueHistory.recorded_at <= dt_to)
        return q.order_by(AssetValueHistory.recorded_at.asc()).all()

    # 2) For administrators only: Add a new "manual adjustment" history record
    @staticmethod
    def add_adjustment(
        asset_id: int,
        value: float,
        adjusted_by: int,
        reason: str = "",
        recorded_at: Optional[datetime] = None,
    ) -> AssetValueHistory:
        # must be an administrator
        user = User.query.get(adjusted_by)
        if not user or not user.is_manager:
            raise PermissionError("Only manager can adjust asset values.")

        item = AssetValueHistory(
            asset_id = asset_id,
            value = value,
            recorded_at = datetime.utcnow(),
            source = "manual_adjust",
            adjusted_by = adjusted_by,
            adjustment_reason = reason,
        )
        db.session.add(item)

        # （可选）同步更新主表当前值，便于列表页快速显示
        asset = Asset.query.get(asset_id)
        if asset is not None:
            # 你们的 Asset.total_value 字段类型是 String，所以转成字符串存
            asset.total_value = str(value)

        db.session.commit()
        return item

    # 3) Get the latest value (sometimes the page needs to display the "current value")
    @staticmethod
    def latest_value(asset_id: int) -> Optional[AssetValueHistory]:
        return (
            AssetValueHistory.query.filter_by(asset_id=asset_id)
            .order_by(AssetValueHistory.recorded_at.desc())
            .first()
        )