"""Storage backends for SecurityAgent."""
from security_agent.storage.document_store import DocumentStore, get_document_store

__all__ = ["DocumentStore", "get_document_store"]
