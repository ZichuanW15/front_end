"""Portfolio service for managing user portfolio and transaction operations."""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, or_
from app import db
from app.models import Fraction, Asset, AssetValueHistory, Transaction


class PortfolioService:
    """Provide aggregated owning-fractions + user transaction history."""

    @staticmethod
    def user_owning_fractions(user_id: int) -> List[Dict[str, Any]]:
        """
        Return user's holding grouped by asset, including latest value & est. value.
        """
        # Total shares held for each asset
        rows = (
            db.session.query(
                Fraction.asset_id,
                func.sum(Fraction.units).label("units"),
            )
            .filter(Fraction.owner_id == user_id, Fraction.is_active.is_(True))
            .group_by(Fraction.asset_id)
            .all()
        )

        if not rows:
            return []

        # Find information of these assets
        asset_ids = [r.asset_id for r in rows]
        assets = {
            a.asset_id: a for a in Asset.query.filter(Asset.asset_id.in_(asset_ids)).all()
        }

        # Get the latest price for each asset
        result: List[Dict[str, Any]] = []
        for r in rows:
            aid = r.asset_id
            units = int(r.units or 0)
            latest = (
                AssetValueHistory.query
                .filter(AssetValueHistory.asset_id == aid)
                .order_by(AssetValueHistory.recorded_at.desc())
                .first()
            )
            latest_value = float(latest.value) if latest else float(assets[aid].total_value)

            result.append({
                "asset_id": aid,
                "asset_name": assets[aid].asset_name if aid in assets else None,
                "units": units,
                "latest_value": latest_value,
                "estimated_value": round(units * latest_value, 2),
            })
        return result

    @staticmethod
    def user_transactions(
        user_id: int,
        asset_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Transaction], int]:
        """
        Return user's related transactions (buy/sell/transfer), time-desc, with optional asset filter.
        """
        q = (
            db.session.query(Transaction)
            .join(Fraction, Transaction.fraction_id == Fraction.fraction_id)
            .filter(or_(
                Transaction.from_owner_id == user_id,
                Transaction.to_owner_id == user_id
            ))
        )
        if asset_id:
            q = q.filter(Fraction.asset_id == asset_id)

        q = q.order_by(Transaction.transaction_at.desc())
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total