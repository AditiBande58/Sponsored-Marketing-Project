import { Link } from "react-router-dom";

export default function Chrome({ action, showResearcher = false }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Study store</p>
        <p className="wordmark">Campus Cart</p>
      </div>
      {action}
      {showResearcher && (
        <Link className="texty" to="/researcher">
          Researcher
        </Link>
      )}
    </header>
  );
}
