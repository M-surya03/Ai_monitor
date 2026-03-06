const BASE = "http://localhost:8080";

async function request(path, opts = {}) {

  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json"
    }
  });

  const text = await res.text();

  let data;

  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }

  if (!res.ok) {
    throw new Error(data?.message || data || `HTTP ${res.status}`);
  }

  return data;
}

export const progressApi = {

  getProgress: () => request(`/api/dashboard`)

};