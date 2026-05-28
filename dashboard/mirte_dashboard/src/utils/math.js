export function quaternionToYaw(q) {
  const siny = 2 * (q.w * q.z + q.x * q.y);
  const cosy = 1 - 2 * (q.y * q.y + q.z * q.z);

  return Math.atan2(siny, cosy);
}
