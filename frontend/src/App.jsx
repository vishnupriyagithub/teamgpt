import { useState, useEffect } from "react";
import { uploadDocument, askQuestion ,fetchProjects} from "./api";
import "./styles.css";
import { GoogleLogin } from "@react-oauth/google";
import { useRef } from "react";

export default function App() {
  const [projectId, setProjectId] = useState("");
  const [projects, setProjects] = useState([]);
  const [newProjectId, setNewProjectId] = useState("");
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const chatEndRef = useRef(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showNewProject, setShowNewProject] = useState(false);

  useEffect(() => {
  chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


  useEffect(() => {
    if (!token) return;
    fetchProjects()
      .then((data) => setProjects(data.projects || []))
      .catch(() => setProjects([]));
  }, [token]);

  const activeProjectId = newProjectId || projectId;
  // 
  const handleGoogleLogin = async (credentialResponse) => {
    try{
      const googleIdToken = credentialResponse.credential;
      const res = await fetch("http://127.0.0.1:8000/auth/google", {

        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: googleIdToken }),
      });
      console.log("Status:", res.status);
      if (!res.ok) throw new Error("Google login failed");
      const data = await res.json();
      console.log("Response data:", data);
      setProjects([]);
      setProjectId("");
      setNewProjectId("");
      setFile(null);
      setQuestion("");
      setMessages([]);

      if(!data.access_token) throw new Error("No access token in response");
      localStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);

    } catch (e) {
      console.error("Login error", e);
      alert("Google login failed,please try gain")
    }
    
  };
  // logout
  const handleLogout = () => {
    localStorage.clear();
    setToken(null);
    setProjects([]);
    setProjectId("");
    setNewProjectId("");
    setFile(null);
    setQuestion("");
    setAnswer("");

  };
  const handleNewProject = () => {
    const name = prompt("Enter project name:");
    if (!name) return;

    setProjectId(name);
    setMessages([]);
  };

  




  // 
  const handleUpload = async () => {
    if (!activeProjectId || !file) return alert("Project ID & file required");

    setLoading(true);
    try {
      await uploadDocument(activeProjectId, file);
      alert("Document uploaded successfully");
      const data = await fetchProjects();
      setProjects(data.projects || []);
      setNewProjectId("");
      setProjectId(activeProjectId);
    } catch (e) {
      alert(e.message);
    }
    setLoading(false);
  };

  const handleAsk = async () => {
    if (!activeProjectId || !question) return alert("Missing fields");
    const userMessage = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    
    try {
      const res = await askQuestion(activeProjectId, question);
      const assistantMessage = { role: "assistant", content: res.answer };
      setMessages((prev) => [...prev, assistantMessage]);
      
    } catch (e) {
      alert(e.message);
    }
    setLoading(false);
  };

  // block app if not logged in
  if (!token) {
    return (
      <div className="container">
        <h1>TeamGPT</h1>
        <p className="subtitle">Project Knowledge Assistant</p>

        <div className="card">
          <p>Please sign in with Google to continue</p>
          <GoogleLogin
            onSuccess={handleGoogleLogin}
            onError={() => alert("Google Login Failed")}
          />
        </div>
      </div>
    );
  }
  return (

    <div className="app-layout">

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-header">
          <button onClick={() => setSidebarOpen(!sidebarOpen)}>
            ☰
          </button>
          <button className="new-project-btn" onClick={handleNewProject}>
            + New Project
          </button>
        </div>

        <div className="project-list">
          {projects.map((p) => (
            <div
              key={p}
              className={`project-item ${projectId === p ? "active" : ""}`}
              onClick={() => setProjectId(p)}
            >
              {p}
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-area">

        {/* Top Bar */}
        <div className="top-bar">
          <h2>TeamGPT</h2>
          <h3>{projectId}</h3>
          <button onClick={handleLogout}>Logout</button>
        </div>

        {/* Chat Messages */}
        <div className="chat-window">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-bubble ${msg.role}`}
            >
              {msg.content}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Upload button inside project */}
        {projectId && (
          <div className="upload-bar">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={handleUpload}>Upload</button>
          </div>
        )}

        {/* Input Area */}
        <div className="chat-input-area">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask something..."
          />
          <button onClick={handleAsk}>Ask</button>
        </div>

      </div>

    </div>
  );

  // 

  // return (
  //   <div className="container">
  //     <div className="header">

  //       <h1>TeamGPT</h1>
  //       <button onClick={handleLogout}>Logout</button>
  //     </div>

  //     <p className="subtitle">Project Knowledge Assistant</p>

  //     {/* PROJECT SELECTION */}
  //     <div className="card">
  //       <label>Existing Project</label>
  //       <select
  //         value={projectId}
  //         onChange={(e) => {
  //           setProjectId(e.target.value);
  //           setNewProjectId("");
  //         }}
  //       >
  //         <option value="">Select a project</option>
  //         {projects.map((p) => (
  //           <option key={p} value={p}>
  //             {p}
  //           </option>
  //         ))}
  //       </select>

  //       <label>Or create new project</label>
  //       <input
  //         placeholder="New project name"
  //         value={newProjectId}
  //         onChange={(e) => {
  //           setNewProjectId(e.target.value);
  //           setProjectId("");
  //         }}
  //       />
  //     </div>

  //     {/* UPLOAD */}
  //     <div className="card">
  //       <input
  //         type="file"
  //         onChange={(e) => setFile(e.target.files[0])}
  //       />

  //       <button onClick={handleUpload} disabled={loading}>
  //         Upload Document
  //       </button>
  //     </div>

  //     {/* ASK */}
  //     <div className="card">
  //       <textarea
  //         placeholder="Ask a question about the project..."
  //         value={question}
  //         onChange={(e) => setQuestion(e.target.value)}
  //       />

  //       <button onClick={handleAsk} disabled={loading}>
  //         Ask
  //       </button>
  //       <div className="chat-window">
  //         {messages.map((msg, index) => (
  //           <div key={index} className={`chat-bubble ${msg.role === "user" ? "user" : "assistant"}`}>

  //             {msg.content}
  //           </div>
  //         ))}
  //         {loading && (<div className="chat-bubble assistant">...</div>)}
  //         <div ref={chatEndRef} />

  //       </div>
  //     </div>
  //   </div>
  // );
}