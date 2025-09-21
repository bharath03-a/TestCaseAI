"""
Document parsing service for healthcare requirements.
"""

import logging
from typing import List, Dict, Any
from ..models import DocumentMetadata, DocumentType, ProcessingStatus

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parses documents and extracts text content."""
    
    def __init__(self):
        """Initialize the document parser."""
        pass
    
    def parse_documents(self, state) -> Any:
        """
        Parse documents and extract text content.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with parsed content
        """
        logger.info(f"Starting document parsing for {len(state.input_documents)} documents")
        
        try:
            document_metadata = []
            raw_text_content = []
            
            for doc in state.input_documents:
                # Extract basic metadata
                filename = doc.get("filename", "unknown")
                content = doc.get("content", "")
                
                # Create document metadata
                metadata = DocumentMetadata(
                    filename=filename,
                    document_type=DocumentType.TEXT,
                    file_size=len(content.encode('utf-8')),
                    word_count=len(content.split()),
                    parsing_status=ProcessingStatus.COMPLETED
                )
                document_metadata.append(metadata)
                raw_text_content.append(content)
            
            # Update state
            state.document_metadata = document_metadata
            state.raw_text_content = raw_text_content
            
            logger.info(f"Successfully parsed {len(document_metadata)} documents")
            return state
            
        except Exception as e:
            logger.error(f"Document parsing failed: {str(e)}")
            state.error_log.append(f"Document parsing failed: {str(e)}")
            state.overall_status = ProcessingStatus.FAILED
            return state
