import React, { useState } from "react";
import './App.css';


function App() {
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [user, setUser] = useState("");
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleLogin = async () => {
    const res = await fetch("/api/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    const data = await res.json();
    if (res.ok) {
      setUser(data.username);
      setError("");
    } else {
      setError(data.error);
    }
  };

  const handleSummarizeText = async () => {
    const res = await fetch("/api/summarize", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    if (res.ok) setSummary(data.summary);
    else setError(data.error);
  };

  const handleSummarizeFile = async () => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("/api/summarize-file", {
      method: "POST",
      credentials: "include",
      body: formData,
    });
    const data = await res.json();
    if (res.ok) setSummary(data.summary);
    else setError(data.error);
  };

  if (!user) {
    return (
      <div className="container">
        <div style={{ padding: 20 }}>
          <h2>Login</h2>
          <input placeholder="Username"  type='username' onChange={e => setCredentials({ ...credentials, username: e.target.value })} />
          <br />
          <input type="password" placeholder="Password" onChange={e => setCredentials({ ...credentials, password: e.target.value })} />
          <br />
          <button onClick={handleLogin}>Login</button>
          {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
      </div>
      
    );
  }

  return (

    <div className="container">
        <div style={{ padding: 20 }}>
        <h1>Welcome, {user}</h1>
        <textarea rows="6" value={text} onChange={e => setText(e.target.value)} placeholder="Paste your note here" />
        <br />
        <button onClick={handleSummarizeText}>Summarize Text</button>

        <hr />
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <button onClick={handleSummarizeFile}>Summarize File</button>

        <hr />
        {summary && (
          <>
            <h3>📌 Summary:</h3>
            <p>{summary}</p>
          </>
        )}
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    </div>
    
  );
}

export default App;
