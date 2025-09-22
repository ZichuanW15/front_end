"""
SQLAlchemy models for the API backbone.
These models match the provided PostgreSQL schema.
"""

from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app import db

<<<<<<< HEAD

class User(db.Model):
=======
# Use Flask-SQLAlchemy's Model base class
Base = db.Model


class User(Base):
>>>>>>> newrepo/frontend
    """User model for authentication and authorization."""
    __tablename__ = 'Users'
    
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_name = Column(String)
    created_at = Column(DateTime, nullable=False)
    is_manager = Column(Boolean, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    
    # Relationships
    fractions = relationship('Fraction', backref='owner')
    transactions_from = relationship('Transaction', foreign_keys='Transaction.from_owner_id', backref='from_owner')
    transactions_to = relationship('Transaction', foreign_keys='Transaction.to_owner_id', backref='to_owner')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_manager': self.is_manager,
            'email': self.email
        }
    
    def __repr__(self):
        return f'<User {self.user_name}>'


<<<<<<< HEAD
class Asset(db.Model):
=======
class Asset(Base):
>>>>>>> newrepo/frontend
    """Asset model for fractional ownership assets."""
    __tablename__ = 'Assets'
    
    asset_id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_name = Column(Text, nullable=False)
    total_unit = Column(BigInteger, nullable=False)
    unit_min = Column(BigInteger, nullable=False)
    unit_max = Column(BigInteger, nullable=False)
    total_value = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    fractions = relationship('Fraction', backref='asset')
<<<<<<< HEAD
=======
    transactions = relationship('Transaction', backref='asset')
>>>>>>> newrepo/frontend
    
    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'asset_name': self.asset_name,
            'total_unit': self.total_unit,
            'unit_min': self.unit_min,
            'unit_max': self.unit_max,
            'total_value': self.total_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Asset {self.asset_name}>'


<<<<<<< HEAD
class Fraction(db.Model):
=======
class Fraction(Base):
>>>>>>> newrepo/frontend
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
    
    def to_dict(self):
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


<<<<<<< HEAD
class Transaction(db.Model):
    """Transaction model for fraction trading."""
    __tablename__ = 'Transactions'
    
    transaction_id = Column(BigInteger, primary_key=True)
=======
class Transaction(Base):
    """Transaction model for fraction trading."""
    __tablename__ = 'Transactions'
    
    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_id = Column(BigInteger, ForeignKey('Assets.asset_id'), nullable=False)
>>>>>>> newrepo/frontend
    fraction_id = Column(BigInteger, ForeignKey('Fractions.fraction_id'), nullable=False)
    unit_moved = Column(BigInteger, nullable=False)
    transaction_type = Column(Text)
    transaction_at = Column(DateTime, nullable=False)
    from_owner_id = Column(BigInteger, ForeignKey('Users.user_id'), nullable=False)
    to_owner_id = Column(BigInteger, ForeignKey('Users.user_id'), nullable=False)
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
<<<<<<< HEAD
=======
            'asset_id': self.asset_id,
>>>>>>> newrepo/frontend
            'fraction_id': self.fraction_id,
            'unit_moved': self.unit_moved,
            'transaction_type': self.transaction_type,
            'transaction_at': self.transaction_at.isoformat() if self.transaction_at else None,
            'from_owner_id': self.from_owner_id,
            'to_owner_id': self.to_owner_id
        }
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'