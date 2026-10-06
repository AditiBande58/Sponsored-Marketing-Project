import { useState } from "react";

export default function LeaveRun({ onAbandon }) {
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button type="button" className="texty" onClick={() => setOpen(true)}>
        Leave this run
      </button>
    );
  }

  return (
    <span className="leave">
      Abandon this run and start over?
      <button type="button" className="texty" onClick={onAbandon}>
        Yes, start over
      </button>
      <button type="button" className="texty" onClick={() => setOpen(false)}>
        Keep shopping
      </button>
    </span>
  );
}
