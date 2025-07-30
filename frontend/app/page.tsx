"use client";
import { useState } from "react";
import AskForm from "../components/AskForm";
import AnswerDisplay from "../components/AnswerDisplay";
import SourcesList from "../components/SourcesList";
import LoginForm from "../components/LoginForm";
import { askBackend, login } from "../utils/api";

export default function Home() {
  const [token, setToken] = useState<string>("");
  const [loginError, setLoginError] = useState<string>("");
  const [loadingLogin, setLoadingLogin] = useState(false);

  // For /ask
  const [answer, setAnswer] = useState<string>("");
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (username: string, password: string) => {
    setLoadingLogin(true);
    setLoginError("");
    try {
      const data = await login(username, password);
      console.log("Login API returned:", data);     // <-- See the actual backend response
      if (data && data.access_token) {
        setToken(data.access_token);
      } else {
        setLoginError("Unexpected login response");
        console.error("Login response did not include access_token:", data);
      }
    } catch (err: any) {
      setLoginError("Invalid credentials");
      console.error("Login error:", err);
    }
    setLoadingLogin(false);
  };

  const handleAsk = async (question: string, selectedSources: string[]) => {
    setLoading(true);
    try {
      const data = await askBackend(question, selectedSources, token);
      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err: any) {
      setAnswer("Error: " + err.message);
      setSources([]);
    }
    setLoading(false);
  };

  return (
    <main className="p-8 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Vectorworx AI Frontend</h1>
      {!token ? (
        <>
          <LoginForm onLogin={handleLogin} loading={loadingLogin} />
          {loginError && <div className="text-red-600 mb-2">{loginError}</div>}
        </>
      ) : (
        <>
          <AskForm onAsk={handleAsk} loading={loading} />
          <AnswerDisplay answer={answer} loading={loading} />
          <SourcesList sources={sources} />
        </>
      )}
    </main>
  );
}
