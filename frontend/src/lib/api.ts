const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return res.json();
}

export type Neighborhood = {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
};

export type ModelMetrics = {
  model: string;
  mae: number;
  r2: number;
  n_samples: number;
};

export type PredictionRequest = {
  type: string;
  neighborhood_id: string;
  area: number;
  bedrooms: number;
  bathrooms: number;
  parking: number;
};

export type ImpactFactor = {
  label: string;
  value: number;
  weight: number;
};

export type PredictionResponse = {
  price: number;
  min: number;
  max: number;
  margin_pct: number;
  factors: ImpactFactor[];
};

export const api = {
  neighborhoods: () => get<Neighborhood[]>("/neighborhoods"),
  modelMetrics: () => get<ModelMetrics>("/model/metrics"),
  predict: (body: PredictionRequest) => post<PredictionResponse>("/predictions", body),
};
