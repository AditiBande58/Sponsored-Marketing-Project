export default function Ticks({ current, total }) {
  return (
    <div className="ticks" aria-hidden="true">
      {Array.from({ length: total }, (_, index) => {
        let state = "";
        if (index < current - 1) state = "done";
        else if (index === current - 1) state = "now";
        return <span key={index} className={`tick ${state}`} />;
      })}
    </div>
  );
}
