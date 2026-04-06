const BASE_URL = "http://127.0.0.1:8000";

export async function uploadDocument(projectId, file) {
  const formData = new FormData();
  formData.append("project_id", projectId);
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers: {
      ...authHeaders(),
    },
    body: formData,
  });

  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token
    ? { Authorization: `Bearer ${token}` }
    : {};
}


export async function askQuestion(projectId, question) {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json" ,
      ...authHeaders(),

    },
    body: JSON.stringify({ project_id: projectId, question }),
  });

  if (!res.ok) throw new Error("Question failed");
  return res.json();
}

export async function fetchProjects() {
  const res = await fetch(`${BASE_URL}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}
