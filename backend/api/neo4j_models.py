"""
Basic Neo4j schema management for Mapbox/campus routing.
This script is intended to be used by the background synchronization tasks
to pull coordinates from MongoDB and establish routing edges in Neo4j.
"""

from neo4j import GraphDatabase
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
    def close(self):
        self.driver.close()

    def create_dining_hall_node(self, hall_id, name, lat, lng):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (d:DiningHall {id: $id})
                SET d.name = $name, d.lat = $lat, d.lng = $lng
                """,
                id=str(hall_id), name=name, lat=lat, lng=lng
            )
            
    def setup_campus_schema(self):
        """
        Creates constraints and prepares standard campus geography graph.
        """
        try:
            with self.driver.session() as session:
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:DiningHall) REQUIRE d.id IS UNIQUE")
                # Add route pathways, building edges, etc. here as needed
            logger.info("Neo4j campus schema successfully applied.")
        except Exception as e:
            logger.error(f"Failed to setup Neo4j schema: {e}")
