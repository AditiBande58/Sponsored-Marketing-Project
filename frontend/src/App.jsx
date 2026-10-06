import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { api } from "./api";
import Checkpoint from "./screens/Checkpoint";
import Debrief from "./screens/Debrief";
import Intro from "./screens/Intro";
import Researcher from "./screens/Researcher";
import Shop from "./screens/Shop";

const ID_KEY = "campus-cart-participant";
const PHASE_KEY = "campus-cart-phase";
const RECEIPT_KEY = "campus-cart-receipt";

function clearRun(participantId) {
  localStorage.removeItem(ID_KEY);
  sessionStorage.removeItem(PHASE_KEY);
  sessionStorage.removeItem(RECEIPT_KEY);
  if (!participantId) return;
  const prefix = `campus-cart-draft:${participantId}:`;
  for (let index = localStorage.length - 1; index >= 0; index -= 1) {
    const key = localStorage.key(index);
    if (key && key.startsWith(prefix)) localStorage.removeItem(key);
  }
}

function Study() {
  const [phase, setPhase] = useState("loading");
  const [session, setSession] = useState(null);
  const [receipt, setReceipt] = useState(null);

  useEffect(() => {
    const id = localStorage.getItem(ID_KEY);
    if (!id) {
      setPhase("intro");
      return undefined;
    }
    let cancelled = false;
    api(`/api/sessions/${id}`)
      .then((data) => {
        if (cancelled) return;
        setSession(data.session);
        if (data.session.completed) {
          setPhase("debrief");
          return;
        }
        const savedReceipt = sessionStorage.getItem(RECEIPT_KEY);
        if (sessionStorage.getItem(PHASE_KEY) === "checkpoint" && savedReceipt) {
          try {
            const parsed = JSON.parse(savedReceipt);
            if (parsed && data.session.current_round === parsed.round_num + 1) {
              setReceipt(parsed);
              setPhase("checkpoint");
              return;
            }
          } catch {
            // The saved receipt is unreadable, so open the current aisle.
          }
        }
        setPhase("shop");
      })
      .catch(() => {
        if (cancelled) return;
        localStorage.removeItem(ID_KEY);
        setPhase("intro");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function start(payload) {
    const data = await api("/api/sessions", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    localStorage.setItem(ID_KEY, data.session.participant_id);
    sessionStorage.removeItem(PHASE_KEY);
    sessionStorage.removeItem(RECEIPT_KEY);
    setSession(data.session);
    setReceipt(null);
    setPhase("shop");
  }

  async function finishRound(payload) {
    const roundNum = session.round.round_num;
    const data = await api(
      `/api/sessions/${session.participant_id}/rounds/${roundNum}`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
    setSession(data.session);
    if (data.session.completed) {
      sessionStorage.removeItem(PHASE_KEY);
      sessionStorage.removeItem(RECEIPT_KEY);
      setPhase("debrief");
      return;
    }
    if (data.receipt) {
      sessionStorage.setItem(PHASE_KEY, "checkpoint");
      sessionStorage.setItem(RECEIPT_KEY, JSON.stringify(data.receipt));
      setReceipt(data.receipt);
      setPhase("checkpoint");
      return;
    }
    setPhase("shop");
  }

  function continueShopping() {
    sessionStorage.removeItem(PHASE_KEY);
    sessionStorage.removeItem(RECEIPT_KEY);
    setReceipt(null);
    setPhase("shop");
  }

  function abandon() {
    clearRun(session?.participant_id);
    setSession(null);
    setReceipt(null);
    setPhase("intro");
  }

  return (
    <div className="page">
      {phase === "loading" && <p className="loading">Opening the store…</p>}
      {phase === "intro" && <Intro onStart={start} />}
      {phase === "shop" && session?.round && (
        <Shop session={session} onComplete={finishRound} onAbandon={abandon} />
      )}
      {phase === "checkpoint" && session?.round && receipt && (
        <Checkpoint
          receipt={receipt}
          nextRound={session.round.round_num}
          nextTitle={session.round.title}
          nextBlurb={session.round.blurb}
          nextBudget={session.round.budget}
          totalRounds={session.total_rounds}
          onContinue={continueShopping}
          onAbandon={abandon}
        />
      )}
      {phase === "debrief" && session && <Debrief session={session} onAgain={abandon} />}
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Study />} />
      <Route path="/researcher" element={<Researcher />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
