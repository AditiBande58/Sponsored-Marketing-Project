import { useState } from "react";
import { Link } from "react-router-dom";
import { money } from "../api";
import Chrome from "../Chrome";

export default function Debrief({ session, onAgain }) {
  const [copied, setCopied] = useState(false);
  const summary = session.summary || { rounds: 0, items: 0, total_spend: 0 };

  async function copyId() {
    try {
      await navigator.clipboard.writeText(session.participant_id);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <>
      <Chrome showResearcher />
      <div className="debrief">
        <section className="panel">
          <p className="eyebrow">Finished</p>
          <h1>Thanks for shopping.</h1>
          <p className="lede">
            You checked out of {summary.rounds} aisles, bagged {summary.items} items, and
            spent {money(summary.total_spend)} in play money.
          </p>
          <p>
            The same kind of mid-priced item sat in the first spot every aisle — top-left
            on a wide screen, where people tend to look first. On half the aisles that
            item said Sponsored. On half it did not. From person to person, that label
            order was flipped, so it was not always on the early aisles.
          </p>
          <p>
            What we save is whether you clicked that item, whether you bought it, and how
            much of the budget you spent. The focus rating from the start is saved too.
            The comparison resamples people, not single aisles, because your ten rounds
            belong together.
          </p>
          <div className="id-row">
            <code>{session.participant_id}</code>
            <button type="button" className="ghost" onClick={copyId}>
              {copied ? "Copied" : "Copy ID"}
            </button>
          </div>
          {session.participant_code && (
            <p className="fine">Recorded under {session.participant_code}.</p>
          )}
          <div className="modal-actions">
            <button type="button" className="primary" onClick={onAgain}>
              Start a new session
            </button>
            <Link className="ghost link-button" to="/researcher">
              Researcher view
            </Link>
          </div>
        </section>

        {session.aisles?.length > 0 && (
          <section className="panel">
            <h2>Your bags</h2>
            <ul className="aisle-list">
              {session.aisles.map((aisle) => (
                <li key={aisle.round_num}>
                  <div>
                    <strong>{aisle.title}</strong>
                    <span>{aisle.items.join(", ")}</span>
                  </div>
                  <span>{money(aisle.spend)}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </>
  );
}
