"""
Intelligent Q&A System using GPT-4o + Embeddings (RAG)
Combines vector search with GPT-4o for natural language answers
"""

import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from services import VectorSearchService, get_db

# Azure OpenAI configuration
# Support multiple environment variable names for flexibility
AZURE_OPENAI_API_KEY = (
    os.environ.get('AZURE_OPENAI_API_KEY') or 
    os.environ.get('AZURE_OPENAI_KEY') or
    os.environ.get('OPENAI_API_KEY')
)
AZURE_OPENAI_ENDPOINT = (
    os.environ.get('AZURE_OPENAI_ENDPOINT') or
    os.environ.get('AZURE_OPENAI_API_BASE') or
    os.environ.get('AZURE_EMBEDDING_ENDPOINT')
)
AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-02-01')
AZURE_DEPLOYMENT_NAME = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
USE_GPT = bool(AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT)

print(f"🔧 Azure OpenAI Configuration:")
print(f"   API Key: {'✅ Set' if AZURE_OPENAI_API_KEY else '❌ Missing'}")
print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT if AZURE_OPENAI_ENDPOINT else '❌ Missing'}")
print(f"   Deployment: {AZURE_DEPLOYMENT_NAME}")
print(f"   USE_GPT: {USE_GPT}")

class IntelligentQAService:
    """RAG-based Q&A system for RFP documents"""
    
    def __init__(self, db=None):
        self.vector_service = VectorSearchService(db)
        self.gpt_client = None
        
        if USE_GPT:
            try:
                self.gpt_client = AzureOpenAI(
                    api_key=AZURE_OPENAI_API_KEY,
                    api_version=AZURE_OPENAI_API_VERSION,
                    azure_endpoint=AZURE_OPENAI_ENDPOINT
                )
                print(f"✅ GPT-4o initialized: {AZURE_DEPLOYMENT_NAME}")
            except Exception as e:
                print(f"⚠️ GPT-4o initialization failed: {e}")
                self.gpt_client = None
    
    def ask_question(
        self, 
        question: str, 
        filters: Optional[Dict] = None,
        top_n: int = 10,  # Increased from 5 to 10 for more context
        temperature: float = 0.3,
        max_tokens: int = 2000  # Increased from 1000 for more detailed answers
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG (Retrieval-Augmented Generation)
        
        Args:
            question: User's natural language question
            filters: Optional filters (product, category, etc.)
            top_n: Number of relevant documents to retrieve
            temperature: GPT creativity (0-1, lower = more focused)
            max_tokens: Maximum response length
            
        Returns:
            {
                'answer': str,  # GPT-4o generated answer
                'sources': List[Dict],  # Retrieved documents used
                'mode': str,  # 'intelligent' or 'search-only'
                'confidence': float  # 0-1 confidence score
            }
        """
        try:
            print(f"🔍 Processing question: {question}")
            print(f"   Retrieving top {top_n} documents...")
            
            # Check if GPT client is available
            if not self.gpt_client:
                print("⚠️ GPT client not initialized - falling back to simple search")
                # Fallback to simple MongoDB search
                return self._fallback_to_simple_search(question, filters, top_n)
            
            # Check if vector service is properly initialized
            if not self.vector_service or not self.vector_service.azure_client:
                print("⚠️ Vector service not available - falling back to simple search")
                return self._fallback_to_simple_search(question, filters, top_n)
            
            # Step 1: Vector search to find relevant documents
            print("   Performing vector search...")
            search_results = self.vector_service.search(
                query=question,
                top_n=top_n,
                filters=filters
            )
            print(f"   Found {len(search_results)} results")
            
            if not search_results:
                print("   ❌ No search results found")
                return {
                    'answer': "I couldn't find any relevant information in the RFP documents for your question.",
                    'sources': [],
                    'mode': 'no-results',
                    'confidence': 0.0
                }
            
            # Step 2: Prepare context from retrieved documents
            print("   Preparing context from sources...")
            context = self._prepare_context(search_results)
            
            # DEBUG: Print context to verify it's being prepared correctly
            print("="*80)
            print("PREPARED CONTEXT FOR GPT:")
            print(context[:1000])  # Print first 1000 chars
            print("="*80)
            
            # Step 3: Generate answer using GPT-4o
            print("   Generating answer with GPT-4o...")
            answer, confidence = self._generate_answer(
                question=question,
                context=context,
                temperature=temperature,
                max_tokens=max_tokens
            )
            print(f"   ✅ Answer generated (confidence: {confidence})")
            
            # Clean sources for frontend display
            cleaned_sources = self._clean_sources_for_display(search_results)
            
            return {
                'answer': answer,
                'sources': cleaned_sources,
                'mode': 'intelligent',
                'confidence': confidence,
                'model': AZURE_DEPLOYMENT_NAME,
                'total_sources': len(cleaned_sources),
                'sources_analyzed': min(top_n, len(cleaned_sources))
            }
            
        except Exception as e:
            error_message = str(e)
            print(f"Error in intelligent Q&A: {error_message}")
            
            # Provide more helpful error messages
            if "Connection" in error_message or "refused" in error_message:
                return {
                    'answer': "The semantic search feature is currently unavailable. The vector database service is not running. You can still upload and manage documents, but AI-powered search requires additional infrastructure setup.",
                    'sources': [],
                    'mode': 'error',
                    'confidence': 0.0,
                    'error_type': 'connection_error'
                }
            elif "embeddings not configured" in error_message.lower():
                return {
                    'answer': "Azure OpenAI embeddings are being configured. Please try again in a moment.",
                    'sources': [],
                    'mode': 'error',
                    'confidence': 0.0,
                    'error_type': 'configuration_error'
                }
            else:
                return {
                    'answer': f"I encountered an error processing your question: {error_message}",
                    'sources': [],
                    'mode': 'error',
                    'confidence': 0.0,
                    'error_type': 'unknown_error'
                }
    
    def _prepare_context(self, search_results: List[Dict]) -> str:
        """Format search results into context for GPT"""
        context_parts = []
        
        for idx, result in enumerate(search_results, 1):
            # Results come directly from vector service, not nested in 'payload'
            requirement = result.get('requirement', 'N/A')
            product = result.get('product', 'General')
            category = result.get('requirement_category', 'N/A')
            rfp_name = result.get('rfp_name', 'Unknown RFP')
            bank_name = result.get('bank_name', 'Unknown Bank')
            sheet_name = result.get('sheet_name', 'Unknown Sheet')
            file_name = result.get('file_name', 'Unknown File')
            relevance_score = result.get('relevance_score', 0)
            
            # Clean up the requirement text to remove "Unnamed:" prefixes
            cleaned_requirement = self._clean_requirement_text(requirement)
            
            context_parts.append(
                f"[Document {idx}]\n"
                f"Source: {file_name} - Sheet: {sheet_name}\n"
                f"RFP: {rfp_name} (Bank: {bank_name})\n"
                f"Product/Module: {product}\n"
                f"Category: {category}\n"
                f"Content:\n{cleaned_requirement}\n"
                f"Relevance Score: {relevance_score:.2f}\n"
            )
        
        return "\n".join(context_parts)
    
    def _clean_requirement_text(self, text: str) -> str:
        """Clean up requirement text by removing 'Unnamed:' prefixes and formatting nicely"""
        if not text or text == 'N/A':
            return text
        
        # Split by pipe separator
        parts = text.split('|')
        cleaned_parts = []
        
        for part in parts:
            part = part.strip()
            
            # Remove "Unnamed: N:" prefix pattern
            import re
            # Pattern matches "Unnamed: 1:", "Unnamed: 2:", etc.
            cleaned = re.sub(r'^Unnamed:\s*\d+:\s*', '', part)
            
            # Only add non-empty parts
            if cleaned:
                cleaned_parts.append(cleaned)
        
        # Join with newlines for better readability
        if len(cleaned_parts) > 1:
            # Format as structured data
            result = []
            for i, part in enumerate(cleaned_parts):
                if i == 0:
                    result.append(f"Requirement: {part}")
                elif i == 1:
                    result.append(f"Department/Category: {part}")
                elif i == 2:
                    result.append(f"Status: {part}")
                elif i == 3:
                    result.append(f"Details: {part}")
                else:
                    result.append(part)
            return '\n'.join(result)
        else:
            return cleaned_parts[0] if cleaned_parts else text
    
    def _clean_sources_for_display(self, search_results: List[Dict]) -> List[Dict]:
        """Clean source documents for frontend display by removing 'Unnamed:' prefixes"""
        cleaned_sources = []
        
        for result in search_results:
            # Make a copy to avoid modifying original
            cleaned_result = result.copy()
            
            # Clean the requirement field if it exists
            if 'requirement' in cleaned_result and cleaned_result['requirement']:
                requirement = cleaned_result['requirement']
                
                # Split by pipe and clean each part
                parts = requirement.split('|')
                cleaned_parts = []
                
                for part in parts:
                    part = part.strip()
                    # Remove "Unnamed: N:" prefix
                    import re
                    cleaned = re.sub(r'^Unnamed:\s*\d+:\s*', '', part)
                    if cleaned:
                        cleaned_parts.append(cleaned)
                
                # Join with | for display
                cleaned_result['requirement'] = ' | '.join(cleaned_parts)
            
            # Clean highlight field if it exists
            if 'highlight' in cleaned_result and cleaned_result['highlight']:
                highlight = cleaned_result['highlight']
                import re
                cleaned_result['highlight'] = re.sub(r'Unnamed:\s*\d+:\s*', '', highlight)
            
            cleaned_sources.append(cleaned_result)
        
        return cleaned_sources
    
    def _generate_answer(
        self, 
        question: str, 
        context: str,
        temperature: float,
        max_tokens: int
    ) -> tuple[str, float]:
        """Generate answer using GPT-4o"""
        
        # Carefully crafted system prompt for RFP Q&A
        system_prompt = """You are an expert RFP (Request for Proposal) analyst assistant. Your role is to help users understand and analyze RFP requirements from the provided context documents.

**CRITICAL: You MUST carefully read and analyze ALL the source documents provided in the "RFP Context" section below. Do NOT say "no information found" if the context contains relevant data.**

**Your capabilities:**
- Answer questions about RFP requirements accurately based on provided sources
- Summarize complex technical specifications from the documents
- Compare and contrast different requirements across documents
- Identify patterns and dependencies in the RFP data
- Provide structured, professional responses with proper citations

**Guidelines:**
1. **ALWAYS read the entire RFP Context section carefully before answering**
2. Base your answers ONLY on the information in the provided source documents
3. If you find relevant information, cite the specific document number (e.g., [Document 1])
4. Extract key details like: requirement text, department/category, status, implementation details
5. If multiple documents mention the topic, synthesize information from all of them
6. Use bullet points for clarity when listing multiple items
7. Be concise but comprehensive - include all relevant details from sources
8. Use professional, business-appropriate language
9. If asked about implementation, reference the vendor response/details from the documents

**Response format:**
- Start with a direct answer based on what you found in the sources
- Quote or paraphrase key requirements from the documents (cite document numbers)
- List specific details: departments involved, integration requirements, vendor capabilities
- If applicable, mention any gaps, dependencies, or notes from the RFP
- End with implementation considerations or next steps if mentioned in sources

**Remember: If the RFP Context contains information about the question, you MUST extract and present it. Do not claim "no information" when sources are provided.**"""

        user_prompt = f"""Question: {question}

RFP Context:
{context}

Please provide a comprehensive answer based on the RFP requirements above."""

        try:
            response = self.gpt_client.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )
            
            answer = response.choices[0].message.content
            
            # Calculate confidence based on finish reason and context quality
            finish_reason = response.choices[0].finish_reason
            confidence = 0.9 if finish_reason == 'stop' else 0.7
            
            return answer, confidence
            # Calculate confidence based on finish reason and response quality
            finish_reason = response.choices[0].finish_reason
            
            # Higher confidence for complete answers
            if finish_reason == 'stop':
                confidence = 0.95  # High confidence for complete response
            elif finish_reason == 'length':
                confidence = 0.85  # Good confidence but hit token limit
            else:
                confidence = 0.75  # Moderate confidence for other cases
            
            # Boost confidence if answer contains document citations
            if '[Document' in answer:
                confidence = min(confidence + 0.05, 1.0)
            
            return answer, confidence
            
        except Exception as e:
            print(f"GPT-4o generation failed: {e}")
            return f"Error generating answer: {str(e)}", 0.0
    
    def _fallback_to_simple_search(
        self, 
        question: str, 
        filters: Optional[Dict],
        top_n: int
    ) -> Dict[str, Any]:
        """
        Fallback to simple MongoDB text search when vector/GPT unavailable
        """
        try:
            from services import get_db
            db = get_db()
            
            if not db:
                return {
                    'answer': "Database connection not available.",
                    'sources': [],
                    'mode': 'error',
                    'confidence': 0.0
                }
            
            # Simple text search on requirement field
            search_terms = question.lower().split()
            regex_patterns = [
                {'requirement': {'$regex': term, '$options': 'i'}} 
                for term in search_terms if len(term) > 2
            ]
            
            if not regex_patterns:
                return {
                    'answer': "Please provide more specific search terms.",
                    'sources': [],
                    'mode': 'no-results',
                    'confidence': 0.0
                }
            
            results = list(db.rfp_entries.find({'$or': regex_patterns}).limit(top_n))
            
            if not results:
                return {
                    'answer': "No matching RFP entries found.",
                    'sources': [],
                    'mode': 'no-results',
                    'confidence': 0.0
                }
            
            # Format sources
            sources = []
            for result in results:
                sources.append({
                    'record_id': str(result.get('_id')),
                    'product': result.get('product', 'N/A'),
                    'requirement': self._clean_requirement_text(result.get('requirement', 'N/A')),
                    'category': result.get('requirement_category', 'N/A'),
                    'response_category': result.get('response_category', 'N/A'),
                    'sheet_name': result.get('sheet_name', 'N/A'),
                    'file_name': result.get('file_name', 'N/A'),
                    'rfp_name': result.get('rfp_name', 'N/A'),
                    'bank_name': result.get('bank_name', 'N/A')
                })
            
            answer = self._format_search_results_for_fallback(sources, question)
            
            return {
                'answer': answer,
                'sources': sources,
                'mode': 'simple-search',
                'confidence': 0.6,
                'note': 'Using simple keyword search. AI-powered analysis unavailable.'
            }
            
        except Exception as e:
            print(f"Fallback search error: {e}")
            return {
                'answer': f"Search error: {str(e)}",
                'sources': [],
                'mode': 'error',
                'confidence': 0.0
            }
    
    def _format_search_results_for_fallback(
        self, 
        sources: List[Dict], 
        question: str
    ) -> str:
        """Format search results for fallback mode"""
        answer_parts = [
            f"Found {len(sources)} relevant RFP entries for '{question}':\n"
        ]
        
        for idx, source in enumerate(sources, 1):
            requirement = source.get('requirement', 'N/A')
            product = source.get('product', 'N/A')
            category = source.get('category', 'N/A')
            
            answer_parts.append(
                f"\n{idx}. **{product}** - {category}\n"
                f"   {requirement[:200]}{'...' if len(requirement) > 200 else ''}"
            )
        
        answer_parts.append(
            "\n\n💡 Note: This is a simple keyword search. "
            "For AI-powered analysis, ensure Azure OpenAI is configured."
        )
        
        return "\n".join(answer_parts)
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results as plain text (fallback when GPT unavailable)"""
        if not results:
            return "No relevant results found."
        
        formatted = ["Based on the RFP documents, here are the relevant requirements:\n"]
        
        for idx, result in enumerate(results, 1):
            payload = result.get('payload', {})
            requirement = payload.get('requirement', 'N/A')
            product = payload.get('product', 'General')
            score = result.get('score', 0)
            
            formatted.append(
                f"{idx}. [{product}] (Relevance: {score:.1%})\n"
                f"   {requirement}\n"
            )
        
        return "\n".join(formatted)
    
    def ask_follow_up(
        self,
        question: str,
        conversation_history: List[Dict[str, str]],
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Handle follow-up questions with conversation context
        
        Args:
            question: Follow-up question
            conversation_history: List of previous Q&A pairs
                [{'question': '...', 'answer': '...'}, ...]
            filters: Optional search filters
            
        Returns:
            Same format as ask_question()
        """
        # Combine current question with conversation context
        contextual_question = self._build_contextual_query(
            question, 
            conversation_history
        )
        
        return self.ask_question(
            question=contextual_question,
            filters=filters
        )
    
    def _build_contextual_query(
        self,
        question: str,
        history: List[Dict[str, str]]
    ) -> str:
        """Build enhanced query using conversation history"""
        if not history:
            return question
        
        # Take last 2 exchanges for context
        recent_history = history[-2:]
        
        context_parts = []
        for exchange in recent_history:
            context_parts.append(f"Previous Q: {exchange['question']}")
            context_parts.append(f"Previous A: {exchange['answer'][:200]}...")  # Truncate
        
        context_parts.append(f"Current Q: {question}")
        
        return "\n".join(context_parts)
    
    def analyze_rfp_coverage(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze RFP coverage and generate insights
        
        Returns comprehensive analysis of:
        - Total requirements
        - Categories breakdown
        - Products/modules covered
        - Response readiness
        """
        # This would query all documents and generate analytics
        # Implementation depends on your MongoDB structure
        pass
    
    def compare_requirements(
        self,
        requirement_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple requirements side-by-side
        Uses GPT-4o to generate comparison analysis
        """
        # Retrieve specific requirements and compare
        pass
    
    def suggest_questions(self, rfp_id: Optional[str] = None) -> List[str]:
        """
        Suggest relevant questions users might want to ask
        Based on RFP content analysis
        """
        suggestions = [
            "What are the main technical requirements?",
            "List all integration requirements",
            "What are the security and compliance requirements?",
            "Summarize the fraud detection specifications",
            "What AI/ML capabilities are required?",
            "What are the performance requirements?",
            "List all third-party integrations needed",
            "What are the data migration requirements?",
            "Summarize the deployment and infrastructure needs",
            "What are the testing and quality assurance requirements?"
        ]
        
        return suggestions


# Example usage and testing
if __name__ == "__main__":
    qa_service = IntelligentQAService()
    
    # Test question
    result = qa_service.ask_question(
        question="What are the fraud detection requirements?",
        top_n=5
    )
    
    print(f"\n{'='*60}")
    print(f"Question: What are the fraud detection requirements?")
    print(f"{'='*60}")
    print(f"\nMode: {result['mode']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {len(result['sources'])} documents retrieved")
