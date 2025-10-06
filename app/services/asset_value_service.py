"""
Asset value history service: Query history and allow administrators to manually adjust values.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.database import db
from app.models import AssetValueHistory, Asset, User


class AssetValueService:
    """Service class for asset value history operations."""
    @staticmethod
    def list_history(
        asset_id: int,
        dt_from: Optional[datetime] = None,
        dt_to: Optional[datetime] = None,
    ) -> List[AssetValueHistory]:
        """
        Query the history of an asset over a period of time (in ascending order of time).
        
        Args:
            asset_id: Asset ID to query history for
            dt_from: Start date filter (optional)
            dt_to: End date filter (optional)
            
        Returns:
            List of AssetValueHistory records
        """
        q = AssetValueHistory.query.filter(AssetValueHistory.asset_id == asset_id)
        if dt_from:
            q = q.filter(AssetValueHistory.recorded_at >= dt_from)
        if dt_to:
            q = q.filter(AssetValueHistory.recorded_at <= dt_to)
        return q.order_by(AssetValueHistory.recorded_at.asc()).all()

    @staticmethod
    def add_adjustment(
        asset_id: int,
        value: float,
        adjusted_by: int,
        reason: str = "",
        recorded_at: Optional[datetime] = None,
    ) -> AssetValueHistory:
        """
        For administrators only: Add a new "manual adjustment" history record.
        
        Args:
            asset_id: Asset ID to adjust
            value: New asset value
            adjusted_by: User ID of the administrator making the adjustment
            reason: Reason for the adjustment (optional)
            recorded_at: Timestamp for the adjustment (optional, defaults to now)
            
        Returns:
            Created AssetValueHistory record
            
        Raises:
            PermissionError: If user is not a manager
        """
        # must be an administrator
        user = User.query.get(adjusted_by)
        if not user or not user.is_manager:
            raise PermissionError("Only manager can adjust asset values.")

        item = AssetValueHistory(
            asset_id = asset_id,
            value = value,
            recorded_at = recorded_at if recorded_at else datetime.utcnow(),
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

    @staticmethod
    def latest_value(asset_id: int) -> Optional[AssetValueHistory]:
        """
        Get the latest value for an asset.
        
        Args:
            asset_id: Asset ID to get latest value for
            
        Returns:
            Latest AssetValueHistory record or None if not found
        """
        return (
            AssetValueHistory.query.filter_by(asset_id=asset_id)
            .order_by(AssetValueHistory.recorded_at.desc())
            .first()
        )