import Panel from './Panel';

export default function ClickedPointPanel({
  clickedPoint,
}) {
  return (
    <Panel title="Selected Point">
      {clickedPoint ? (
        <>
          <div className="statusRow">
            <span>X</span>
            <span>
              {clickedPoint.x.toFixed(2)}
            </span>
          </div>

          <div className="statusRow">
            <span>Y</span>
            <span>
              {clickedPoint.y.toFixed(2)}
            </span>
          </div>
        </>
      ) : (
        <p>Click anywhere on the map</p>
      )}
    </Panel>
  );
}
