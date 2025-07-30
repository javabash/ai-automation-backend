// frontend/utils/api.ts

// Ask endpoint (POST /ask)
export async function askBackend(question: string, sources: string[], token: string) {
  const res = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ question, sources }),
  });
  if (!res.ok) {
    throw new Error("API error");
  }
  return res.json();
}

// Login endpoint (POST /token)
export async function login(username: string, password: string) {
  const res = await fetch("http://localhost:8000/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}
