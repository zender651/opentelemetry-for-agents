from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.responses import JSONResponse
import logging

# Initialize FastAPI app
app = FastAPI()

# MySQL connection setup
DATABASE_URL = "mysql+mysqlconnector://mcpuser:mcppass@localhost:3306/mcp_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp")

# Pydantic input models
class TableSchema(BaseModel):
    name: str
    columns: dict  # e.g. {"id": "INT PRIMARY KEY", "name": "VARCHAR(255)"}

# --- Routes ---

@app.get("/")
def root():
    return {"message": "MCP MySQL Server is running"}

@app.post("/tables")
def create_table(schema: TableSchema):
    try:
        columns = ", ".join([f"{col} {dtype}" for col, dtype in schema.columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {schema.name} ({columns})"
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
        logger.info(f"Table created: {schema.name}")
        return {"status": "created", "table": schema.name}
    except Exception as e:
        logger.error(f"Create failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tables")
def list_tables():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES")).fetchall()
        tables = [row[0] for row in result]
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tables/{table_name}")
def delete_table(table_name: str):
    try:
        query = f"DROP TABLE IF EXISTS {table_name}"
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
        logger.warning(f"Table deleted: {table_name}")
        return {"status": "deleted", "table": table_name}
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
