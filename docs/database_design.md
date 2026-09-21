# Database Design: SQLite Schema & SQLAlchemy Models

## 1. Why SQLite?
SQLite is an embedded, zero-configuration SQL database engine. For a CA3 mini project and embedded automotive edge telematics:
- No external server setup (e.g. Postgres/MySQL daemon) required.
- Single file persistence (`vehiclecare.db`) easy to backup, demonstrate, and transfer.
- ACID-compliant and supports multi-threaded connections in FastAPI using `check_same_thread=False`.
- Clean abstraction using SQLAlchemy 2.0 ORM allows switching to PostgreSQL in enterprise production without changing application code.

---

## 2. Entity-Relationship Diagram (ERD)

```
       +----------------------------+
       |          vehicles          |
       +----------------------------+
       | id (PK)           VARCHAR  |<----+
       | make              VARCHAR  |     |
       | model             VARCHAR  |     |
       | year              INTEGER  |     |
       | type              VARCHAR  |     |
       | mileage           INTEGER  |     | 1:N
       | days_since_service INTEGER |     |
       | battery_voltage   FLOAT    |     |
       | engine_temp       FLOAT    |     |
       | brake_wear_pct    FLOAT    |     |
       | tire_pressure_avg FLOAT    |     |
       | oil_life_pct      FLOAT    |     |
       | created_at        DATETIME |     |
       | updated_at        DATETIME |     |
       +----------------------------+     |
                     | 1:N                |
                     |                    |
                     v                    |
       +----------------------------+     |
       |    maintenance_records     |     |
       +----------------------------+     |
       | id (PK)           VARCHAR  |     |
       | vehicle_id (FK)   VARCHAR  |-----+
       | date              VARCHAR  |
       | mileage           INTEGER  |
       | service_type      VARCHAR  |
       | cost              FLOAT    |
       | notes             VARCHAR  |
       | created_at        DATETIME |
       +----------------------------+
                     |
                     v
       +----------------------------+
       |        predictions         |
       +----------------------------+
       | id (PK)           VARCHAR  |
       | vehicle_id (FK)   VARCHAR  |
       | risk_level        VARCHAR  |
       | probability       FLOAT    |
       | maintenance_req   VARCHAR  |
       | affected_subsys   TEXT     |
       | input_features    TEXT     |
       | created_at        DATETIME |
       +----------------------------+

       +----------------------------+
       |          datasets          |
       +----------------------------+
       | id (PK)           VARCHAR  |
       | filename          VARCHAR  |
       | records           INTEGER  |
       | features          INTEGER  |
       | target_column     VARCHAR  |
       | status            VARCHAR  |
       | uploaded_at       DATETIME |
       +----------------------------+
```

---

## 3. Table Definitions

### `vehicles`
Stores core vehicle specifications and current baseline telemetry.

### `maintenance_records`
Maintains historical workshop logs (date, mileage, service performed, cost, notes). Used by the AI Agent's `get_maintenance_history` tool.

### `predictions`
Persists model and agent diagnostic outputs. Enables tracking risk trajectory over time.

### `datasets`
Tracks training dataset versions, uploaded files, and sample counts.
