import Panel from './Panel';

export default function CameraPanel({
  cameraImage,
  latestObservation,
}) {
  return (
    <Panel title="Latest Snapshot">
      {cameraImage ? (
        <>
          <img
            src={cameraImage}
            alt="Snapshot"
            style={{
              width: '100%',
              height: 'auto',
            }}
          />

          {latestObservation?.metadata && (
            <div style={{ marginTop: '1rem' }}>
              <h4>Metadata</h4>

              <div>
                <strong>Flower Lengths</strong>
                <pre>
                  {JSON.stringify(
                    latestObservation.metadata.flower_lengths,
                    null,
                    2
                   )}
                </pre>
              </div>

              <div>
                <strong>Greenhouse Reading</strong>
                <pre>
                  {JSON.stringify(
                    latestObservation.metadata.greenhouse_reading,
                    null,
                    2
                  )}
                 </pre>
              </div>
            </div>
          )}
        </>
      ) : (
        <p>No image received</p>
      )}
    </Panel>
  );
}
