import React, { useState } from 'react';
import jwt from 'jsonwebtoken';  

function App() {
  const [prompt, setPrompt] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [accessToken, setAccessToken] = useState('');

  const handleLogin = async () => {
    try {
      const response = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      const { access_token } = data;
      setAccessToken(access_token);
    } catch (error) {
      console.error('Error during login:', error.message);
    }
  };

  const handleGenerateData = async () => {
    try {
      // Verify the token before making the request
      const decodedToken = jwt.verify(accessToken, 'your-secret-key');
      if (decodedToken) {
        const response = await fetch('http://localhost:8000/generate_data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({ prompt }),
        });
        const data = await response.json();
        console.log(data.message);
      }
    } catch (error) {
      console.error('Error generating data:', error.message);
    }
  };

  return (
    <div>
      <h1>React Frontend</h1>
      <div>
        <label>Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>
      <div>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <div>
        <button onClick={handleLogin}>Login</button>
      </div>
      <div>
        <label>Prompt:</label>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </div>
      <div>
        <button onClick={handleGenerateData}>Generate Data</button>
      </div>
    </div>
  );
}

export default App;
