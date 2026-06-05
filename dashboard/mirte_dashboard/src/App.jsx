import { useState } from 'react';
import './App.css';

import useROS from './utils/useROS.js';
import MapPanel from './Panels/MapPanel.jsx';
import ControlsPanel from './Panels/ControlsPanel.jsx';
import RobotStatusPanel from './Panels/RobotStatusPanel.jsx';
import ClickedPointPanel from './Panels/ClickedPointPanel.jsx';
import CameraPanel from './Panels/CameraPanel.jsx';

export default function App() {
  const {connected, map, robotPos, moveRobot, battery, cameraImage, sendArmPose} = useROS();

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
            battery={battery}
          />

          <ClickedPointPanel
            clickedPoint={clickedPoint}
          />

          <CameraPanel
            cameraImage={cameraImage}
          />

          <ControlsPanel
            moveRobot={moveRobot}
            sendArmPose={sendArmPose}
          />
        </div>
      </div>
    </div>
  );
}
