// frontend/utils/askBackend.ts

export async function askBackend(
  question: string,
  sources: string[],
  token: string
) {
  const resp = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      question,
      sources,
    }),
  });

  if (!resp.ok) {
    throw new Error(`Ask failed (${resp.status}): ${await resp.text()}`);
  }

  // The API returns {answer, sources}
  return await resp.json();
}
