import { useState } from "react";
import Panel from './Panel';

export default function RobotStatusPanel({
  connected,
  robotPos,
  battery,
}) {
  const [r, setR] = useState(0);
  const [g, setG] = useState(0);
  const [b, setB] = useState(0);

  return (
    <Panel title="Robot Status">
      <div className="statusRow">
        <span>Status</span>
        <span>
          {connected
            ? '🟢 Connected'
            : '🔴 Offline'}
        </span>
      </div>

      <div className="statusRow">
        <span>Battery</span>
        <span>{battery.percentage.toFixed(2)}%</span>
      </div>
    </Panel>
  );
}
