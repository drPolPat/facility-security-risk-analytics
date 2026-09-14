const BASE = import.meta.env.VITE_API_BASE_URL || "";

function formatDetail(body) {
  if (!body?.detail) return null;
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    // FastAPI/Pydantic 422 shape: [{loc: [...], msg: "..."}, ...]
    return body.detail
      .map((d) => `${(d.loc ?? []).slice(-1)[0] ?? "value"}: ${d.msg}`)
      .join("; ");
  }
  return JSON.stringify(body.detail);
}

async function handle(res) {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      detail = formatDetail(await res.json()) ?? detail;
    } catch {
      /* keep the status text */
    }
    throw new Error(detail);
  }
  return res.json();
}

function getJSON(path) {
  return fetch(`${BASE}${path}`).then(handle);
}

function postJSON(path, payload) {
  return fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(handle);
}

export function getFacilities(archetype) {
  const params = new URLSearchParams();
  if (archetype) params.set("archetype", archetype);
  const qs = params.toString();
  return getJSON(`/api/facilities${qs ? `?${qs}` : ""}`);
}

export function getFacility(id) {
  return getJSON(`/api/facilities/${encodeURIComponent(id)}`);
}

export function whatIf(id, { factors = {}, flags = {} } = {}) {
  return postJSON(`/api/facilities/${encodeURIComponent(id)}/what-if`, { factors, flags });
}

export function getShapSummary() {
  return getJSON("/api/shap-summary");
}
