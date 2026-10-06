import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, money } from "../api";
import Chrome from "../Chrome";

const STORE = "campus-cart-researcher-key";

function formatShare(value) {
  if (value == null) return "—";
  return `${(value * 100).toFixed(1)}%`;
}

function formatPoints(value) {
  if (value == null) return "Not enough data";
  const amount = (value * 100).toFixed(1);
  return `${value > 0 ? "+" : ""}${amount} percentage points`;
}

function signedMoney(value) {
  if (value == null) return "Not enough data";
  if (value > 0) return `+${money(value)}`;
  return money(value);
}

function Meter({ value, max, text }) {
  const width = value == null || !max ? 0 : Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div className="share-meter">
      <div className="share-fill" style={{ width: `${width}%` }} />
      <span>{text}</span>
    </div>
  );
}

function Compare({ title, unlabeled, sponsored, format, max }) {
  return (
    <div className="compare">
      <h3>{title}</h3>
      <div className="compare-row">
        <span>No label</span>
        <Meter value={unlabeled} max={max} text={format(unlabeled)} />
      </div>
      <div className="compare-row">
        <span>Sponsored</span>
        <Meter value={sponsored} max={max} text={format(sponsored)} />
      </div>
    </div>
  );
}

function Effect({ title, effect, format }) {
  if (!effect) {
    return (
      <p>
        <strong>{title}: </strong>Need at least two participants.
      </p>
    );
  }
  return (
    <p>
      <strong>{title}: </strong>
      {format(effect.estimate)}
      <span className="fine">
        {" "}
        95% interval {format(effect.ci_low)} to {format(effect.ci_high)}, from{" "}
        {effect.n_participants} people resampled {effect.n_boot} times.
      </span>
    </p>
  );
}

export default function Researcher() {
  const [key, setKey] = useState("");
  const [authed, setAuthed] = useState(false);
  const [completedOnly, setCompletedOnly] = useState(false);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load(nextKey, onlyCompleted) {
    setLoading(true);
    setError("");
    try {
      const params = onlyCompleted ? "?completed=1" : "";
      const data = await api(`/api/results${params}`, {
        headers: { "X-Researcher-Key": nextKey },
      });
      sessionStorage.setItem(STORE, nextKey);
      setReport(data);
      setAuthed(true);
    } catch (err) {
      setReport(null);
      setAuthed(false);
      sessionStorage.removeItem(STORE);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const saved = sessionStorage.getItem(STORE);
    if (saved) {
      setKey(saved);
      load(saved, false);
    }
    // The saved key is loaded once when the page opens.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function unlock(event) {
    event.preventDefault();
    load(key.trim(), completedOnly);
  }

  function toggleCompleted(event) {
    const next = event.target.checked;
    setCompletedOnly(next);
    if (authed) load(key.trim(), next);
  }

  async function downloadCsv() {
    setError("");
    try {
      const params = completedOnly ? "?completed=1" : "";
      const response = await fetch(`/api/results.csv${params}`, {
        headers: { "X-Researcher-Key": key.trim() },
      });
      if (!response.ok) {
        let message = "Could not download the CSV.";
        try {
          const data = await response.json();
          if (data.error) message = data.error;
        } catch {
          // Keep the fallback message.
        }
        throw new Error(message);
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "campus-cart-results.csv";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  }

  const sponsored = report?.conditions?.sponsored;
  const unlabeled = report?.conditions?.unlabeled;
  const spendMax = Math.max(sponsored?.avg_spend || 0, unlabeled?.avg_spend || 0, 1);
  const targetSpendMax = Math.max(
    sponsored?.avg_target_spend || 0,
    unlabeled?.avg_target_spend || 0,
    1,
  );

  return (
    <div className="page">
      <Chrome
        action={
          <Link className="texty" to="/">
            Back to the store
          </Link>
        }
      />
      <section className="panel researcher">
        <p className="eyebrow">Results</p>
        <h1>What people clicked and bought</h1>
        <p className="lede">
          The top-left item stays put. Half the aisles label it Sponsored and half do not.
          A positive difference means the label increased that outcome.
        </p>

        <form className="key-row" onSubmit={unlock}>
          <label htmlFor="researcher-key">
            Researcher key
            <input
              id="researcher-key"
              value={key}
              autoComplete="off"
              onChange={(event) => setKey(event.target.value)}
            />
          </label>
          <button className="primary" type="submit" disabled={!key.trim() || loading}>
            {loading ? "Loading…" : "Show results"}
          </button>
        </form>
        <p className="fine">The local default is campus-cart. Change RESEARCHER_KEY before sharing the server.</p>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
      </section>

      {report && (
        <>
          <section className="stat-grid">
            <article className="stat">
              <span>People started</span>
              <strong>{report.participants_started}</strong>
            </article>
            <article className="stat">
              <span>People finished</span>
              <strong>{report.participants_completed}</strong>
            </article>
            <article className="stat">
              <span>Aisles saved</span>
              <strong>{report.observations}</strong>
            </article>
            <article className="stat">
              <span>Label order A / B</span>
              <strong>
                {report.sequence_counts.A} / {report.sequence_counts.B}
              </strong>
            </article>
          </section>

          <section className="panel">
            <div className="section-head">
              <h2>Sponsored versus no label</h2>
              <label className="check">
                <input type="checkbox" checked={completedOnly} onChange={toggleCompleted} />
                Finished sessions only
              </label>
            </div>
            {report.observations === 0 ? (
              <p>No shopping rounds yet.</p>
            ) : (
              <>
                <Compare
                  title="Click share of the top-left item"
                  unlabeled={unlabeled.click_share}
                  sponsored={sponsored.click_share}
                  format={formatShare}
                  max={1}
                />
                <Compare
                  title="Purchase share of the top-left item"
                  unlabeled={unlabeled.purchase_share}
                  sponsored={sponsored.purchase_share}
                  format={formatShare}
                  max={1}
                />
                <Compare
                  title="Average basket spend"
                  unlabeled={unlabeled.avg_spend}
                  sponsored={sponsored.avg_spend}
                  format={money}
                  max={spendMax}
                />
                <Compare
                  title="Average spend on the top-left item"
                  unlabeled={unlabeled.avg_target_spend}
                  sponsored={sponsored.avg_target_spend}
                  format={money}
                  max={targetSpendMax}
                />
                <p className="fine">
                  No label n = {unlabeled.n}. Sponsored n = {sponsored.n}. Unfinished
                  sessions are included unless the box above is checked.
                </p>
              </>
            )}
          </section>

          <section className="panel">
            <h2>Participant bootstrap</h2>
            <p>
              Rounds from the same person stay together. Each redraw picks people, not
              individual aisles.
            </p>
            <Effect title="Click share, sponsored minus unlabeled" effect={report.bootstrap.clicked_target} format={formatPoints} />
            <Effect title="Purchase share, sponsored minus unlabeled" effect={report.bootstrap.purchased_target} format={formatPoints} />
            <Effect title="Basket spend, sponsored minus unlabeled" effect={report.bootstrap.spend} format={signedMoney} />
            <p className="formula">
              purchased_target ~ sponsored_label + price + round_num + cognitive_state
            </p>
            <p className="fine">
              Cluster standard errors by participant_id. Those columns are in the CSV.
              sponsored_label is 1 when the top-left item says Sponsored.
            </p>
            <button type="button" className="ghost" onClick={downloadCsv}>
              Download CSV
            </button>
          </section>

          <section className="panel">
            <h2>Aisle rows</h2>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Person</th>
                    <th>Code</th>
                    <th>Aisle</th>
                    <th>Category</th>
                    <th>Label</th>
                    <th>Price</th>
                    <th>Clicked</th>
                    <th>Bought</th>
                    <th>Spend</th>
                    <th>Focus</th>
                  </tr>
                </thead>
                <tbody>
                  {report.rows.map((row) => (
                    <tr key={`${row.participant_id}-${row.round_num}`}>
                      <td title={row.participant_id}>{row.participant_id.slice(0, 8)}</td>
                      <td>{row.participant_code || "—"}</td>
                      <td>{row.round_num}</td>
                      <td>{row.category}</td>
                      <td>{row.sponsored_label ? "Sponsored" : "No label"}</td>
                      <td>{money(row.price)}</td>
                      <td>{row.clicked_target ? "Yes" : "No"}</td>
                      <td>{row.purchased_target ? "Yes" : "No"}</td>
                      <td>{money(row.spend)}</td>
                      <td>{row.cognitive_state}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
