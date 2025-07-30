"use client";
import { useState } from "react";

export default function LoginForm({ onLogin, loading }: { onLogin: (username: string, password: string) => void, loading: boolean }) {
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("test123");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLogin(username, password);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 flex flex-col gap-2 max-w-xs">
      <input
        className="p-2 border rounded"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <input
        className="p-2 border rounded"
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />
      <button
        className="bg-green-600 text-white rounded px-4 py-2"
        type="submit"
        disabled={loading}
      >
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}
