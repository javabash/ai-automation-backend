// frontend/utils/login.ts

export async function login(username: string, password: string) {
  const resp = await fetch("http://localhost:8000/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });

  if (!resp.ok) {
    throw new Error(`Login failed (${resp.status}): ${await resp.text()}`);
  }

  // The API returns {access_token, token_type}
  return await resp.json();
}
