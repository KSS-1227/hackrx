"""
Simple test script for the LLM Document Processing API
"""

import asyncio
import httpx
import json
from typing import List


class APITester:
    """Test client for the document processing API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", bearer_token: str = "dev-bearer-token"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
    
    async def test_health(self):
        """Test the health endpoint"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                print(f"Health Check: {response.status_code}")
                print(f"Response: {response.json()}")
                return response.status_code == 200
            except Exception as e:
                print(f"Health check failed: {e}")
                return False
    
    async def test_document_processing(
        self, 
        document_urls: List[str], 
        questions: List[str]
    ):
        """Test document processing endpoint"""
        
        payload = {
            "documents": document_urls,
            "questions": questions
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                print("Sending request to /hackrx/run...")
                print(f"Documents: {document_urls}")
                print(f"Questions: {questions}")
                
                response = await client.post(
                    f"{self.base_url}/hackrx/run",
                    headers=self.headers,
                    json=payload
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("Success!")
                    print(f"Processing Time: {result.get('processing_time', 'N/A')} seconds")
                    print(f"Document Count: {result.get('document_count', 'N/A')}")
                    print("\nAnswers:")
                    for i, answer in enumerate(result.get('answers', []), 1):
                        print(f"{i}. {answer}")
                else:
                    print(f"Error: {response.text}")
                
                return response.status_code == 200
                
            except Exception as e:
                print(f"Request failed: {e}")
                return False
    
    async def test_detailed_processing(
        self, 
        document_urls: List[str], 
        questions: List[str]
    ):
        """Test detailed document processing endpoint"""
        
        payload = {
            "documents": document_urls,
            "questions": questions
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                print("Sending request to /hackrx/run/detailed...")
                
                response = await client.post(
                    f"{self.base_url}/hackrx/run/detailed",
                    headers=self.headers,
                    json=payload
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("Success!")
                    print(f"Processing Time: {result.get('processing_time', 'N/A')} seconds")
                    print(f"Document Count: {result.get('document_count', 'N/A')}")
                    
                    print("\nDocument Details:")
                    for doc in result.get('documents', []):
                        print(f"- {doc.get('filename', 'Unknown')}: {doc.get('chunks', 0)} chunks")
                    
                    print("\nAnswers:")
                    for i, answer in enumerate(result.get('answers', []), 1):
                        print(f"{i}. {answer}")
                else:
                    print(f"Error: {response.text}")
                
                return response.status_code == 200
                
            except Exception as e:
                print(f"Request failed: {e}")
                return False


async def main():
    """Main test function"""
    print("=== LLM Document Processing API Test ===\n")
    
    tester = APITester()
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health_ok = await tester.test_health()
    print(f"Health check: {'✓' if health_ok else '✗'}\n")
    
    if not health_ok:
        print("API is not running. Please start the server first.")
        return
    
    # Example test data
    # Note: Replace these with actual document URLs for real testing
    test_documents = [
        "https://example.com/sample-policy.pdf",  # Replace with real URLs
        "https://example.com/terms-conditions.docx"
    ]
    
    test_questions = [
        "What is the coverage limit for medical procedures?",
        "What is the waiting period for new policies?",
        "Are pre-existing conditions covered?",
        "What are the exclusions in this policy?"
    ]
    
    print("2. Testing basic document processing...")
    basic_ok = await tester.test_document_processing(test_documents, test_questions)
    print(f"Basic processing: {'✓' if basic_ok else '✗'}\n")
    
    print("3. Testing detailed document processing...")
    detailed_ok = await tester.test_detailed_processing(test_documents, test_questions)
    print(f"Detailed processing: {'✓' if detailed_ok else '✗'}\n")
    
    print("=== Test Summary ===")
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    print(f"Basic Processing: {'✓' if basic_ok else '✗'}")
    print(f"Detailed Processing: {'✓' if detailed_ok else '✗'}")


if __name__ == "__main__":
    asyncio.run(main())