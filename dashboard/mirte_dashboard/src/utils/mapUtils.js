export function worldToPixel(map, x, y) {
  if (!map) return { x: 0, y: 0 };

  const resolution = map.info.resolution;
  const origin = map.info.origin.position;
  const mapHeight = map.info.height;

  return {
    x: (x - origin.x) / resolution,
    y: mapHeight - (y - origin.y) / resolution,
  };
}

export function pixelToWorld(map, px, py) {
  if (!map) return { x: 0, y: 0 };

  const resolution = map.info.resolution;
  const origin = map.info.origin.position;
  const mapHeight = map.info.height;

  return {
    x: px * resolution + origin.x,
    y: (mapHeight - py) * resolution + origin.y,
  };
}
