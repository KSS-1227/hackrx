"""
LLM service for generating answers and reasoning using Google Gemini
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from loguru import logger

from app.core.config import settings
from app.core.exceptions import LLMError
from app.models.document import DocumentChunk


class LLMService:
    """Service for LLM-based text generation and reasoning using Google Gemini"""
    
    def __init__(self):
        self.client: Optional[genai.GenerativeModel] = None
        self.model_name = settings.GEMINI_MODEL
        self.use_gemini = bool(settings.GEMINI_API_KEY)
        
        if self.use_gemini:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.client = genai.GenerativeModel(self.model_name)
    
    async def generate_answer(
        self, 
        question: str, 
        context_chunks: List[DocumentChunk],
        max_context_length: int = 8000
    ) -> str:
        """
        Generate an answer to a question based on document context
        
        Args:
            question: The user's question
            context_chunks: Relevant document chunks
            max_context_length: Maximum context length to include
            
        Returns:
            Generated answer string
        """
        try:
            if not self.use_gemini or not self.client:
                return await self._generate_fallback_answer(question, context_chunks)
            
            # Prepare context from chunks
            context = self._prepare_context(context_chunks, max_context_length)
            
            # Create the prompt
            prompt = self._create_answer_prompt(question, context)
            
            # Generate response using Gemini
            response = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                # In the generate_answer method, update the generation_config:
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Slightly higher for more detailed responses
                    max_output_tokens=1500,  # Increased token limit
                    top_p=0.95,  # Add top_p parameter
                    top_k=40,  # Add top_k parameter
                )
            )
            
            answer = response.text.strip()
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return await self._generate_fallback_answer(question, context_chunks)
    
    async def generate_structured_response(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate a structured JSON response"""
        try:
            if not self.use_gemini or not self.client:
                return None
            
            structured_prompt = f"""
{prompt}

Please respond in valid JSON format only. Do not include any text outside the JSON structure.
"""
            
            response = await asyncio.to_thread(
                self.client.generate_content,
                structured_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000,
                )
            )
            
            content = response.text.strip()
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    return json.loads(content[json_start:json_end])
                
                logger.warning("Could not parse Gemini response as JSON")
                return None
                
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            return None
    
    def _prepare_context(self, chunks: List[DocumentChunk], max_length: int) -> str:
        """Prepare context string from document chunks"""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        current_length = 0
        
        # Sort chunks by similarity score if available
        sorted_chunks = sorted(
            chunks,
            key=lambda x: x.metadata.get('similarity_score', 0),
            reverse=True
        )
        
        for i, chunk in enumerate(sorted_chunks):
            chunk_text = f"[Context {i+1}] {chunk.content}"
            
            if current_length + len(chunk_text) > max_length:
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n\n".join(context_parts)
    
    def _create_answer_prompt(self, question: str, context: str) -> str:
        """Create a prompt for answer generation"""
        return f"""
You are an expert document analyst specializing in insurance policies, contracts, and legal documents. Your role is to:

1. Analyze document content accurately and thoroughly
2. Provide precise answers based on the given context
3. Identify relevant clauses, terms, and conditions
4. Explain complex policy language in clear terms
5. Highlight important limitations, exclusions, or requirements
6. Maintain objectivity and accuracy in all responses

Based on the following context from policy documents, please answer the user's question accurately and comprehensively.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer based ONLY on the information provided in the context
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Be specific and cite relevant details from the context
4. If there are specific conditions, requirements, or limitations, mention them
5. Use clear, professional language
6. If amounts, dates, or specific terms are mentioned in the context, include them in your answer

ANSWER:"""
    
    async def _generate_fallback_answer(
        self, 
        question: str, 
        context_chunks: List[DocumentChunk]
    ) -> str:
        """Generate a fallback answer when Gemini is not available"""
        
        if not context_chunks:
            return "I couldn't find relevant information in the provided documents to answer your question."
        
        # Simple keyword-based matching for fallback
        question_lower = question.lower()
        relevant_content = []
        
        for chunk in context_chunks[:3]:  # Use top 3 chunks
            content = chunk.content
            
            # Check if chunk contains question keywords
            question_words = set(question_lower.split())
            content_words = set(content.lower().split())
            
            if question_words.intersection(content_words):
                relevant_content.append(content[:300] + "..." if len(content) > 300 else content)
        
        if relevant_content:
            return f"Based on the available documents:\n\n" + "\n\n".join(relevant_content)
        else:
            return "I found some potentially relevant information, but cannot provide a specific answer without more advanced processing capabilities."
    
    async def evaluate_answer_quality(
        self, 
        question: str, 
        answer: str, 
        context_chunks: List[DocumentChunk]
    ) -> Dict[str, Any]:
        """Evaluate the quality of a generated answer"""
        try:
            if not self.use_gemini or not self.client:
                return {"confidence": 0.5, "reasoning": "Fallback evaluation"}
            
            evaluation_prompt = f"""
Evaluate the quality of this answer based on the question and context provided.

QUESTION: {question}

ANSWER: {answer}

CONTEXT: {self._prepare_context(context_chunks, 2000)}

Please evaluate on these criteria:
1. Accuracy: Is the answer factually correct based on the context?
2. Completeness: Does it fully address the question?
3. Relevance: Is the answer directly relevant to the question?
4. Clarity: Is the answer clear and well-structured?

Respond in JSON format:
{{
    "confidence": 0.0-1.0,
    "accuracy_score": 0.0-1.0,
    "completeness_score": 0.0-1.0,
    "relevance_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "reasoning": "Brief explanation of the evaluation"
}}
"""
            
            evaluation = await self.generate_structured_response(evaluation_prompt)
            
            if evaluation:
                return evaluation
            else:
                return {"confidence": 0.7, "reasoning": "Could not evaluate answer quality"}
                
        except Exception as e:
            logger.error(f"Error evaluating answer quality: {str(e)}")
            return {"confidence": 0.5, "reasoning": f"Evaluation error: {str(e)}"}
    
    async def extract_key_information(self, text: str) -> Dict[str, Any]:
        """Extract key information from text using Gemini"""
        try:
            if not self.use_gemini or not self.client:
                return {}
            
            prompt = f"""
Extract key information from the following text. Focus on:
- Important terms and conditions
- Amounts, dates, and numbers
- Requirements and eligibility criteria
- Exclusions and limitations
- Key entities (people, organizations, procedures, etc.)

TEXT: {text[:4000]}

Respond in JSON format with extracted information.
"""
            
            result = await self.generate_structured_response(prompt)
            return result or {}
            
        except Exception as e:
            logger.error(f"Error extracting key information: {str(e)}")
            return {}
