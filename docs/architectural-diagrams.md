# Architectural & Workflow Diagrams

## Table of Contents
- [System Architecture](#system-architecture)
- [Data Flow Architecture](#data-flow-architecture)
- [Forecasting Process Flow](#forecasting-process-flow)
- [Order Management Flow](#order-management-flow)
- [Auto-Ordering Workflow](#auto-ordering-workflow)
- [User Authentication Flow](#user-authentication-flow)
- [Inventory Management Flow](#inventory-management-flow)
- [API Interaction Diagram](#api-interaction-diagram)
- [ML Model Training Flow](#ml-model-training-flow)
- [Security Architecture](#security-architecture)

## System Architecture

### High-Level Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   LOAD BALANCER                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               TRAFFIC DISTRIBUTION                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│     WEB TRAFFIC                    │           API TRAFFIC                              │
│   (Static Content)                │        (Dynamic Requests)                          │
│                                   │                                                    │
│   ┌─────────────────────────────┐  │   ┌──────────────────────────────────────────────┐ │
│   │                             │  │   │                                              │ │
│   │         NGINX               │  │   │         FASTAPI                              │ │
│   │    (Static Content)         │  │   │      (Business Logic)                        │ │
│   │                             │  │   │                                              │ │
│   └─────────────────────────────┘  │   └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       MICROSERVICES INFRASTRUCTURE                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │             │  │             │  │                 │  │                 │          │
│  │  DATABASE   │  │   CACHE     │  │  ML SERVICE     │  │  FILE STORAGE   │          │
│  │ (PostgreSQL) │  │   (Redis)   │  │ (Forecasting)   │  │   (MinIO)       │          │
│  │             │  │             │  │                 │  │                 │          │
│  └─────────────┘  └─────────────┘  └─────────────────┘  └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────────────┐
                         │        MONITORING           │
                         │   (Prometheus + Grafana)    │
                         └─────────────────────────────┘
```

### Component Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  FRONTEND ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                       │
│  │     BROWSER     │  │   QUASAR UI     │  │  STATE MGMT     │                       │
│  │   (Client)      │  │   (Material)    │  │   (Pinia)       │                       │
│  │                 │  │                 │  │                 │                       │
│  │  <html>, <css>  │  │  Components,    │  │  User Sessions, │                       │
│  │  Rendering      │  │  Layouts,       │  │  App State      │                       │
│  │                 │  │  Routing        │  │                 │                       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                       │
│         │                       │                       │                              │
│         ▼                       ▼                       ▼                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                       │
│  │   API CALLS     │  │   CHARTS        │  │   UTILITIES     │                       │
│  │   (Axios)       │  │   (Chart.js)    │  │   (Helpers)     │                       │
│  │                 │  │                 │  │                 │                       │
│  │  REST Calls to  │  │  Forecasting    │  │  Validation,    │                       │
│  │  Backend API    │  │  Visualizations │  │  Formatting     │                       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  BACKEND ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                       │
│  │   FASTAPI       │  │  ML SERVICES    │  │   AUTH MIDDLEWARE│                       │
│  │   (Gateway)     │  │   (AI/ML)       │  │   (JWT, RBAC)   │                       │
│  │                 │  │                 │  │                 │                       │
│  │  API Routes     │  │  Forecasting    │  │  Authentication │                       │
│  │  Validation     │  │  Predictions    │  │  Authorization  │                       │
│  │  Request/Resp   │  │  Analytics      │  │  Security       │                       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                       │
│         │                      │                        │                              │
│         ▼                      ▼                        ▼                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                       │
│  │ DATABASE LAYER  │  │  ML PROCESSING  │  │  CACHE LAYER    │                       │
│  │ (SQLAlchemy)    │  │ (Pandas, SkLearn)│ │   (Redis)       │                       │
│  │                 │  │                 │  │                 │                       │
│  │  ORM Mapping    │  │  Data Modeling  │  │  Request Caching│                       │
│  │  Transactions   │  │  Predictions    │  │  Session Store  │                       │
│  │  Connections    │  │  Analytics      │  │  Rate Limiting  │                       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### Core System Components
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  SYSTEM COMPONENTS                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                   WEB APPLICATION                              │  │
│  ├─────────────────────────────────────────────────────────────────────────────────┤  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  │                              │  │
│  │  │  │   FRONTEND      │  │   BACKEND       │  │                              │  │
│  │  │  │  (Vue/Quasar)   │  │  (FastAPI)      │  │                              │  │
│  │  │  └─────────────────┘  └─────────────────┘  │                              │  │
│  │  │         │                      │            │                              │  │
│  │  │         ▼                      ▼            │                              │  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  │                              │  │
│  │  │  │   UI LAYERS     │  │  API LAYERS     │  │                              │  │
│  │  │  │ • Templates     │  │ • Controllers   │  │                              │  │
│  │  │  │ • Views         │  │ • Services      │  │                              │  │
│  │  │  │ • Components    │  │ • Validators    │  │                              │  │
│  │  │  └─────────────────┘  └─────────────────┘  │                              │  │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │  │                              DATA LAYERS                                        │  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │  │
│  │  │  │   DATABASE      │  │   ML LAYERS     │  │   CACHES        │              │  │
│  │  │  │ • PostgreSQL    │  │ • Forecasting   │  │ • Redis         │              │  │
│  │  │  │ • Models        │  │ • Predictions   │  │ • Sessions      │              │  │
│  │  │  │ • Migrations    │  │ • Analytics     │  │ • Rate Limits   │              │  │
│  │  │  └─────────────────┘  └─────────────────┘  └─────────────────┘              │  │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘  │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Forecasting Process Flow

### ML/Analytics Pipeline
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            ML/AI PIPELINE ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   DATA INPUT    │    │   PROCESSING    │    │   ML MODEL      │                  │
│  │   SOURCES       │───▶│   PIPELINE      │───▶│   TRAINING      │                  │
│  │ • Sales Data    │    │ • Cleaning      │    │ • Scikit-learn  │                  │
│  │ • Seasonal Patt │    │ • Transform     │    │ • Predictions   │                  │
│  │ • Historic      │    │ • Feature Eng   │    │ • Analytics     │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│                                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   OUTPUT        │◀───│   DECISION      │◀───│   FORECASTING   │                  │
│  │   ACTIONS       │    │   ENGINE        │    │   MODELS        │                  │
│  │ • Auto Orders   │    │ • Thresholds    │    │ • Trend Anal    │                  │
│  │ • Alerts        │    │ • Triggers      │    │ • Seasonal Adj  │                  │
│  │ • Notifications │    │ • Logic         │    │ • Confidence    │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Order Management Flow

### Order Processing Workflow
```
Start: User places an order
    ↓
Validate order data (products available, quantities, pricing)
    ↓
Calculate totals (subtotals, taxes, shipping, discounts)
    ↓
Process payment (if applicable)
    ↓
Create order record in database
    ↓
Update inventory (reduce stock levels)
    ↓
Send order confirmation to customer
    ↓
Notify warehouse/shipping department
    ↓
[Conditional: Physical vs Digital Products]
    ↓
Physical: Prepare for shipping → Generate shipping label → Ship package → Update tracking
    ↓
Digital: Generate download links → Send access credentials
    ↓
Update order status (Processing → Shipped → Delivered)
    ↓
End: Order fulfilled
```

## Auto-Ordering Workflow

### Automated Reordering Process
```
Start: System checks inventory thresholds daily
    ↓
For each product in inventory
    ↓
[Is current_stock ≤ minimum_threshold?]
    ↓ Yes
        ↓
    [Is forecasted_demand > current_stock?]
        ↓ Yes
        ↓
    Check auto-order settings for product
        ↓
    [Is auto-ordering enabled for this product?]
        ↓ Yes
        ↓
    Calculate optimal order quantity based on:
    - Forecasted demand for next 30 days
    - Current stock level
    - Lead time until delivery
    - Supplier minimum order quantities
        ↓
    Generate purchase order with calculated quantity
        ↓
    Send purchase order to preferred supplier
        ↓
    Update system with order status and expected delivery
        ↓
    End: Auto-order processed
        ↓
    No → Continue to next product
```

## User Authentication Flow

### Login and Authentication Sequence
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │   Frontend  │    │   Backend   │    │  Database   │
└─────┬───────┘    └─────┬───────┘    └─────┬───────┘    └─────┬───────┘
      │                  │                  │                  │
      │ Login            │                  │                  │
      │─────────────────▶│ Validate Input   │                  │
      │                  │─────────────────▶│ Check Username   │
      │                  │                  │─────────────────▶│
      │                  │                  │ Verify Unique    │
      │                  │                  │◀─────────────────│
      │                  │ Hash Password    │ Create User      │
      │                  │─────────────────▶│─────────────────▶│
      │                  │                  │ Store Encrypted  │
      │                  │                  │◀─────────────────│
      │                  │ Return Success   │                  │
      │◀─────────────────│─────────────────▶│                  │
      │ Login            │                  │                  │
      │─────────────────▶│ Validate Creds   │                  │
      │                  │─────────────────▶│ Verify User      │
      │                  │                  │─────────────────▶│
      │                  │                  │ Check Password   │
      │                  │                  │◀─────────────────│
      │                  │ Generate JWT     │                  │
      │                  │◀─────────────────│                  │
      │                  │ Send Token       │                  │
      │◀─────────────────│─────────────────▶│                  │
```

## Inventory Management Flow

### Stock Level Monitoring Process
```
Start: Continuous monitoring service runs
    ↓
Fetch current stock levels from database
    ↓
Compare each product's current stock vs. configured thresholds
    ↓
[Is current_stock ≤ alert_threshold?]
    ↓ Yes
        ↓
    Create inventory alert record
        ↓
    Send notification to staff member
        ↓
    [Is auto_order_enabled for product?]
        ↓ Yes
            ↓
        Trigger auto-ordering process
            ↓
        Generate purchase order
            ↓
        Send to supplier
            ↓
        Schedule order fulfillment
            ↓
        Update system with expected delivery
            ↓
        End: Auto-order initiated
            ↓
    [Is user_action_required?]
        ↓ Yes
            ↓
        Send urgent notification to staff
            ↓
        Wait for manual intervention
            ↓
        End: Manual action pending
            ↓
    No → Continue to next product
```

## API Interaction Diagram

### Request/Response Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Service       │    │   Database      │
│   (Vue/Quasar)  │    │   (FastAPI)     │    │   Layer         │    │   (PostgreSQL)  │
└─────┬───────────┘    └──────┬──────────┘    └──────┬──────────┘    └──────┬──────────┘
      │                        │                       │                       │
      │  API Request           │                       │                       │
      │───────────────────────▶│                       │                       │
      │                        │  Validate JWT         │                       │
      │                        │──────────────────────▶│                       │
      │                        │                       │  Authenticate User   │
      │                        │                       │─────────────────────▶│
      │                        │                       │                       │
      │                        │                       │    Verify perms      │
      │                        │                       │◀─────────────────────│
      │                        │                       │                       │
      │                        │                       │  Process Request     │
      │                        │                       │─────────────────────▶│
      │                        │                       │                       │
      │                        │                       │    Query data        │
      │                        │                       │◀─────────────────────│
      │                        │                       │                       │
      │                        │    Process           │                       │
      │                        │◀─────────────────────│                       │
      │                        │                       │                       │
      │   Response            │                       │                       │
      │◀──────────────────────│                       │                       │
```

## ML Model Training Flow

### Forecasting Model Lifecycle
```
Start: New sales data available
    ↓
Collect historical sales data (past 90 days)
    ↓
Apply seasonal adjustments (academic calendar integration)
    ↓
Perform time series decomposition:
- Extract trend component
- Extract seasonal component
- Extract irregular (error) component
    ↓
Apply smoothing algorithms to reduce noise in data
    ↓
Train forecasting model using historical patterns
- Fit regression model to trend
- Adjust for seasonal multipliers
- Calibrate confidence intervals
    ↓
Validate model accuracy against recent data
    ↓
[Does model meet accuracy thresholds?]
    ↓ Yes
        ↓
    Deploy model to production
        ↓
    Generate forecasts for next 30 days
        ↓
    Calculate confidence intervals
        ↓
    Identify products needing attention
        ↓
    Trigger appropriate actions (alerts, auto-orders)
        ↓
    End: Model deployed and running
        ↓
    No → Return to training phase with additional features
```

## Security Architecture

### Authentication and Authorization Flow
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY ARCHITECTURE                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   User Input    │───▶│   Validation    │───▶│   Sanitization  │                  │
│  │  (Credentials)  │    │   (Pydantic)    │    │  (XSS Prevention)│                 │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│         │                        │                        │                          │
│         ▼                        ▼                        ▼                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   Password      │    │   JWT Creation  │    │   RBAC Matrix   │                  │
│  │   Hashing       │    │   (Expiration)  │    │   (Permissions) │                  │
│  │  (BCrypt)       │    │                 │    │                 │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│         │                        │                        │                          │
│         ▼                        ▼                        ▼                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   Database      │    │   Token Store   │    │   Session       │                  │
│  │   (Encrypted)   │    │  (Redis/JWT)    │    │   (Valid)       │                  │
│  │   Storage       │    │                 │    │                 │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │                    API SECURITY                                                 │  │
│  ├─────────────────────────────────────────────────────────────────────────────────┤  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  │                              │  │
│  │  │  │  Rate Limiting  │  │  Input         │  │                              │  │
│  │  │  │  (Abuse Prevent)│  │  Validation    │  │                              │  │
│  │  │  └─────────────────┘  └─────────────────┘  │                              │  │
│  │  │         │                      │            │                              │  │
│  │  │         ▼                      ▼            │                              │  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  │                              │  │
│  │  │  │  CORS Check     │  │  SQL Injection  │  │                              │  │
│  │  │  │  (Origins)      │  │  Prevention    │  │                              │  │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Database Schema Relationships

### Core Entity Relationships
```
Users (1) ←→ (0..n) Orders (customer relationship)
Orders (1) ←→ (0..n) OrderItems (order composition)
Products (1) ←→ (0..n) OrderItems (product reference)
Categories (1) ←→ (0..n) Products (category assignment)
Orders (1) ←→ (1) Addresses (shipping address)
Users (1) ←→ (0..n) Addresses (address collection)
Products (1) ←→ (1) StockItems (inventory tracking)
StockItems (1) ←→ (0..n) StockMovements (movement history)
Products (1) ←→ (0..n) Forecasts (demand prediction)
SeasonalPatterns (1..12) ←→ (1..n) Forecasts (seasonal factors)
Users (1) ←→ (1) Roles (role assignment)
Roles (1) ←→ (0..n) Permissions (role permissions)
Users (1) ←→ (0..n) RefillRequests (request creator)
RefillRequests (1) ←→ (1) PurchaseOrders (order reference)
```

This comprehensive diagram documentation provides visual representations of the system architecture, workflows, and technical processes that govern the Mugnificent E-Commerce Platform's operation.