import { useEffect, useState } from "react";
import { api } from "../api";
import Chrome from "../Chrome";

const FOCUS = [1, 2, 3, 4, 5, 6, 7];

export default function Intro({ onStart }) {
  const [aisles, setAisles] = useState([]);
  const [focus, setFocus] = useState(null);
  const [code, setCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    api("/api/aisles")
      .then((data) => {
        if (!cancelled) setAisles(data.aisles || []);
      })
      .catch(() => {
        if (!cancelled) setAisles([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function submit(event) {
    event.preventDefault();
    if (!focus || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      await onStart({
        participant_code: code.trim(),
        cognitive_state: focus,
      });
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  }

  return (
    <>
      <Chrome showResearcher />
      <div className="intro-layout">
        <form className="panel" onSubmit={submit}>
          <h1>Shop ten aisles with play money.</h1>
          <p className="lede">
            Campus Cart is a pretend store for a class study. Nothing is charged.
            Shop the way you would with your own money.
          </p>
          <ol className="steps">
            <li>Each aisle has its own budget.</li>
            <li>Click an item to look at it, then add what you want.</li>
            <li>Buy at least one thing, then check out. Please do this once.</li>
          </ol>

          <fieldset className="field">
            <legend>How focused do you feel right now?</legend>
            <div className="scale" role="radiogroup" aria-label="How focused do you feel right now?">
              {FOCUS.map((value) => (
                <button
                  key={value}
                  type="button"
                  role="radio"
                  aria-checked={focus === value}
                  className={focus === value ? "scale-btn selected" : "scale-btn"}
                  onClick={() => setFocus(value)}
                >
                  {value}
                </button>
              ))}
            </div>
            <div className="scale-ends">
              <span>Very distracted</span>
              <span>Very focused</span>
            </div>
          </fieldset>

          <label className="field" htmlFor="participant-code">
            Class or participant ID
            <span className="optional">Optional</span>
            <input
              id="participant-code"
              value={code}
              maxLength={64}
              autoComplete="off"
              placeholder="Only if you were given one"
              onChange={(event) => setCode(event.target.value)}
            />
          </label>

          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}

          <button className="primary" type="submit" disabled={!focus || submitting}>
            {submitting ? "Opening aisle 1…" : "Start shopping"}
          </button>
          <p className="fine">
            Starting saves your choices for the project. There is no account and no payment.
          </p>
        </form>

        <aside className="poster">
          <p className="poster-kicker">On the list</p>
          <p className="poster-title">Ten short stops.</p>
          {aisles.length > 0 ? (
            <ol>
              {aisles.map((aisle) => (
                <li key={aisle.title}>{aisle.title}</li>
              ))}
            </ol>
          ) : (
            <p>Snacks, dorm gear, tech, and a few more stops along the way.</p>
          )}
        </aside>
      </div>
    </>
  );
}
