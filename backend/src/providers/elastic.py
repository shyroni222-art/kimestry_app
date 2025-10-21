from typing import Dict, List, Any, Optional
from src.utils.constants import ELASTICSEARCH_URL
from src.utils.logging_setup import get_logger
import requests
import json

logger = get_logger(__name__)


class ElasticProvider:
    def __init__(self, es_url: str = ELASTICSEARCH_URL):
        self.es_url = es_url
        self.session = requests.Session()

    def index_document(self, index_name: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index a document in Elasticsearch"""
        try:
            url = f"{self.es_url}/{index_name}/_doc/{doc_id}"
            response = self.session.put(url, json=document)
            
            if response.status_code in [200, 201]:
                logger.info(f"Document {doc_id} indexed successfully in {index_name}")
                return True
            else:
                logger.error(f"Failed to index document {doc_id}. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error indexing document {doc_id} in {index_name}: {str(e)}")
            return False

    def search(self, index_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search documents in Elasticsearch"""
        try:
            url = f"{self.es_url}/{index_name}/_search"
            response = self.session.get(url, json=query)
            
            if response.status_code == 200:
                result = response.json()
                hits = result.get('hits', {}).get('hits', [])
                return [hit['_source'] for hit in hits]
            else:
                logger.error(f"Search failed. Status: {response.status_code}, Response: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error searching in {index_name}: {str(e)}")
            return []

    def create_index(self, index_name: str, mapping: Optional[Dict[str, Any]] = None) -> bool:
        """Create an index in Elasticsearch"""
        try:
            url = f"{self.es_url}/{index_name}"
            payload = {}
            if mapping:
                payload = {"mappings": mapping}
            
            response = self.session.put(url, json=payload)
            
            if response.status_code in [200, 201]:
                logger.info(f"Index {index_name} created successfully")
                return True
            elif response.status_code == 400:
                # Index already exists
                logger.info(f"Index {index_name} already exists")
                return True
            else:
                logger.error(f"Failed to create index {index_name}. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {str(e)}")
            return False

    def bulk_index(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Bulk index documents in Elasticsearch"""
        try:
            url = f"{self.es_url}/{index_name}/_bulk"
            
            bulk_body = ""
            for doc in documents:
                bulk_body += json.dumps({"index": {"_id": doc.get("id")}}) + "\n"
                bulk_body += json.dumps(doc) + "\n"
            
            response = self.session.post(url, data=bulk_body, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                errors = result.get('errors', False)
                if errors:
                    logger.warning(f"Bulk index completed with errors: {result.get('items', [])}")
                else:
                    logger.info(f"Bulk index completed successfully for {len(documents)} documents")
                return True
            else:
                logger.error(f"Failed to bulk index documents. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error in bulk indexing: {str(e)}")
            return False

    def delete_index(self, index_name: str) -> bool:
        """Delete an index in Elasticsearch"""
        try:
            url = f"{self.es_url}/{index_name}"
            response = self.session.delete(url)
            
            if response.status_code == 200:
                logger.info(f"Index {index_name} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete index {index_name}. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error deleting index {index_name}: {str(e)}")
            return False


# Global instance for easy access
elastic_provider = ElasticProvider()