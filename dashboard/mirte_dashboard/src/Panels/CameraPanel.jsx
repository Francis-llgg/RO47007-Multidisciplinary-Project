import Panel from './Panel';

export default function CameraPanel({
  cameraImage,
}) {
  return (
    <Panel title="Gripper Camera">
      {cameraImage ? (
        <img
          src={cameraImage}
          alt="Camera"
          style={{
            width: '100%',
            height: 'auto',
          }}
        />
      ) : (
        <p>No image received</p>
      )}
    </Panel>
  );
}
