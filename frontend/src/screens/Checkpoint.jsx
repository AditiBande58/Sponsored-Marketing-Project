import { money } from "../api";
import Chrome from "../Chrome";
import LeaveRun from "../LeaveRun";
import Ticks from "../Ticks";

export default function Checkpoint({
  receipt,
  nextRound,
  nextTitle,
  nextBlurb,
  nextBudget,
  totalRounds,
  onContinue,
  onAbandon,
}) {
  return (
    <>
      <Chrome action={<p className="aisle-count">Aisle {nextRound} of {totalRounds}</p>} />
      <div className="checkpoint">
        <article className="receipt">
          <p className="eyebrow">Receipt</p>
          <h1>{receipt.title}</h1>
          <Ticks current={nextRound} total={totalRounds} />
          <ul className="cart-items">
            {receipt.items.map((item) => (
              <li key={item.id} className="receipt-line">
                <span>{item.name}</span>
                <span>{money(item.price)}</span>
              </li>
            ))}
          </ul>
          <div className="totals">
            <span>Spent</span>
            <strong>
              {money(receipt.spend)} of {money(receipt.budget)}
            </strong>
          </div>
          <p className="fine">Paid with play money.</p>
        </article>

        <section className="panel next-aisle">
          <p className="eyebrow">Next aisle</p>
          <h2>{nextTitle}</h2>
          <p>{nextBlurb}</p>
          <p className="budget-callout">Budget {money(nextBudget)}</p>
          <button type="button" className="primary" onClick={onContinue}>
            Continue
          </button>
          <LeaveRun onAbandon={onAbandon} />
        </section>
      </div>
    </>
  );
}
