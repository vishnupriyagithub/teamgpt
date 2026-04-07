import { useState, useEffect } from "react";
import { uploadDocument, askQuestion ,fetchProjects} from "./api";
import "./styles.css";
import { GoogleLogin } from "@react-oauth/google";
import { useRef } from "react";
import {Menu, Plus, Folder} from "lucide-react";

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
  const [username, setUsername] = useState(
  localStorage.getItem("user_name") || "User"
  );
  const [userPicture, setUserPicture] = useState(
    localStorage.getItem("user_picture") || "👤 "
  );


  

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const res = await fetch("http://127.0.0.1:8000/projects", { 
          headers: {
            Authorization: `Bearer ${token}`,
          }
        });
        if (!res.ok) throw new Error("Invalid token");
        setToken(token);

      }catch (e) {
        console.error("Token validation failed", e);
        localStorage.clear();
        setToken(null);
      }
    };
    validateToken();
  }, []);


  useEffect(() => {
  chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (projectId){
      loadChat(projectId);
    }
  }, [projectId]);


  useEffect(() => {
    if (!token) return;
    fetchProjects()
      .then((data) => setProjects(data.projects || []))
      .catch(() => setProjects([]));
  }, [token]);

  const activeProjectId = newProjectId || projectId;
  


  const loadChat = async (projectId) => {

    try {
      const res = await fetch(`http://127.0.0.1:8000/chat/${projectId}`,{
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        }
      });
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (e) {
      console.error("Failed to load chat", e);
    }
  };



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
      localStorage.setItem("user_name", data.user?.name || "User");
      localStorage.setItem("user_picture", data.user?.picture || "");
      setToken(data.access_token);
      setUsername(data.user?.name || "User");
      setUserPicture(data.user?.picture || "");

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
    // setAnswer("");

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
      console.log("Uploading document", { projectId: activeProjectId, file });
      await uploadDocument(activeProjectId, file);
      alert("Document uploaded successfully");
      const data = await fetchProjects();
      setProjects(data.projects || []);
      setNewProjectId("");
      setProjectId(activeProjectId);
      setFile(null);
    } catch (e) {
      alert(e.message,"eorrrrr");
    }
    setLoading(false);
  };

  const handleUploadDirect = async (selectedFile, activeProjectId) => {
    setLoading(true);

    try {
      console.log("Uploading:", selectedFile.name, "to project:", activeProjectId);

      const res = await uploadDocument(activeProjectId, selectedFile);

      console.log("Upload response:", res);

      alert("Document uploaded successfully");

      const data = await fetchProjects();
      setProjects(data.projects || []);

      setProjectId(activeProjectId);

    // reset file input
      document.getElementById("fileUpload").value = "";

    } catch (e) {
      console.error("Upload error:", e);
      alert("Upload failed");
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
      <div className="login-page">
      <div className="login-card">
        <h1 className="logo">TeamGPT</h1>
        <p className="subtitle">Project Knowledge Assistant</p>

        <p className="login-text">
          Sign in with Google to continue
        </p>

        <div className="google-btn">
          <GoogleLogin
            onSuccess={handleGoogleLogin}
            onError={() => alert("Google Login Failed")}
          />
        </div>
      </div>
    </div>
    );
  }
  return (

    <div className="app-layout">

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-top">
          <button
          className="menu-btn"
          onClick={()=> setSidebarOpen(!sidebarOpen)}
          >
          <Menu size={20} stroke="white" />
          </button>
        </div>
        
        {/* new project */}
        <div className="sidebar-header">
            <button className= "new-project-btn" onClick={handleNewProject}>
            <Plus size={18} style={{minWidth:"18px"}}/>
            {sidebarOpen && <span>New Project</span>}
          </button>
        </div>
        {/* Projects */}
        <div className="project-list">
          {projects.map((p) => (
            <div
              key={p}
              className={`project-item ${projectId === p ? "active" : ""}`}
              onClick={() => {
                setProjectId(p);
                loadChat(p);
              }}
              title={p}
            >
              <Folder size={18} style={{minWidth:"18px"}} />
              {sidebarOpen && <span>{p}</span>}
            </div>
          ))}
        </div>
        <div className="sidebar-footer">
          <div className="user-info">
            {userPicture ? (
              <img src={userPicture} alt="avatar" className="avatar-img" />
            ) : (
              <div className="avatar">
                {username.charAt(0).toUpperCase()}
              </div>
            )}
            {sidebarOpen && <span>{username}</span>}
          </div>
        </div> 
      
        
      </div>

        {/* <div className="sidebar-header">
          <button style={{fontSize:"18px"}} onClick={() => setSidebarOpen(!sidebarOpen)}>
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
              onClick={() => {
                setProjectId(p);
                loadChat(p);
              }}
            >
              {p}
            </div>
          ))}
        </div>
      </div> */}

      {/* Main Chat Area */}
      <div className="main-area">

        {/* Top Bar */}
        <div className="top-bar">
          <h2>TeamGPT</h2>
          
          <button onClick={handleLogout}>Logout</button>
        </div>

        {/* Chat Messages */}
        <div className="chat-container">
          <div className="chat-window">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`chat-bubble ${msg.role}`}
              >
                {msg.content}
              </div>
            ))}
            {loading && <div className="chat-bubble assistant">
              <span className="typing-dots">•••</span>
              </div>}
            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Upload button inside project */}
        {/* {projectId && (
          <div className="upload-bar">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={handleUpload}>Upload</button>
          </div>
        )} */}

        {/* Input Area */}
        <div className="chat-input-area">
          <input
            type="file"
            id="fileUpload"
            style={{ display: "none" }}
            onChange={(e) => {
              const selectedFile = e.target.files[0];
              if(!selectedFile) return;
              if(!activeProjectId) return alert("Please select or create a project first");
              handleUploadDirect(selectedFile, activeProjectId);
            }}
              
          />
          <button
            className="upload-btn"
            onClick={() => document.getElementById("fileUpload").click()}
          >
            <Plus size={18} color="#ffff" />
          </button>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask something..."
            onKeyDown={(e)=>{
              if(e.key === "Enter") handleAsk();
            }}
          />
          <button className="send-btn" onClick={handleAsk} disabled={loading}>
            {loading ? "..." : "Send"}
          </button>
          
        </div>

      </div>

    </div>

  );
};
