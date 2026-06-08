import Panel from './Panel';

export default function CameraPanel({
  liveCamera,
}) {
  return (
    <Panel title="Gripper Camera">
      {liveCamera ? (
        <img
          src={liveCamera}
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
