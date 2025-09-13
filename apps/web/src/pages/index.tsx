import { useEffect, useState } from "react";

export default function Home() {
  const [apiHealth, setApiHealth] = useState<string>("loading...");
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${base}/health`)
      .then((r) => r.json())
      .then((d) => setApiHealth(d.status || JSON.stringify(d)))
      .catch(() => setApiHealth("unreachable"));
  }, [base]);

  return (
    <main style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>AI English Learning App (MVP)</h1>
      <p>Next.js is running. API health: {apiHealth}</p>
      <p>API base: {base}</p>
    </main>
  );
}

