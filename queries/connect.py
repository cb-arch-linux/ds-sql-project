from sqlalchemy import create_engine
import pandas as pd

# SQLite (local file)
engine = create_engine("sqlite:///teaching.db")

# PostgreSQL (direct)
engine = create_engine("postgresql://user:pass@db.exeter.ac.uk:5432/bee2041")

# PostgreSQL (via SSH tunnel)
engine = create_engine("postgresql://user:pass@localhost:5433/bee2041")