/** Unwrap FastAPI ``APIResponse`` `{ data, meta, ai_context? }` for client fetch handlers. */

export function unwrapApiData<T>(json: unknown): T {
  if (
    json &&
    typeof json === "object" &&
    Object.prototype.hasOwnProperty.call(json, "data") &&
    Object.prototype.hasOwnProperty.call(json, "meta")
  ) {
    return (json as { data: T }).data;
  }
  return json as T;
}
