import { useMemo } from 'react';
import { Stage, Layer, Image, Line, Rect, Circle, } from 'react-konva';
import useImage from 'use-image';
import { worldToPixel, pixelToWorld, } from '../utils/mapUtils';

const MAP_SCALE = 3;
const LINE_LENGTH = 25;

export default function MapPanel({
  map,
  robotPos,
  clickedPoint,
  onMapClick,
}) {
  const mapCanvas = useMemo(() => {
    if (!map) return null;

    const width = map.info.width;
    const height = map.info.height;

    const canvas =
      document.createElement('canvas');

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    const imageData =
      ctx.createImageData(width, height);

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const srcIndex = x + (height - y - 1) * width;
        const value = map.data[srcIndex];
        const color = value === -1 ? 180 : 255 - (value / 100) * 255;
        const idx = (y * width + x) * 4;

        imageData.data[idx] = color;
        imageData.data[idx + 1] = color;
        imageData.data[idx + 2] = color;
        imageData.data[idx + 3] = 255;
      }
    }

    ctx.putImageData(
      imageData, 0, 0
    );

    return canvas.toDataURL();
  }, [map]);

  const [mapImage] = useImage(
    mapCanvas || ''
  );

  const robotPixel = worldToPixel(
    map, robotPos.x, robotPos.y
  );

  const clickedPixel = clickedPoint
    ? worldToPixel(
        map,
        clickedPoint.x,
        clickedPoint.y
      )
    : null;

  if (!map) {
    return (
      <div className="mapLoading">
        Waiting for map...
      </div>
    );
  }

  return (
    <div className="mapWrapper">
      <Stage
        width={map.info.width * MAP_SCALE}
        height={map.info.height * MAP_SCALE}
        draggable
        onClick={(e) => {
          const pos = e.target .getStage() .getPointerPosition();
          const world = pixelToWorld(map, pos.x / MAP_SCALE, pos.y / MAP_SCALE );
          onMapClick(world);
        }}
      >
        <Layer>
          <Image
            image={mapImage}
            width={map.info.width * MAP_SCALE}
            height={map.info.height * MAP_SCALE}
          />
          {clickedPixel && (
            <Circle
              x={clickedPixel.x * MAP_SCALE}
              y={clickedPixel.y * MAP_SCALE}
              radius={5}
              fill="red"
            />
          )}
        </Layer>

        <Layer>
          <Rect
            x={robotPixel.x * MAP_SCALE}
            y={robotPixel.y * MAP_SCALE}
            width={30}
            height={20}
            offsetX={15}
            offsetY={10}
            rotation={-(robotPos.yaw * 180) / Math.PI}
            fill="dodgerblue"
            />

          <Line
            points={[
              robotPixel.x * MAP_SCALE,
              robotPixel.y * MAP_SCALE,
              robotPixel.x * MAP_SCALE + Math.cos(robotPos.yaw) * LINE_LENGTH,
              robotPixel.y * MAP_SCALE - Math.sin(robotPos.yaw) * LINE_LENGTH,
            ]}
            stroke="dodgerblue"
            strokeWidth={5}
          />
        </Layer>
      </Stage>
    </div>
  );
}
