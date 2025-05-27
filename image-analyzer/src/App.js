// App.js
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState('');

  const handleImageChange = (e) => { 
    setImage(e.target.files[0]);
  };

  const handleAnalyze = async () => {
    const formData = new FormData();
    formData.append('image', image);

    try {
      const res = await axios.post('https://sp-3.onrender.com/analyze', formData);
      setResult(`Predicted Class: ${res.data.predicted_class}`);
    } catch (err) {
      console.error(err);
      setResult('Error analyzing image');
    }
  };  // ← closes handleAnalyze

  return (
    <div className="App" style={{ padding: 20 }}>
      <h2>Image Analyzer</h2>
      <input type="file" onChange={handleImageChange} />
      <button onClick={handleAnalyze}>Analyze</button>
      <p><strong>Result:</strong> {result}</p>
    </div>
  );
}

export default App;
