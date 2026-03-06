const BASE = "http://localhost:8080";

async function request(path, opts = {}) {

  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(opts.headers || {})
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

export const analysisApi = {

  analyze: (code, language) =>

    request("/api/analyze", {
      method: "POST",
      body: JSON.stringify({
        code,
        language
      })
    })

};