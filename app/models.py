from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    is_manager = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(64))
    username = db.Column(db.String(32), unique=True)
    create_time = db.Column(db.DateTime)
    
    # Relationships
    submitted_assets = db.relationship('Asset', foreign_keys='Asset.submitted_by_users_user_id', backref='submitter')
    approved_assets = db.relationship('Asset', foreign_keys='Asset.approved_by_users_user_id', backref='approver')
    ownerships = db.relationship('Ownership', backref='user')
    transactions_from = db.relationship('Transaction', foreign_keys='Transaction.from_users_user_id', backref='from_user')
    transactions_to = db.relationship('Transaction', foreign_keys='Transaction.to_users_user_id', backref='to_user')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'is_manager': self.is_manager,
            'email': self.email,
            'username': self.username,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }

class Asset(db.Model):
    __tablename__ = 'assets'
    
    asset_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(255))
    max_fractions = db.Column(db.Integer)
    min_fractions = db.Column(db.Integer)
    available_fractions = db.Column(db.Integer)
    submitted_by_users_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), db.CheckConstraint("status IN ('draft','pending','approved','rejected','archived')"))
    approved_at = db.Column(db.DateTime)
    approved_by_users_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    # Relationships
    fractions = db.relationship('Fraction', backref='asset')
    ownerships = db.relationship('Ownership', backref='asset')
    transactions = db.relationship('Transaction', backref='asset')
    value_history = db.relationship('ValueHistory', backref='asset')
    
    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'description': self.description,
            'max_fractions': self.max_fractions,
            'min_fractions': self.min_fractions,
            'available_fractions': self.available_fractions,
            'submitted_by_users_user_id': self.submitted_by_users_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by_users_user_id': self.approved_by_users_user_id
        }

class Fraction(db.Model):
    __tablename__ = 'fractions'
    
    fraction_id = db.Column(db.Integer, primary_key=True)
    assets_asset_id = db.Column(db.Integer, db.ForeignKey('assets.asset_id'))
    fraction_no = db.Column(db.Integer)
    fraction_value = db.Column(db.Numeric(12, 2))
    
    # Relationships
    ownerships = db.relationship('Ownership', backref='fraction')
    transactions = db.relationship('Transaction', backref='fraction')
    
    def to_dict(self):
        return {
            'fraction_id': self.fraction_id,
            'assets_asset_id': self.assets_asset_id,
            'fraction_no': self.fraction_no,
            'fraction_value': float(self.fraction_value) if self.fraction_value else 0.0
        }

class Ownership(db.Model):
    __tablename__ = 'ownership'
    
    users_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    fractions_fraction_id = db.Column(db.Integer, db.ForeignKey('fractions.fraction_id'), primary_key=True)
    fractions_assets_asset_id = db.Column(db.Integer, db.ForeignKey('assets.asset_id'))
    acquired_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'users_user_id': self.users_user_id,
            'fractions_fraction_id': self.fractions_fraction_id,
            'fractions_assets_asset_id': self.fractions_assets_asset_id,
            'acquired_at': self.acquired_at.isoformat() if self.acquired_at else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2))
    currency = db.Column(db.String(3))
    trade_time = db.Column(db.DateTime)
    notes = db.Column(db.String(500))
    from_users_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    to_users_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    fractions_fraction_id = db.Column(db.Integer, db.ForeignKey('fractions.fraction_id'))
    fractions_assets_asset_id = db.Column(db.Integer, db.ForeignKey('assets.asset_id'))
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'currency': self.currency,
            'trade_time': self.trade_time.isoformat() if self.trade_time else None,
            'notes': self.notes,
            'from_users_user_id': self.from_users_user_id,
            'to_users_user_id': self.to_users_user_id,
            'fractions_fraction_id': self.fractions_fraction_id,
            'fractions_assets_asset_id': self.fractions_assets_asset_id
        }

class ValueHistory(db.Model):
    __tablename__ = 'valuehistory'
    
    value_id = db.Column(db.String(45), primary_key=True)
    assets_asset_id = db.Column(db.Integer, db.ForeignKey('assets.asset_id'))
    asset_value = db.Column(db.Integer)
    update_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'value_id': self.value_id,
            'assets_asset_id': self.assets_asset_id,
            'asset_value': self.asset_value,
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }