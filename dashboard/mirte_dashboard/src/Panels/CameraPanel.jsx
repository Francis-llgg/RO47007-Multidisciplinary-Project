import Panel from './Panel';

export default function CameraPanel({
  cameraImage,
  latestObservation,
}) {
  const flowerData = latestObservation?.metadata.flower_lengths;
  const greenhouseData = latestObservation?.metadata.greenhouse_reading;

  const units = {
    temperature: '°C',
    humidity: '%',
    soil_moisture: '',
  };

  return (
    <Panel title="Latest Snapshot">
      {cameraImage ? (
        <>
          <img
            src={cameraImage}
            alt="Snapshot"
            className="snapshot-image"
          />

          <div className="snapshot-metadata">
            {flowerData && (
              <div className="metadata-section">
                <h4>Flowers</h4>

                <p>
                  Detected: <strong>{flowerData.flower_count}</strong>
                </p>

                {flowerData.flowers?.map((flower) => (
                  <div
                    key={flower.id}
                    className="flower-card"
                  >
                    <div>
                      <strong>{flower.class_id}</strong>
                    </div>

                    <div>
                      Length:{' '}
                      {flower.estimated_length_cm.toFixed(1)} cm
                    </div>

                    <div>
                      Confidence:{' '}
                      {(flower.score * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            )}

            {greenhouseData && (
              <div className="metadata-section">
                <h4>Greenhouse Reading</h4>

                <p>
                  Tag ID: <strong>{greenhouseData.tag_id}</strong>
                </p>

                {greenhouseData.readings?.map((reading) => (
                  <div key={reading.name}>
                    <strong>{reading.name}:</strong>{' '}
                    {typeof reading.value === 'number'
                      ? reading.value.toFixed(1)
                      : reading.value}
                    {units[reading.name]
                      ? ` ${units[reading.name]}`
                      : ''}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : (
        <p>No snapshot received</p>
      )}
    </Panel>
  );
}
