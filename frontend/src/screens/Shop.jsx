import { useEffect, useRef, useState } from "react";
import { money } from "../api";
import Chrome from "../Chrome";
import LeaveRun from "../LeaveRun";
import Ticks from "../Ticks";

function toCents(value) {
  return Math.round(Number(value) * 100);
}

function readDraft(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function bootState(key, products) {
  const valid = new Set(products.map((product) => product.id));
  const draft = readDraft(key);
  const keep = (id) => valid.has(id);
  return {
    clickedIds: Array.isArray(draft?.clickedIds) ? draft.clickedIds.filter(keep) : [],
    cartIds: Array.isArray(draft?.cartIds) ? draft.cartIds.filter(keep) : [],
    clickLog: Array.isArray(draft?.clickLog)
      ? draft.clickLog.filter((entry) => entry && keep(entry.id))
      : [],
    startedAt: typeof draft?.startedAt === "number" ? draft.startedAt : Date.now(),
  };
}

function ProductDialog({ product, remainingCents, inCart, onAdd, onRemove, onClose }) {
  const dialogRef = useRef(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;
  const overBudget = !inCart && toCents(product.price) > remainingCents;

  useEffect(() => {
    const dialog = dialogRef.current;
    const previouslyFocused = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialog?.focus();

    function onKey(event) {
      if (event.key === "Escape") {
        onCloseRef.current();
        return;
      }
      if (event.key !== "Tab" || !dialog) return;
      const items = [...dialog.querySelectorAll("button")].filter((item) => !item.disabled);
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
      if (previouslyFocused instanceof HTMLElement) previouslyFocused.focus();
    };
  }, []);

  return (
    <div className="backdrop" onMouseDown={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="product-title"
        tabIndex={-1}
        ref={dialogRef}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <span className="photo">
          <img className="thumb modal-thumb" src={product.image} alt="" />
          {product.sponsored && <span className="sponsored-tag">Sponsored</span>}
        </span>
        <h2 id="product-title">{product.name}</h2>
        <p className="unit">{product.unit}</p>
        <p className="price">{money(product.price)}</p>
        <p>{product.detail}</p>
        <div className="modal-actions">
          {inCart ? (
            <button type="button" className="primary" onClick={() => onRemove(product.id)}>
              Remove from cart
            </button>
          ) : (
            <button type="button" className="primary" disabled={overBudget} onClick={() => onAdd(product)}>
              {overBudget ? "Over budget" : "Add to cart"}
            </button>
          )}
          <button type="button" className="ghost" onClick={onClose}>
            Close
          </button>
        </div>
        {overBudget && <p className="fine">Take something out if you still want this.</p>}
      </div>
    </div>
  );
}

export default function Shop({ session, onComplete, onAbandon }) {
  const round = session.round;
  const draftKey = `campus-cart-draft:${session.participant_id}:${round.round_num}`;
  const [boot] = useState(() => bootState(draftKey, round.products));
  const [clickedIds, setClickedIds] = useState(boot.clickedIds);
  const [cartIds, setCartIds] = useState(boot.cartIds);
  const [clickLog, setClickLog] = useState(boot.clickLog);
  const [startedAt] = useState(boot.startedAt);
  const [active, setActive] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const byId = Object.fromEntries(round.products.map((product) => [product.id, product]));
  const cart = cartIds.map((id) => byId[id]).filter(Boolean);
  const spendCents = cart.reduce((sum, item) => sum + toCents(item.price), 0);
  const budgetCents = toCents(round.budget);
  const remainingCents = budgetCents - spendCents;

  useEffect(() => {
    localStorage.setItem(
      draftKey,
      JSON.stringify({ clickedIds, cartIds, clickLog, startedAt }),
    );
  }, [draftKey, clickedIds, cartIds, clickLog, startedAt]);

  function openProduct(product) {
    setActive(product);
    setClickedIds((current) => (current.includes(product.id) ? current : [...current, product.id]));
    setClickLog((current) => [...current, { id: product.id, at_ms: Date.now() - startedAt }]);
  }

  function addProduct(product) {
    if (toCents(product.price) > remainingCents) return;
    setCartIds((current) => (current.includes(product.id) ? current : [...current, product.id]));
    setConfirming(false);
    setError("");
    setActive(null);
  }

  function removeProduct(id) {
    setCartIds((current) => current.filter((item) => item !== id));
    setConfirming(false);
    setError("");
    setActive(null);
  }

  async function checkout() {
    if (!cartIds.length) {
      setError("Add at least one item before checking out.");
      setConfirming(false);
      return;
    }
    if (!confirming) {
      setConfirming(true);
      setError("");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await onComplete({
        clicked_ids: clickedIds,
        purchased_ids: cartIds,
        click_log: clickLog,
        duration_ms: Date.now() - startedAt,
      });
      localStorage.removeItem(draftKey);
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
      setConfirming(false);
    }
  }

  const checkoutLabel = submitting ? "Checking out…" : confirming ? "Confirm checkout" : "Check out";

  return (
    <section className="shop" style={{ "--aisle": round.accent }}>
      <Chrome
        action={
          <p className="aisle-count">
            Aisle {round.round_num} of {session.total_rounds}
          </p>
        }
      />
      <div className="shop-head">
        <div>
          <h1>{round.title}</h1>
          <p className="lede">{round.blurb}</p>
        </div>
        <LeaveRun onAbandon={onAbandon} />
      </div>
      <Ticks current={round.round_num} total={session.total_rounds} />
      <div className="budget-line">
        <span>{money(remainingCents / 100)} left</span>
        <span>
          {money(spendCents / 100)} of {money(round.budget)}
        </span>
      </div>
      <div className="meter" aria-hidden="true">
        <div
          className="meter-fill"
          style={{ width: `${Math.min(100, (spendCents / budgetCents) * 100)}%` }}
        />
      </div>
      <p className="fine">Click an item to inspect it. Check out when the bag looks right.</p>

      <div className="shop-layout">
        <div className="product-grid">
          {round.products.map((product) => {
            const inCart = cartIds.includes(product.id);
            return (
              <button
                key={product.id}
                type="button"
                className={inCart ? "card in-cart" : "card"}
                onClick={() => openProduct(product)}
              >
                <span className="photo">
                  <img className="thumb" src={product.image} alt="" />
                  {product.sponsored && <span className="sponsored-tag">Sponsored</span>}
                </span>
                <span className="name">{product.name}</span>
                <span className="unit">{product.unit}</span>
                <span className="price">{money(product.price)}</span>
                {inCart && <span className="in-cart-label">In your cart</span>}
              </button>
            );
          })}
        </div>

        <aside className="cart">
          <h2>Your cart</h2>
          {cart.length === 0 ? (
            <p className="fine">Nothing bagged yet.</p>
          ) : (
            <ul className="cart-items">
              {cart.map((item) => (
                <li key={item.id} className="cart-row">
                  <span>
                    {item.name}
                    <small>{money(item.price)}</small>
                  </span>
                  <button type="button" className="texty" onClick={() => removeProduct(item.id)}>
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}
          <div className="totals">
            <span>Total</span>
            <strong>{money(spendCents / 100)}</strong>
          </div>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <button className="primary checkout-btn" type="button" onClick={checkout} disabled={submitting}>
            {checkoutLabel}
          </button>
          <p className="fine">Play money. Nothing is charged. Checkout locks this aisle.</p>
        </aside>
      </div>

      <div className="mobile-bar">
        <span>
          {cart.length} {cart.length === 1 ? "item" : "items"} · {money(spendCents / 100)}
        </span>
        <button className="primary" type="button" onClick={checkout} disabled={submitting}>
          {checkoutLabel}
        </button>
      </div>

      {active && (
        <ProductDialog
          product={active}
          remainingCents={remainingCents}
          inCart={cartIds.includes(active.id)}
          onAdd={addProduct}
          onRemove={removeProduct}
          onClose={() => setActive(null)}
        />
      )}
    </section>
  );
}
