# RDBMS (SQL) Data Science Group Project

Analysing differences in the US and German labour markets

## Team
- Cam
- Octavia
- Ellie
- Marwan

## Database System
- **RDBMS:** PostgreSQL 15 

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/username/ds-sql-project.git
cd ds-sql-project
```

### 2. Install the database
```bash
# PostgreSQL (macOS)
brew install postgresql
brew services start postgresql
```

### 3. Create the database
```bash
psql -U postgres -c "CREATE DATABASE project_db;"
```

### 4. Run the schema
```bash
psql -U postgres -d project_db -f schema/create_tables.sql
```

### 5. Load the data
```bash
psql -U postgres -d project_db -f schema/seed_data.sql
```

## Project Structure
```
ds-sql-project/
├── data/         # Raw and processed data files
├── schema/       # Table definitions, ERDs, migrations
├── queries/      # All SQL query files
├── analysis/     # Views, stored procedures, findings
└── reports/      # Written results and outputs
```
