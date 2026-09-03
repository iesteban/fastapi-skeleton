import os
import uvicorn

from app.main import create_app

env = os.environ.get("APP_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
