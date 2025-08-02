from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
import os
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class RAGTool(BaseTool):
    """Enhanced Retrieval-Augmented Generation tool for document storage and semantic search."""
    
    def __init__(self, knowledge_base_file: str = "knowledge_base.json"):
        self.name = "rag_tool"
        self.description = "Store documents and retrieve relevant information using semantic search. Useful for maintaining a knowledge base."
        self.params = [
            Field(
                name="action",
                description="Action to perform: 'store', 'search', 'list', 'delete', or 'stats'",
                required=True,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="document",
                description="Document content to store (required for store action)",
                required=False,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="query",
                description="Search query for retrieving relevant documents (required for search action)",
                required=False,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="doc_id",
                description="Document ID for deletion (required for delete action)",
                required=False,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="title",
                description="Title for the document (optional for store action)",
                default_value="Untitled Document",
                required=False,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="category",
                description="Category/tag for organizing documents",
                default_value="general",
                required=False,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="max_results",
                description="Maximum number of search results to return (1-20)",
                default_value=5,
                required=False,
                field_type=ToolParameterType.INTEGER
            )
        ]
        self.knowledge_base_file = knowledge_base_file
        self._ensure_knowledge_base()
        super().__init__()
    
    def _ensure_knowledge_base(self) -> None:
        """Ensure knowledge base file exists with proper structure."""
        if not os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "documents": {},
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "total_docs": 0,
                        "version": "1.0"
                    }
                }, f)
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base from file."""
        try:
            with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading knowledge base: {e}")
            return {
                "documents": {},
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "total_docs": 0,
                    "version": "1.0"
                }
            }
    
    def _save_knowledge_base(self, kb_data: Dict[str, Any]) -> None:
        """Save knowledge base to file."""
        try:
            kb_data["metadata"]["last_updated"] = datetime.now().isoformat()
            kb_data["metadata"]["total_docs"] = len(kb_data["documents"])
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(kb_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            raise RuntimeError(f"Failed to save knowledge base: {e}")
    
    def _generate_doc_id(self, content: str, title: str) -> str:
        """Generate a unique document ID based on content hash."""
        content_hash = hashlib.md5(f"{title}:{content}".encode()).hexdigest()
        return f"doc_{content_hash[:12]}"
    
    def _simple_text_search(self, query: str, documents: Dict[str, Any], max_results: int) -> List[Tuple[str, float]]:
        """Simple keyword-based search (fallback for when no embeddings are available)."""
        query_words = set(query.lower().split())
        results = []
        
        for doc_id, doc_data in documents.items():
            content = doc_data.get("content", "").lower()
            title = doc_data.get("title", "").lower()
            
            # Calculate simple relevance score based on keyword matches
            content_words = set(content.split())
            title_words = set(title.split())
            
            # Score based on word overlap
            content_score = len(query_words.intersection(content_words)) / len(query_words) if query_words else 0
            title_score = len(query_words.intersection(title_words)) / len(query_words) if query_words else 0
            
            # Weight title matches higher
            total_score = content_score * 0.7 + title_score * 0.3
            
            if total_score > 0:
                results.append((doc_id, total_score))
        
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]
    
    def _run(self, action: str, document: Optional[str] = None, query: Optional[str] = None,
             doc_id: Optional[str] = None, title: str = "Untitled Document", 
             category: str = "general", max_results: int = 5) -> str:
        """Execute RAG operations."""
        action = action.lower().strip()
        
        if action not in ["store", "search", "list", "delete", "stats"]:
            raise ValueError(f"Invalid action: {action}. Must be 'store', 'search', 'list', 'delete', or 'stats'")
        
        kb_data = self._load_knowledge_base()
        
        if action == "store":
            if not document:
                raise ValueError("'document' content is required for store action")
            
            # Generate document ID
            generated_doc_id = self._generate_doc_id(document, title)
            
            # Check if document already exists
            if generated_doc_id in kb_data["documents"]:
                return f"Document already exists with ID: {generated_doc_id}"
            
            # Store document
            doc_entry = {
                "title": title,
                "content": document,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0,
                "word_count": len(document.split())
            }
            
            kb_data["documents"][generated_doc_id] = doc_entry
            self._save_knowledge_base(kb_data)
            
            return f"Successfully stored document '{title}' with ID: {generated_doc_id}"
        
        elif action == "search":
            if not query:
                raise ValueError("'query' is required for search action")
            
            documents = kb_data["documents"]
            if not documents:
                return "No documents in knowledge base"
            
            # Clamp max_results
            max_results = max(1, min(max_results, 20))
            
            # Perform simple text search
            search_results = self._simple_text_search(query, documents, max_results)
            
            if not search_results:
                return f"No relevant documents found for query: '{query}'"
            
            result = f"Found {len(search_results)} relevant documents for '{query}':\n\n"
            
            for doc_id, relevance_score in search_results:
                doc_data = documents[doc_id]
                doc_data["access_count"] += 1  # Track access
                
                result += f"📄 {doc_data['title']} (ID: {doc_id})\n"
                result += f"   Category: {doc_data['category']} | Relevance: {relevance_score:.2f}\n"
                result += f"   Content: {doc_data['content'][:200]}{'...' if len(doc_data['content']) > 200 else ''}\n\n"
            
            self._save_knowledge_base(kb_data)  # Save updated access counts
            return result.strip()
        
        elif action == "list":
            documents = kb_data["documents"]
            if not documents:
                return "No documents stored in knowledge base"
            
            result = f"Knowledge Base Contents ({len(documents)} documents):\n\n"
            
            # Group by category
            categories = {}
            for doc_id, doc_data in documents.items():
                cat = doc_data.get("category", "general")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((doc_id, doc_data))
            
            for category, docs in categories.items():
                result += f"📁 {category.upper()}\n"
                for doc_id, doc_data in docs:
                    result += f"   📄 {doc_data['title']} (ID: {doc_id[:8]}...)\n"
                    result += f"      Words: {doc_data.get('word_count', 'N/A')} | "
                    result += f"Accessed: {doc_data.get('access_count', 0)} times\n"
                result += "\n"
            
            return result.strip()
        
        elif action == "delete":
            if not doc_id:
                raise ValueError("'doc_id' is required for delete action")
            
            if doc_id in kb_data["documents"]:
                doc_title = kb_data["documents"][doc_id].get("title", "Unknown")
                del kb_data["documents"][doc_id]
                self._save_knowledge_base(kb_data)
                return f"Successfully deleted document: {doc_title} (ID: {doc_id})"
            else:
                return f"Document not found with ID: {doc_id}"
        
        elif action == "stats":
            documents = kb_data["documents"]
            total_docs = len(documents)
            
            if total_docs == 0:
                return "Knowledge base is empty"
            
            # Calculate statistics
            categories = {}
            total_words = 0
            total_accesses = 0
            
            for doc_data in documents.values():
                cat = doc_data.get("category", "general")
                categories[cat] = categories.get(cat, 0) + 1
                total_words += doc_data.get("word_count", 0)
                total_accesses += doc_data.get("access_count", 0)
            
            result = f"📊 Knowledge Base Statistics:\n"
            result += f"   Total Documents: {total_docs}\n"
            result += f"   Total Words: {total_words:,}\n"
            result += f"   Total Accesses: {total_accesses}\n"
            result += f"   Categories: {len(categories)}\n\n"
            
            result += "📁 Documents by Category:\n"
            for cat, count in sorted(categories.items()):
                result += f"   {cat}: {count} documents\n"
            
            return result.strip()
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        kb_data = self._load_knowledge_base()
        return kb_data["documents"].get(doc_id)