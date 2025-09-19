# API Documentation - MVC Architecture

This document describes the API endpoints and the MVC architecture implementation.

## Architecture Overview

The application now follows a proper MVC (Model-View-Controller) architecture:

### Models (`app/models.py`)
- **User**: User authentication and authorization
- **Asset**: Fractional ownership assets
- **Fraction**: Individual asset fractions
- **Transaction**: Fraction trading transactions

### Services (`app/services/`)
Business logic layer that handles:
- **HealthService**: System health checks
- **UserService**: User management operations
- **AssetService**: Asset management operations
- **FractionService**: Fraction management operations
- **TransactionService**: Transaction management operations

### Controllers (`app/controllers/`)
HTTP request handling layer that:
- Validates incoming requests
- Calls appropriate services
- Handles errors and exceptions
- **HealthController**: Health check endpoints
- **UserController**: User-related endpoints
- **AssetController**: Asset-related endpoints
- **FractionController**: Fraction-related endpoints
- **TransactionController**: Transaction-related endpoints

### Views (`app/views/`)
Response formatting layer that:
- Formats data for JSON responses
- Handles error responses
- **HealthView**: Health check response formatting
- **UserView**: User response formatting
- **AssetView**: Asset response formatting
- **FractionView**: Fraction response formatting
- **TransactionView**: Transaction response formatting

### Routes (`app/routes/`)
URL routing layer that:
- Maps URLs to controller methods
- Handles HTTP methods (GET, POST, PUT, DELETE)
- **health.py**: Health check endpoints
- **users.py**: User management endpoints
- **assets.py**: Asset management endpoints
- **fractions.py**: Fraction management endpoints
- **transactions.py**: Transaction management endpoints

## API Endpoints

### Health Checks

#### GET `/health`
Basic health check endpoint.
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000000",
  "service": "API Backbone",
  "version": "1.0.0"
}
```

#### GET `/health/db`
Database connectivity health check.
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00.000000",
  "error": null
}
```

#### GET `/health/detailed`
Detailed system health check.
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000000",
  "service": "API Backbone",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "connected",
      "error": null
    }
  }
}
```

### Users

#### POST `/api/users`
Create a new user.
```json
{
  "user_name": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "is_manager": false
}
```

#### GET `/api/users/<user_id>`
Get user by ID.

#### GET `/api/users`
Get all users with pagination.
- Query parameters: `page`, `per_page`

#### PUT `/api/users/<user_id>`
Update user information.

#### DELETE `/api/users/<user_id>`
Delete a user.

#### GET `/api/users/managers`
Get all manager users.

### Assets

#### POST `/api/assets`
Create a new asset.
```json
{
  "asset_name": "Downtown Office Building",
  "total_unit": 1000,
  "unit_min": 1,
  "unit_max": 100,
  "total_value": "10000000"
}
```

#### GET `/api/assets/<asset_id>`
Get asset by ID.

#### GET `/api/assets`
Get all assets with pagination.
- Query parameters: `page`, `per_page`

#### PUT `/api/assets/<asset_id>`
Update asset information.

#### DELETE `/api/assets/<asset_id>`
Delete an asset.

#### GET `/api/assets/<asset_id>/fractions`
Get all fractions for an asset.

### Fractions

#### POST `/api/fractions`
Create a new fraction.
```json
{
  "asset_id": 1,
  "owner_id": 2,
  "units": 50,
  "is_active": true,
  "value_perunit": 10000
}
```

#### GET `/api/fractions/<fraction_id>`
Get fraction by ID.

#### GET `/api/fractions/owner/<owner_id>`
Get all fractions owned by a user.

#### GET `/api/fractions/asset/<asset_id>`
Get all fractions for an asset.

#### GET `/api/fractions/active`
Get all active fractions.

#### PUT `/api/fractions/<fraction_id>`
Update fraction information.

#### DELETE `/api/fractions/<fraction_id>`
Delete a fraction.

### Transactions

#### POST `/api/transactions`
Create a new transaction.
```json
{
  "fraction_id": 1,
  "unit_moved": 10,
  "transaction_type": "transfer",
  "from_owner_id": 1,
  "to_owner_id": 2
}
```

#### GET `/api/transactions/<transaction_id>`
Get transaction by ID.

#### GET `/api/transactions`
Get all transactions with pagination.
- Query parameters: `page`, `per_page`

#### GET `/api/transactions/fraction/<fraction_id>`
Get all transactions for a fraction.

#### GET `/api/transactions/user/<user_id>`
Get all transactions involving a user.

#### GET `/api/transactions/fraction/<fraction_id>/history`
Get transaction history for a fraction.

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "status_code": 400
}
```

## Benefits of MVC Architecture

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Maintainability**: Easy to modify and extend functionality
3. **Testability**: Each layer can be tested independently
4. **Reusability**: Services can be reused across different controllers
5. **Scalability**: Easy to add new features without affecting existing code
6. **Code Organization**: Clear structure makes the codebase easier to navigate

## Development Guidelines

1. **Models**: Define data structure and relationships
2. **Services**: Implement business logic and data operations
3. **Controllers**: Handle HTTP requests and call services
4. **Views**: Format responses and handle presentation logic
5. **Routes**: Map URLs to controller methods

This architecture ensures clean, maintainable, and scalable code that follows industry best practices.