from pydantic import BaseModel
from datetime import datetime

class HelloModel(BaseModel):
    message: str
    status: str
    timestamp: datetime

def main():

    data = HelloModel(
        message="Hello World from Docker!",
        status="Success",
        timestamp=datetime.now()
    )
    
    print("-" * 30)
    print(f"🚀 {data.message}")
    print(f"📊 Status: {data.status}")
    print(f"⏰ Time: {data.timestamp}")
    print("-" * 30)
    print("Python, Pydantic and Docker are working together!")

if __name__ == "__main__":
    main()