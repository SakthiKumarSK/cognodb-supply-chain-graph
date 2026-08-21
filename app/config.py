import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    COGNODB_URI: str = os.getenv("COGNODB_URI", "bolt+s://demo.databases.cognodb.cloud")
    COGNODB_USER: str = os.getenv("COGNODB_USER", "cognodb")
    COGNODB_PASSWORD: str = os.getenv("COGNODB_PASSWORD", "demo")
    
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = Settings()
