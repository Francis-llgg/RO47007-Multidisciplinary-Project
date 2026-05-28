import Panel from './Panel';

export default function RobotStatusPanel({
  connected,
  robotPos,
}) {
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
        <span>X</span>
        <span>{robotPos.x.toFixed(2)}</span>
      </div>

      <div className="statusRow">
        <span>Y</span>
        <span>{robotPos.y.toFixed(2)}</span>
      </div>

      <div className="statusRow">
        <span>Yaw</span>
        <span>
          {((robotPos.yaw * 180) / Math.PI).toFixed(1)}°
        </span>
      </div>

      <div className="statusRow">
        <span>Battery</span>
        <span>--%</span>
      </div>
    </Panel>
  );
}
