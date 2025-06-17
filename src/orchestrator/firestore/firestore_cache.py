"""
Firestore L1 cache integration for the orchestrator.
"""
from google.cloud import firestore
from typing import Any
import os

COLLECTION = os.getenv("FIRESTORE_COLLECTION", "orchestrator_cache")

class FirestoreCache:
    def __init__(self, project_id: str):
        self.client = firestore.Client(project=project_id)
        self.collection = self.client.collection(COLLECTION)

    def get(self, key: str) -> Any:
        doc = self.collection.document(key).get()
        if doc.exists:
            return doc.to_dict().get("value")
        return None

    def set(self, key: str, value: Any) -> None:
        self.collection.document(key).set({"value": value})

    def clear(self) -> None:
        # Not recommended in prod; for dev/testing only
        for doc in self.collection.stream():
            doc.reference.delete()
