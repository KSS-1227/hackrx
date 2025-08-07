
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [inputMethod, setInputMethod] = useState('link'); // 'upload' or 'link'
  const [documentSource, setDocumentSource] = useState(null); // File object or URL string
  const [questions, setQuestions] = useState(['']);
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Define the base URL for the backend API
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const handleFileChange = (e) => {
    setDocumentSource(e.target.files[0]);
  };

  const handleLinkChange = (e) => {
    setDocumentSource(e.target.value);
  };

  const handleQuestionChange = (idx, value) => {
    const newQuestions = [...questions];
    newQuestions[idx] = value;
    setQuestions(newQuestions);
  };

  const addQuestion = () => {
    setQuestions([...questions, '']);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!documentSource) {
      setError('Please select a file or enter a link.');
      return;
    }

    const filteredQuestions = questions.filter(q => q.trim() !== '');
    if (filteredQuestions.length === 0) {
      setError('Please enter at least one question.');
      return;
    }

    setLoading(true);
    setAnswers([]);
    setError('');

    try {
      let response;
      if (inputMethod === 'upload') {
        const formData = new FormData();
        formData.append('documents', documentSource);
        formData.append('questions', JSON.stringify(filteredQuestions));
        response = await axios.post(`${API_BASE_URL}/hackrx/run`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else { // 'link'
        const payload = {
          documents: [documentSource], // API expects a list of URLs
          questions: filteredQuestions,
        };
        response = await axios.post(`${API_BASE_URL}/hackrx/run/detailed`, payload);
      }
      setAnswers(response.data.answers || []);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'An error occurred.';
      setError(errorMsg);
      setAnswers([errorMsg]);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>HackRx Document Q&A</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', borderBottom: '1px solid #ccc' }}>
          <button type="button" onClick={() => setInputMethod('link')} style={{ all: 'unset', padding: '10px 15px', cursor: 'pointer', backgroundColor: inputMethod === 'link' ? '#e0e0e0' : 'transparent' }}>
            🔗 Paste Link
          </button>
          <button type="button" onClick={() => setInputMethod('upload')} style={{ all: 'unset', padding: '10px 15px', cursor: 'pointer', backgroundColor: inputMethod === 'upload' ? '#e0e0e0' : 'transparent' }}>
            📎 Upload File
          </button>
        </div>

        <div style={{ margin: '16px 0' }}>
          {inputMethod === 'upload' ? (
            <div>
              <label>Upload Document:</label>
              <input type="file" onChange={handleFileChange} style={{ display: 'block', marginTop: '8px' }} />
            </div>
          ) : (
            <div>
              <label>Paste Document Link:</label>
              <input
                type="url"
                placeholder="https://example.com/document.pdf"
                value={documentSource || ''}
                onChange={handleLinkChange}
                style={{ width: '100%', padding: '8px', boxSizing: 'border-box', marginTop: '8px' }}
                required
              />
            </div>
          )}
        </div>

        <div>
          <label>Questions:</label>
          {questions.map((q, idx) => (
            <input
              key={idx}
              type="text"
              value={q}
              onChange={e => handleQuestionChange(idx, e.target.value)}
              style={{ width: '100%', marginBottom: 8, padding: '8px', boxSizing: 'border-box' }}
              required
            />
          ))}
          <button type="button" onClick={addQuestion} style={{ marginBottom: 16 }}>
            + Add Another Question
          </button>
        </div>

        <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>
          {loading ? 'Getting Answers...' : 'Submit'}
        </button>
      </form>

      {error && <div style={{ color: 'red', marginTop: '16px' }}>Error: {error}</div>}

      <div style={{ marginTop: 32 }}>
        {answers.length > 0 && <h3>Answers:</h3>}
        <div>
          {answers.map((ans, idx) => (
            <div key={idx} style={{ marginBottom: 24, borderLeft: '3px solid #0066cc', paddingLeft: 16 }}>
              <h4>Q: {questions.filter(q => q.trim() !== '')[idx]}</h4>
                            <div style={{ whiteSpace: 'pre-wrap', backgroundColor: '#f9f9f9', padding: '10px', borderRadius: '4px', color: '#333' }}>
                {ans}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
