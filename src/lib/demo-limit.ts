const WINDOW = 10 * 60 * 1000;
const buckets = new Map<string, { count: number; until: number }>();
function hit(key: string, max: number) {
  const now = Date.now();
  if (buckets.size > 2000) {
    for (const [k, v] of buckets) if (v.until < now) buckets.delete(k);
    if (buckets.size > 2000) return false;
  }
  let value = buckets.get(key);
  if (!value || value.until < now) {
    value = { count: 0, until: now + WINDOW };
    buckets.set(key, value);
  }
  return ++value.count <= max;
}
export function allowLogin(request: Request) {
  const ip = request.headers.get("x-real-ip") ?? "local";
  const global = hit("global", 150);
  const individual = hit("ip:" + ip, 10);
  return global && individual;
}
