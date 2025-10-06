"""
SQLAlchemy models for the API backbone.
These models match the provided PostgreSQL schema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, ForeignKey, BigInteger, Numeric
from sqlalchemy.orm import relationship
from .database import db

# Use Flask-SQLAlchemy's Model base class
Base = db.Model


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = 'Users'
    
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_name = Column(String)
    created_at = Column(DateTime, nullable=False)
    is_manager = Column(Boolean, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    fractions = relationship('Fraction', backref='owner')
    transactions_from = relationship('Transaction', foreign_keys='Transaction.from_owner_id', backref='from_owner')
    transactions_to = relationship('Transaction', foreign_keys='Transaction.to_owner_id', backref='to_owner')
    offers = relationship('Offer', backref='user')
    
    def to_dict(self):
        """Convert user to dictionary representation."""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_manager': self.is_manager,
            'email': self.email,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return f'<User {self.user_name}>'


class Asset(Base):
    """Asset model for fractional ownership assets."""
    __tablename__ = 'Assets'
    
    asset_id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_name = Column(Text, nullable=False)
    asset_description = Column(Text)
    total_unit = Column(BigInteger, nullable=False)
    unit_min = Column(BigInteger, nullable=False)
    unit_max = Column(BigInteger, nullable=False)
    total_value = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    fractions = relationship('Fraction', backref='asset')
    
    def to_dict(self):
        """Convert asset to dictionary representation."""
        return {
            'asset_id': self.asset_id,
            'asset_name': self.asset_name,
            'asset_description': self.asset_description,
            'total_unit': self.total_unit,
            'unit_min': self.unit_min,
            'unit_max': self.unit_max,
            'total_value': self.total_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Asset {self.asset_name}>'


class Fraction(Base):
    """Fraction model for individual asset fractions."""
    __tablename__ = 'Fractions'
    
    fraction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_id = Column(BigInteger, ForeignKey('Assets.asset_id'), nullable=False)
    owner_id = Column(BigInteger, ForeignKey('Users.user_id'))
    parent_fraction_id = Column(BigInteger, ForeignKey('Fractions.fraction_id'))
    units = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    value_perunit = Column(BigInteger)
    
    # Relationships
    parent_fraction = relationship('Fraction', remote_side='Fraction.fraction_id', backref='child_fractions')
    transactions = relationship('Transaction', backref='fraction')
    offers = relationship('Offer', backref='fraction')
    
    def to_dict(self):
        """Convert fraction to dictionary representation."""
        return {
            'fraction_id': self.fraction_id,
            'asset_id': self.asset_id,
            'owner_id': self.owner_id,
            'parent_fraction_id': self.parent_fraction_id,
            'units': self.units,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'value_perunit': self.value_perunit
        }
    
    def __repr__(self):
        return f'<Fraction {self.fraction_id}>'
    
class Offer(Base):
    """Offer model for buying/selling fractions."""
    __tablename__ = 'Offers'
    
    offer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_id = Column(BigInteger, ForeignKey('Assets.asset_id'), nullable=False)
    fraction_id = Column(BigInteger, ForeignKey('Fractions.fraction_id'))
    user_id = Column(BigInteger, ForeignKey('Users.user_id'), nullable=False)
    is_buyer = Column(Boolean, nullable=False)
    units = Column(BigInteger, nullable=False)
    price_perunit = Column(Numeric(18, 2), nullable=True)
    create_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, nullable=False, default=True)
    
    def to_dict(self):
        """Convert offer to dictionary representation."""
        return {
            'offer_id': self.offer_id,
            'asset_id': self.asset_id,
            'fraction_id': self.fraction_id,
            'user_id': self.user_id,
            'is_buyer': self.is_buyer,
            'units': self.units,
            'price_perunit': float(self.price_perunit) if self.price_perunit else None,
            'is_valid': self.is_valid,
            'create_at': self.create_at.isoformat() if self.create_at else None
        }
    
    
    def __repr__(self):
        return f'<Offer {self.offer_id}>'


class Transaction(Base):
    """Transaction model for fraction trading."""
    __tablename__ = 'Transactions'
    
    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    fraction_id = Column(BigInteger, ForeignKey('Fractions.fraction_id'), nullable=False)
    unit_moved = Column(BigInteger, nullable=False)
    transaction_type = Column(Text)
    transaction_at = Column(DateTime, nullable=False)
    from_owner_id = Column(BigInteger, ForeignKey('Users.user_id'), nullable=False)
    to_owner_id = Column(BigInteger, ForeignKey('Users.user_id'), nullable=False)
    offer_id = Column(BigInteger, ForeignKey('Offers.offer_id'), nullable=False)
    price_perunit = Column(Numeric(18, 2), nullable=False)
    
    
    offer = relationship('Offer', backref='transactions')
    
    def to_dict(self):
        """Convert transaction to dictionary representation."""
        return {
            'transaction_id': self.transaction_id,
            'fraction_id': self.fraction_id,
            'unit_moved': self.unit_moved,
            'transaction_type': self.transaction_type,
            'transaction_at': self.transaction_at.isoformat() if self.transaction_at else None,
            'from_owner_id': self.from_owner_id,
            'to_owner_id': self.to_owner_id,
            'offer_id': self.offer_id,
            'price_perunit': float(self.price_perunit) if self.price_perunit else None
        }
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'



class AssetValueHistory(Base):
    """Asset value history model for tracking asset value changes."""
    __tablename__ = 'AssetValueHistory'

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_id    = Column(BigInteger, ForeignKey('Assets.asset_id'), nullable=False)
    value       = Column(Numeric(18, 2), nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    source      = Column(Text, default='system')
    adjusted_by = Column(BigInteger, ForeignKey('Users.user_id'))
    adjustment_reason = Column(Text)

    # 
    asset     = relationship('Asset', backref='value_history')
    adjuster  = relationship('User', foreign_keys=[adjusted_by])

    def to_dict(self):
        """Convert asset value history to dictionary representation."""
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'value': float(self.value),
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'source': self.source,
            'adjusted_by': self.adjusted_by,
            'reason': self.adjustment_reason,
        }
    
    def __repr__(self):
        """String representation of asset value history."""
        return f'<AssetValueHistory {self.id}>'