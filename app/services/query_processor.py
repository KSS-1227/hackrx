"""
Query processing service for understanding and structuring user queries
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

from app.services.llm_service import LLMService
from app.core.exceptions import LLMError


@dataclass
class QueryStructure:
    """Structured representation of a user query"""
    original_query: str
    intent: str  # e.g., "coverage_check", "claim_eligibility", "policy_terms"
    entities: Dict[str, Any]  # Extracted entities like age, procedure, location, etc.
    keywords: List[str]
    confidence: float


class QueryProcessor:
    """Service for processing and understanding user queries"""
    
    def __init__(self):
        self.llm_service = LLMService()
        
        # Common patterns for different types of queries
        self.intent_patterns = {
            "coverage_check": [
                r"cover(ed|age|s)?",
                r"eligible|eligibility",
                r"qualify|qualifies",
                r"include(d|s)?",
                r"benefit(s)?"
            ],
            "claim_processing": [
                r"claim(s)?",
                r"reimburse(ment|d)?",
                r"pay(ment|s)?",
                r"approve(d|al)?",
                r"process(ing)?"
            ],
            "policy_terms": [
                r"term(s)?",
                r"condition(s)?",
                r"requirement(s)?",
                r"rule(s)?",
                r"policy"
            ],
            "waiting_period": [
                r"waiting period",
                r"wait(ing)?",
                r"grace period",
                r"effective date"
            ],
            "exclusions": [
                r"exclusion(s)?",
                r"not cover(ed)?",
                r"exclude(d|s)?",
                r"limitation(s)?"
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            "age": r"(\d+)\s*year(s)?\s*old|age\s*(\d+)|(\d+)\s*yo",
            "amount": r"\$?([\d,]+(?:\.\d{2})?)|(\d+)\s*dollar(s)?",
            "duration": r"(\d+)\s*(day|week|month|year)s?",
            "procedure": r"(surgery|operation|treatment|procedure|therapy)",
            "location": r"(hospital|clinic|facility|center|office)",
            "date": r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|(\d{4}[/-]\d{1,2}[/-]\d{1,2})"
        }
    
    async def process_query(self, query: str) -> QueryStructure:
        """Process and structure a user query"""
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Basic preprocessing
            cleaned_query = self._preprocess_query(query)
            
            # Extract intent
            intent = self._extract_intent(cleaned_query)
            
            # Extract entities
            entities = self._extract_entities(cleaned_query)
            
            # Extract keywords
            keywords = self._extract_keywords(cleaned_query)
            
            # Use LLM for advanced understanding if available
            enhanced_structure = await self._enhance_with_llm(
                cleaned_query, intent, entities, keywords
            )
            
            if enhanced_structure:
                return enhanced_structure
            
            # Fallback to rule-based structure
            return QueryStructure(
                original_query=query,
                intent=intent,
                entities=entities,
                keywords=keywords,
                confidence=0.7  # Medium confidence for rule-based processing
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            # Return basic structure as fallback
            return QueryStructure(
                original_query=query,
                intent="general",
                entities={},
                keywords=query.lower().split(),
                confidence=0.3
            )
    
    def _preprocess_query(self, query: str) -> str:
        """Clean and preprocess the query"""
        # Convert to lowercase
        cleaned = query.lower().strip()
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove special characters but keep important punctuation
        cleaned = re.sub(r'[^\w\s\-\$\.,\?]', '', cleaned)
        
        return cleaned
    
    def _extract_intent(self, query: str) -> str:
        """Extract the intent from the query using pattern matching"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            # Return intent with highest score
            return max(intent_scores, key=intent_scores.get)
        
        return "general"
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query using regex patterns"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                if entity_type == "age":
                    # Extract age value
                    for match in matches:
                        age_val = next((m for m in match if m.isdigit()), None)
                        if age_val:
                            entities["age"] = int(age_val)
                            break
                
                elif entity_type == "amount":
                    # Extract monetary amount
                    for match in matches:
                        amount_str = match[0] if match[0] else match[1]
                        if amount_str:
                            # Clean and convert to float
                            amount_clean = re.sub(r'[,$]', '', amount_str)
                            try:
                                entities["amount"] = float(amount_clean)
                                break
                            except ValueError:
                                continue
                
                elif entity_type == "duration":
                    # Extract duration
                    for match in matches:
                        if len(match) >= 2:
                            try:
                                value = int(match[0])
                                unit = match[1].lower()
                                entities["duration"] = {"value": value, "unit": unit}
                                break
                            except ValueError:
                                continue
                
                else:
                    # For other entities, just store the first match
                    entities[entity_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return entities
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from the query"""
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its',
            'our', 'their'
        }
        
        # Split into words and filter
        words = query.lower().split()
        keywords = []
        
        for word in words:
            # Clean word
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Filter out stop words and short words
            if (clean_word not in stop_words and 
                len(clean_word) > 2 and 
                clean_word.isalpha()):
                keywords.append(clean_word)
        
        return keywords
    
    async def _enhance_with_llm(
        self, 
        query: str, 
        intent: str, 
        entities: Dict[str, Any], 
        keywords: List[str]
    ) -> Optional[QueryStructure]:
        """Use LLM to enhance query understanding"""
        try:
            # Create a prompt for query analysis
            prompt = f"""
            Analyze the following user query and extract structured information:
            
            Query: "{query}"
            
            Please provide:
            1. Intent (coverage_check, claim_processing, policy_terms, waiting_period, exclusions, or general)
            2. Key entities (age, amount, duration, procedure, location, date, etc.)
            3. Important keywords
            4. Confidence score (0.0 to 1.0)
            
            Current analysis:
            - Intent: {intent}
            - Entities: {entities}
            - Keywords: {keywords}
            
            Respond in JSON format:
            {{
                "intent": "...",
                "entities": {{}},
                "keywords": [],
                "confidence": 0.0,
                "reasoning": "..."
            }}
            """
            
            response = await self.llm_service.generate_structured_response(prompt)
            
            if response and isinstance(response, dict):
                return QueryStructure(
                    original_query=query,
                    intent=response.get("intent", intent),
                    entities=response.get("entities", entities),
                    keywords=response.get("keywords", keywords),
                    confidence=response.get("confidence", 0.8)
                )
            
        except Exception as e:
            logger.warning(f"LLM enhancement failed, using rule-based analysis: {str(e)}")
        
        return None
    
    def get_search_terms(self, query_structure: QueryStructure) -> List[str]:
        """Generate search terms for vector search based on query structure"""
        search_terms = []
        
        # Add original query
        search_terms.append(query_structure.original_query)
        
        # Add keywords
        search_terms.extend(query_structure.keywords)
        
        # Add entity-based terms
        for entity_type, value in query_structure.entities.items():
            if entity_type == "age" and isinstance(value, int):
                search_terms.extend([
                    f"{value} years old",
                    f"age {value}",
                    f"minimum age {value}",
                    f"maximum age {value}"
                ])
            elif entity_type == "amount" and isinstance(value, (int, float)):
                search_terms.extend([
                    f"${value:,.2f}",
                    f"{value} dollars",
                    f"cost {value}",
                    f"limit {value}"
                ])
            elif entity_type == "duration" and isinstance(value, dict):
                duration_val = value.get("value")
                duration_unit = value.get("unit")
                search_terms.extend([
                    f"{duration_val} {duration_unit}",
                    f"{duration_val} {duration_unit}s",
                    f"period {duration_val} {duration_unit}"
                ])
        
        # Add intent-specific terms
        intent_terms = {
            "coverage_check": ["coverage", "covered", "eligible", "benefits"],
            "claim_processing": ["claim", "reimbursement", "payment", "approval"],
            "policy_terms": ["terms", "conditions", "requirements", "rules"],
            "waiting_period": ["waiting period", "grace period", "effective date"],
            "exclusions": ["exclusions", "not covered", "limitations"]
        }
        
        if query_structure.intent in intent_terms:
            search_terms.extend(intent_terms[query_structure.intent])
        
        # Remove duplicates and empty terms
        unique_terms = list(set(term.strip() for term in search_terms if term.strip()))
        
        return unique_terms