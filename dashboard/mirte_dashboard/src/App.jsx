import { useState } from 'react';
import './App.css';

import useROS from './utils/useROS.js';
import MapPanel from './Panels/MapPanel.jsx';
import ControlsPanel from './Panels/ControlsPanel.jsx';
import RobotStatusPanel from './Panels/RobotStatusPanel.jsx';
import ClickedPointPanel from './Panels/ClickedPointPanel.jsx';
import CameraPanel from './Panels/CameraPanel.jsx';
import LiveCameraPanel from './Panels/LiveCameraPanel.jsx';

export default function App() {
  const {connected, map, robotPos, moveRobot, battery, cameraImage, latestObservation, liveCamera, sendArmPose, setInitialPose} = useROS();

  const [clickedPoint, setClickedPoint] = useState(null);

  return (
    <div className="app">
      <div className="mainLayout">
        <MapPanel
          map={map}
          robotPos={robotPos}
          clickedPoint={clickedPoint}
          setClickedPoint={setClickedPoint}
          setInitialPose={setInitialPose}
        />

        <div className="sidebar">
          <RobotStatusPanel
            connected={connected}
            robotPos={robotPos}
            battery={battery}
          />

          <LiveCameraPanel
            liveCamera={liveCamera}
          />

          <ClickedPointPanel
            clickedPoint={clickedPoint}
          />

          <CameraPanel
            cameraImage={cameraImage}
            latestObservation={latestObservation}
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
