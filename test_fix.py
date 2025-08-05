import requests
import json
import os

# Test file path
test_file_path = os.path.join(os.getcwd(), 'README.md')

# Ensure the file exists
if not os.path.exists(test_file_path):
    with open(test_file_path, 'w') as f:
        f.write('# Test Document\n\nThis is a test document for the LLM Document Processing System.\n\nIt contains information about knee surgery and medical policies.')

# API endpoint
url = 'http://localhost:8001/hackrx/run'

# Prepare the files and data
files = {
    'documents': ('test.md', open(test_file_path, 'rb'), 'text/markdown')
}

# Prepare the questions
questions = [
    'Does this document mention knee surgery?'
]

# Convert questions to JSON string
questions_json = json.dumps(questions)

# Prepare the form data
data = {
    'questions': questions_json
}

# Make the request
print('Sending request to API...')
response = requests.post(url, files=files, data=data)

# Print the response
print(f'Status code: {response.status_code}')
if response.status_code == 200:
    print('Success! Response:')
    print(json.dumps(response.json(), indent=2))
else:
    print('Error! Response:')
    print(response.text)