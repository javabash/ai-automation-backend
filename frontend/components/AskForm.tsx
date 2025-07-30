// frontend/components/AskForm.tsx
"use client";
import { useState } from "react";

const retrieverOptions = ["mock", "chroma", "faiss"];

export default function AskForm({
  onAsk,
  loading,
}: {
  onAsk: (q: string, sources: string[]) => void;
  loading: boolean;
}) {
  const [question, setQuestion] = useState("");
  const [sources, setSources] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question && sources.length) onAsk(question, sources);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 flex flex-col gap-2">
      <input
        className="p-2 border rounded"
        placeholder="Enter your question..."
        value={question}
        onChange={e => setQuestion(e.target.value)}
      />
      <div className="flex gap-2">
        {retrieverOptions.map(opt => (
          <label key={opt} className="flex items-center">
            <input
              type="checkbox"
              value={opt}
              onChange={e => setSources(s =>
                e.target.checked ? [...s, opt] : s.filter(x => x !== opt)
              )}
            />
            <span className="ml-1">{opt}</span>
          </label>
        ))}
      </div>
      <button
        className="bg-blue-500 text-white rounded px-4 py-2"
        type="submit"
        disabled={loading}
      >
        {loading ? "Asking..." : "Ask"}
      </button>
    </form>
  );
}
