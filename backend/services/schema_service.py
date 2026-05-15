import logging
from typing import Dict, List

import chromadb
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, inspect

from config import settings

logger = logging.getLogger(__name__)


class SchemaService:
    def __init__(self):
        try:
            logger.info("Initializing SchemaService...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer loaded")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            raise

        try:
            self.chroma_client = chromadb.PersistentClient(path=settings.chroma_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="schema_descriptions"
            )
            logger.info(f"ChromaDB collection ready at {settings.chroma_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

        try:
            self.demo_engine = create_engine(
                settings.demo_db_url,
                connect_args={"check_same_thread": False}
            )
            logger.info("Demo database engine created")
        except Exception as e:
            logger.error(f"Failed to create demo engine: {e}")
            raise

    def introspect_schema(self) -> Dict[str, List[Dict]]:
        try:
            inspector = inspect(self.demo_engine)
            table_names = inspector.get_table_names()
            schema_dict = {}

            for table_name in table_names:
                try:
                    columns = inspector.get_columns(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    pk_constraint = inspector.get_pk_constraint(table_name)

                    pk_columns = pk_constraint.get('constrained_columns', [])

                    fk_map = {}
                    for fk in foreign_keys:
                        for col in fk.get('constrained_columns', []):
                            fk_map[col] = {
                                'table': fk.get('referred_table'),
                                'column': fk.get('referred_columns', [])
                            }

                    formatted_columns = []
                    for col in columns:
                        col_info = {
                            'name': col['name'],
                            'type': str(col['type']),
                            'primary_key': col['name'] in pk_columns,
                            'foreign_keys': fk_map.get(col['name'])
                        }
                        formatted_columns.append(col_info)

                    schema_dict[table_name] = formatted_columns
                    logger.debug(f"Introspected table: {table_name}")

                except Exception as e:
                    logger.error(f"Failed to introspect table {table_name}: {e}")
                    continue

            logger.info(f"Schema introspection complete: {len(schema_dict)} tables")
            return schema_dict

        except Exception as e:
            logger.error(f"Schema introspection failed: {e}")
            return {}

    def format_table_description(self, table_name: str, columns: List[Dict]) -> str:
        try:
            col_descriptions = []
            for col in columns:
                col_desc = f"{col['name']}({col['type']}"

                if col['primary_key']:
                    col_desc += ", PK"

                if col['foreign_keys']:
                    fk_info = col['foreign_keys']
                    fk_ref = f"FK→{fk_info['table']}"
                    col_desc += f", {fk_ref}"

                col_desc += ")"
                col_descriptions.append(col_desc)

            description = f"Table: {table_name}. Columns: {', '.join(col_descriptions)}"
            return description

        except Exception as e:
            logger.error(f"Failed to format table {table_name}: {e}")
            return f"Table: {table_name}"

    def embed_schema(self) -> None:
        try:
            schema_dict = self.introspect_schema()

            if not schema_dict:
                logger.warning("No schema found to embed")
                return

            for table_name, columns in schema_dict.items():
                try:
                    description = self.format_table_description(table_name, columns)
                    embedding = self.model.encode([description])[0].tolist()

                    self.collection.upsert(
                        ids=[table_name],
                        documents=[description],
                        embeddings=[embedding]
                    )

                    print(f"Schema embedded: {table_name}")
                    logger.info(f"Embedded schema for table: {table_name}")

                except Exception as e:
                    logger.error(f"Failed to embed table {table_name}: {e}")
                    continue

            logger.info("Schema embedding complete")

        except Exception as e:
            logger.error(f"Schema embedding failed: {e}")

    def search_schema(self, query: str, top_k: int = 3) -> str:
        try:
            query_embedding = self.model.encode([query])[0].tolist()

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            if results and results.get("documents") and results["documents"][0]:
                schema_text = "\n\n".join(results["documents"][0])
                logger.info(f"Schema search found {len(results['documents'][0])} results")
                return schema_text
            else:
                logger.warning("No schema search results, returning full schema")
                return self.format_full_schema()

        except Exception as e:
            logger.error(f"Schema search failed: {e}, returning full schema")
            return self.format_full_schema()

    def format_full_schema(self) -> str:
        try:
            schema_dict = self.introspect_schema()

            if not schema_dict:
                return "No schema available"

            descriptions = []
            for table_name, columns in schema_dict.items():
                desc = self.format_table_description(table_name, columns)
                descriptions.append(desc)

            full_schema = "\n\n".join(descriptions)
            logger.info("Full schema formatted")
            return full_schema

        except Exception as e:
            logger.error(f"Failed to format full schema: {e}")
            return "Schema unavailable due to error"

    def get_schema_dict(self) -> Dict[str, List[Dict]]:
        try:
            return self.introspect_schema()
        except Exception as e:
            logger.error(f"Failed to get schema dict: {e}")
            return {}


schema_service = SchemaService()
