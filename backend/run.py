import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
host = os.getenv("API_HOST", "localhost")
port = int(os.getenv("API_PORT", "8000"))

if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run("app.main:app", host=host, port=port, reload=True)