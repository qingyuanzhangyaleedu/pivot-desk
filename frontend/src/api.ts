export interface Fact {
  id: string;
  kind: "experience" | "education" | "skill" | "language";
  title: string;
  organization: string;
  start: string;
  end: string;
  description: string;
  evidence_quote: string;
}
export interface Profile {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  facts: Fact[];
  confirmed: boolean;
  demo: boolean;
  warnings: string[];
  veteran_status: string | null;
  work_authorization: string | null;
}
export interface Prefs {
  query: string;
  regions: string[];
  industries: string[];
  exclude: string[];
  job_type: string;
  remote_ok: boolean;
  minimum_salary: number;
}
export interface Job {
  id: string;
  title: string;
  company: string;
  industry: string;
  location: string;
  description: string;
  url: string;
  source: string;
  retrieved_at: string;
  updated_at: string | null;
  job_type: string;
  salary_min: number | null;
  salary_max: number | null;
  score: number | null;
  breakdown: Record<string, number>;
  evidence: { fact_id: string; title: string; terms: string[] }[];
  matched_terms: string[];
  label: string;
}
export interface Run {
  run_id: string;
  kind: string;
  status: string;
  result: any;
  error: string | null;
  events: {
    id: number;
    agent: string;
    action: string;
    summary: string;
    created: string;
  }[];
  usage: {
    input_tokens: number;
    cached_tokens: number;
    output_tokens: number;
    requests: number;
    cost: number;
  } | null;
}
export async function api<T = any>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  const r = await fetch("/api" + url, {
    ...options,
    credentials: "include",
    headers:
      options.body instanceof FormData
        ? options.headers
        : { "Content-Type": "application/json", ...options.headers },
  });
  const data = await r.json();
  if (!r.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail || data),
    );
  return data;
}
export function download(value: unknown, name: string) {
  const a = document.createElement("a");
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }),
  );
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
