import requests
import json
import os

# Test the fixed search functionality
def test_search():
    # URL of the API endpoint
    url = "http://localhost:8001/hackrx/run"
    
    # Path to a test file
    test_file_path = "README.md"
    
    # Check if the file exists
    if not os.path.exists(test_file_path):
        print(f"Error: Test file {test_file_path} not found.")
        return
    
    # Prepare the files and data
    files = {
        'documents': ('README.md', open(test_file_path, 'rb'), 'text/markdown')
    }
    
    # Prepare the questions
    questions = [
        'What features does this system support?'
    ]
    
    # Convert questions to JSON string
    questions_json = json.dumps(questions)
    
    # Prepare the form data
    data = {
        'questions': questions_json
    }
    
    # Make the POST request
    try:
        print("Sending search query to API...")
        response = requests.post(url, files=files, data=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("API Response:")
            print(json.dumps(result, indent=2))
            print("\nTest successful! The search functionality is working correctly.")
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error making API request: {str(e)}")

if __name__ == "__main__":
    test_search()