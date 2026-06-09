import { useRef } from "react";
import Panel from './Panel';

const LINEAR_SPEED = 1.4;
const ANGULAR_SPEED = 1.4;

export default function ControlsPanel({
  moveRobot,
  sendArmPose,
}) {
  const startMove = (linear, angular) => {
    // avoid multiple intervals stacking
    if (intervalRef.current) return;

    intervalRef.current = setInterval(() => {
      moveRobot(linear, angular);
    }, 50); // 20 Hz
  };

  const stopMove = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    moveRobot(0, 0);
  };

  const holdEvents = (linear, angular) => ({
    onMouseDown: () => startMove(linear, angular),
    onMouseUp: stopMove,
    onMouseLeave: stopMove,
    onTouchStart: () => startMove(linear, angular),
    onTouchEnd: stopMove,
  });

  const intervalRef = useRef(null);

  return (
    <Panel title="Controls">
      <div className="controlsGrid">
        <button
          className="controlButton"
          {...holdEvents(
            LINEAR_SPEED, 0
          )}
        >
          ↑
        </button>

        <div className="middleRow">
          <button
            className="controlButton"
            {...holdEvents(
              0, ANGULAR_SPEED
            )}
          >
            ←
          </button>

          <button
            className="controlButton stop"
            onClick={() =>
              moveRobot(0, 0)
            }
          >
            ■
          </button>


          <button
            className="controlButton"
            {...holdEvents(
              0, -ANGULAR_SPEED
            )}
          >
            →
          </button>
        </div>

        <button
          className="controlButton"
          {...holdEvents(
            -LINEAR_SPEED, 0
          )}
        >
          ↓
        </button>
      </div>

      <div className="armControls">
        <h4>Arm Presets</h4>

        <button
          className="controlButton"
          onClick={() =>
            sendArmPose([0, 0, 0, -1])
          }
        >
          Up
        </button>

        <button
          className="controlButton"
          onClick={() =>
            sendArmPose([0, 0, -1, 0])
          }
        >
          Low
        </button>
      </div>
    </Panel>
  );
}
