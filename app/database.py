import logging
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase, Driver
from app.config import settings

logger = logging.getLogger("cognodb-driver")
logging.basicConfig(level=logging.INFO)

class DatabaseManager:
    """
    Manages connection lifecycle with CognoDB Cloud instance using official Neo4j Python Driver.
    Includes seamless mock/fallback mode for offline or unconfigured environment evaluations.
    """
    def __init__(self):
        self.driver: Optional[Driver] = None
        self.is_connected: bool = False
        self.error_message: Optional[str] = None
        self._init_driver()

    def _init_driver(self):
        uri = settings.COGNODB_URI
        user = settings.COGNODB_USER
        password = settings.COGNODB_PASSWORD

        if not uri or "demo-instance" in uri or not password or password == "cognodb_demo_password":
            self.is_connected = False
            self.error_message = "CognoDB credentials unconfigured or placeholder. Running in Mock/Fallback graph mode."
            logger.info(self.error_message)
            return

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test connectivity
            self.driver.verify_connectivity()
            self.is_connected = True
            self.error_message = None
            logger.info(f"Successfully connected to CognoDB instance at {uri}")
        except Exception as e:
            self.is_connected = False
            self.error_message = f"Failed to connect to CognoDB at {uri}: {str(e)}"
            logger.warning(self.error_message)
            if self.driver:
                try:
                    self.driver.close()
                except Exception:
                    pass
                self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()
            self.is_connected = False

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query against CognoDB with parameter binding.
        """
        if not self.is_connected or not self.driver:
            raise ConnectionError(self.error_message or "CognoDB database driver is not connected.")

        parameters = parameters or {}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

db_manager = DatabaseManager()
