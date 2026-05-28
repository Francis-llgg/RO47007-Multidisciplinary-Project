import { useState } from 'react';
import './App.css';

import useROS from './utils/useROS.js';
import MapPanel from './Panels/MapPanel.jsx';
import ControlsPanel from './Panels/ControlsPanel.jsx';
import RobotStatusPanel from './Panels/RobotStatusPanel.jsx';
import ClickedPointPanel from './Panels/ClickedPointPanel.jsx';

export default function App() {
  const {connected, map, robotPos, moveRobot, } = useROS();

  const [clickedPoint, setClickedPoint] = useState(null);

  return (
    <div className="app">
      <div className="mainLayout">
        <MapPanel
          map={map}
          robotPos={robotPos}
          clickedPoint={clickedPoint}
          onMapClick={setClickedPoint}
        />

        <div className="sidebar">
          <RobotStatusPanel
            connected={connected}
            robotPos={robotPos}
          />

          <ClickedPointPanel
            clickedPoint={clickedPoint}
          />

          <ControlsPanel
            moveRobot={moveRobot}
          />
        </div>
      </div>
    </div>
  );
}
