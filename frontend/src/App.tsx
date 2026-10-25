import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  ArrowRight,
  Search,
  SlidersHorizontal,
  BriefcaseBusiness,
  FileText,
  Layers,
  ShieldCheck,
  Activity,
  Upload,
  Check,
  Plus,
  RefreshCw,
  MapPin,
  Bookmark,
  Download,
  X,
  ChevronDown,
  Sparkles,
  CheckCircle2,
  Clock,
  ExternalLink,
  Trash2,
} from "lucide-react";
import {
  api,
  download,
  type Profile,
  type Prefs,
  type Job,
  type Run,
} from "./api";
const defaults: Prefs = {
  query: "strategy product operations",
  regions: ["West Coast"],
  industries: ["Healthcare", "Technology"],
  exclude: ["investment banking"],
  job_type: "any",
  remote_ok: true,
  minimum_salary: 0,
};
const money = (n: number) => "$" + n.toLocaleString();
const date = (s: string) =>
  new Date(s).toLocaleDateString("en-US", { month: "short", day: "numeric" });
const stages = [
  "Saved",
  "Preparing",
  "Applied",
  "Interview",
  "Offer",
  "Closed",
];
export default function App() {
  const [tab, setTab] = useState("discover"),
    [status, setStatus] = useState<any>(null),
    [profile, setProfile] = useState<Profile | null>(null),
    [prefs, setPrefs] = useState<Prefs>(defaults),
    [jobs, setJobs] = useState<Job[]>([]),
    [selected, setSelected] = useState<Job | null>(null),
    [searchInfo, setSearchInfo] = useState<any>(null),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState(""),
    [error, setError] = useState(""),
    [run, setRun] = useState<Run | null>(null),
    [runId, setRunId] = useState(""),
    [analysisJobId, setAnalysisJobId] = useState(""),
    [track, setTrack] = useState<any[]>([]),
    [metrics, setMetrics] = useState<any>(null),
    [consent, setConsent] = useState(false),
    [resumeText, setResumeText] = useState(""),
    [upload, setUpload] = useState<File | null>(null),
    [showImport, setShowImport] = useState(false),
    [importData, setImportData] = useState({
      title: "",
      company: "",
      location: "",
      industry: "Healthcare",
      url: "",
      description: "",
    });
  const working =
    !!runId && !["completed", "cached", "error"].includes(run?.status || "");
  async function boot() {
    try {
      const s = await api("/status");
      setStatus(s);
      setProfile(s.draft || s.profile);
      const p = s.preferences || defaults;
      setPrefs(p);
      await search(p, false);
      await refreshExtras();
    } catch (e) {
      setError(String(e));
    }
  }
  async function refreshExtras() {
    const [t, m] = await Promise.all([api("/tracker"), api("/metrics")]);
    setTrack(t);
    setMetrics(m);
  }
  useEffect(() => {
    void boot();
  }, []);
  useEffect(() => {
    if (!runId) return;
    let stop = false;
    const poll = async () => {
      try {
        const r = await api<Run>("/runs/" + runId);
        if (stop) return;
        setRun(r);
        if (["completed", "cached", "error"].includes(r.status)) {
          setRunId("");
          if (r.kind === "resume" && r.result) {
            setProfile(r.result);
            setTab("profile");
            setNotice(
              "Extraction ready. Check each fact, then save your reviewed profile.",
            );
          }
          if (r.error) setError(r.error);
          void refreshExtras();
        }
      } catch (e) {
        setError(String(e));
        setRunId("");
      }
    };
    void poll();
    const timer = setInterval(poll, 1000);
    return () => {
      stop = true;
      clearInterval(timer);
    };
  }, [runId]);
  async function search(p = prefs, refresh = false) {
    if (working) return;
    setBusy(true);
    setError("");
    try {
      const d = await api("/search", {
        method: "POST",
        body: JSON.stringify({ preferences: p, refresh }),
      });
      setJobs(d.jobs);
      setSearchInfo(d);
      setSelected(d.jobs[0] || null);
      setRun(null);
      if (refresh)
        setNotice(
          d.sources?.length
            ? "Employer refresh finished. Source failures, if any, are shown below."
            : d.message,
        );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function demo() {
    if (working) return;
    try {
      const p = await api<Profile>("/demo", { method: "POST" });
      setProfile(p);
      setNotice(
        "Fictional demo profile loaded. Upload your own resume to personalize the workspace.",
      );
      await search();
    } catch (e) {
      setError(String(e));
    }
  }
  async function extract() {
    if (!consent) {
      setError("Please confirm the AI processing checkbox first.");
      return;
    }
    if (!upload && !resumeText.trim()) {
      setError("Choose a resume file or paste its text.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const body = new FormData();
      body.append(
        "file",
        upload || new File([resumeText], "resume.txt", { type: "text/plain" }),
      );
      body.append("consent", "true");
      const r = await api("/resume", { method: "POST", body });
      setRun(null);
      setRunId(r.run_id);
      setNotice(
        "Reading your resume. You will review the extracted facts before saving.",
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function saveProfile() {
    if (working) return;
    if (!profile) return;
    setBusy(true);
    setError("");
    try {
      const p = await api<Profile>("/profile", {
        method: "PUT",
        body: JSON.stringify({ ...profile, confirmed: true }),
      });
      setProfile(p);
      setNotice("Reviewed profile saved in this browser workspace.");
      await search();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function analyze() {
    if (!selected) return;
    setAnalysisJobId(selected.id);
    setError("");
    try {
      const r = await api("/analyze", {
        method: "POST",
        body: JSON.stringify({
          job_id: selected.id,
          consent: true,
          compact: false,
        }),
      });
      setRun(null);
      setRunId(r.run_id);
    } catch (e) {
      setError(String(e));
    }
  }
  async function saveJob(j: Job, stage = "Saved", note = "", follow_up = "") {
    try {
      await api("/tracker", {
        method: "PUT",
        body: JSON.stringify({ job_id: j.id, stage, note, follow_up }),
      });
      await refreshExtras();
      setNotice("Saved to your pipeline. No application was sent.");
    } catch (e) {
      setError(String(e));
    }
  }
  async function packet() {
    try {
      download(await api("/packet"), "pivot-profile-private.json");
      setNotice(
        "Private profile packet exported. Only import it into the Pivot Desk extension.",
      );
    } catch (e) {
      setError(String(e));
    }
  }
  async function importJob() {
    if (working) return;
    try {
      const j = await api("/jobs/import", {
        method: "POST",
        body: JSON.stringify(importData),
      });
      setShowImport(false);
      setNotice(
        "Posting imported into your private workspace. It has not been live-verified.",
      );
      await search({
        ...prefs,
        query: "",
        regions: [],
        industries: [],
        exclude: [],
      });
      setSelected(j);
    } catch (e) {
      setError(String(e));
    }
  }
  const toggle = (key: "industries" | "regions", v: string) =>
    setPrefs({
      ...prefs,
      [key]: prefs[key].includes(v)
        ? prefs[key].filter((x) => x !== v)
        : [...prefs[key], v],
    });
  const Banner = () => (
    <>
      {error && (
        <div className="banner error" role="alert">
          <ShieldCheck size={18} />
          <span>{error}</span>
          <button aria-label="Dismiss error" onClick={() => setError("")}>
            <X size={16} />
          </button>
        </div>
      )}
      {notice && (
        <div className="banner" role="status">
          <CheckCircle2 size={18} />
          <span>{notice}</span>
          <button
            aria-label="Dismiss notification"
            onClick={() => setNotice("")}
          >
            <X size={16} />
          </button>
        </div>
      )}
    </>
  );
  const Feed = () =>
    run || working ? (
      <div className="run-panel">
        <div className="section-head">
          <span className="eyebrow">AGENT NOTEBOOK</span>
          <span className={"pill " + (working ? "pulse" : "")}>
            {working ? "Working" : run?.status}
          </span>
        </div>
        {run?.events.map((e) => (
          <div className="event" key={e.id}>
            <span className="event-dot" />
            <div>
              <strong>{e.agent}</strong>
              <p>{e.summary}</p>
            </div>
          </div>
        ))}
        {working && !run?.events.length && (
          <p className="shimmer">Connecting to the evidence reader…</p>
        )}
        {run?.usage && (
          <div className="usage-inline">
            {run.usage.input_tokens.toLocaleString()} input ·{" "}
            {run.usage.output_tokens.toLocaleString()} output tokens · $
            {run.usage.cost.toFixed(5)} estimated
          </div>
        )}
      </div>
    ) : null;
  return (
    <div className="shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setTab("discover");
          }}
        >
          <span className="brand-icon">
            p<span>↗</span>
          </span>
          <div>
            pivot desk<small>MAKE YOUR NEXT MOVE COUNT</small>
          </div>
        </a>
        <div className="sidebar-label">YOUR RECRUITING WORKSPACE</div>
        <nav>
          {[
            ["discover", Search, "Discover roles"],
            ["profile", FileText, "My evidence"],
            ["kit", Layers, "Application kit"],
            ["tracker", BriefcaseBusiness, "My pipeline"],
            ["evidence", Activity, "Usage & proof"],
          ].map(([id, Icon, label]: any) => (
            <button
              key={id}
              className={tab === id ? "active" : ""}
              onClick={() => setTab(id)}
            >
              <Icon size={19} />
              {label}
              {id === "tracker" && (
                <span className="nav-count">{track.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <Sparkles size={23} />
          <h3>
            A pivot is a story.
            <br />
            Back yours with facts.
          </h3>
          <p>Find the overlap. See the gaps. Keep every application yours.</p>
        </div>
        <div className="sidebar-bottom">
          <div className="avatar">
            {profile ? profile.full_name.slice(0, 1) : "Y"}
          </div>
          <div>
            <strong>{profile?.full_name || "Your workspace"}</strong>
            <span>
              {profile?.demo
                ? "Fictional demo profile"
                : profile
                  ? "Private · this browser"
                  : "Start with your resume"}
            </span>
          </div>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <span>
            THE RECRUITING DESK <span className="slash">/</span>{" "}
            {
              (
                {
                  discover: "Discovery",
                  profile: "Your evidence",
                  kit: "Application kit",
                  tracker: "Pipeline",
                  evidence: "Usage & proof",
                } as any
              )[tab]
            }
          </span>
          <div>
            <span className="status-dot" /> Local & private{" "}
            <span className="sep">·</span>
            <span>{status?.ai_available ? "AI configured" : "Demo ready"}</span>
          </div>
        </header>
        <div className="workspace">
          <Banner />
          {tab === "discover" && (
            <>
              <div className="page-heading">
                <div className="eyebrow">LESS SEARCHING. MORE INTENTION.</div>
                <div className="heading-row">
                  <h1>
                    Find your next <em>chapter.</em>
                  </h1>
                  <button
                    className="button secondary"
                    onClick={() => setTab("profile")}
                  >
                    <FileText size={17} />
                    {profile ? "Review resume" : "Add your resume"}
                    <ArrowUpRight size={17} />
                  </button>
                </div>
                <p>
                  Roles that fit where you want to go—with evidence from where
                  you’ve been.
                </p>
              </div>
              {!profile && (
                <div className="welcome">
                  <div>
                    <span className="tag">START HERE</span>
                    <h3>Turn your resume into your recruiting advantage.</h3>
                    <p>
                      Upload a PDF or DOCX, review the facts, then see how they
                      connect to real roles.
                    </p>
                  </div>
                  <div className="actions">
                    <button
                      className="button primary"
                      onClick={() => setTab("profile")}
                    >
                      Upload resume <ArrowRight size={17} />
                    </button>
                    <button className="text-button" onClick={demo}>
                      Explore a fictional demo ↗
                    </button>
                  </div>
                </div>
              )}
              {profile?.demo && (
                <div className="demo-bar">
                  DEMO PROFILE{" "}
                  <span>
                    Avery is fictional. Job listings come from real employer
                    sources.
                  </span>
                  <button onClick={() => setTab("profile")}>
                    Use my resume →
                  </button>
                </div>
              )}
              <div className="discovery-tools">
                <div className="searchbar">
                  <Search size={20} />
                  <input
                    aria-label="Role keywords"
                    value={prefs.query}
                    onChange={(e) =>
                      setPrefs({ ...prefs, query: e.target.value })
                    }
                    onKeyDown={(e) => e.key === "Enter" && search()}
                    placeholder="Strategy, product, operations…"
                  />
                  <button onClick={() => search()} disabled={busy}>
                    {busy ? "Searching…" : "Find roles"}
                    <ArrowRight size={16} />
                  </button>
                </div>
                <button
                  className="button secondary"
                  onClick={() => setShowImport(true)}
                >
                  <Plus size={17} /> Add a posting
                </button>
              </div>
              <div className="role-shortcuts" aria-label="MBA role shortcuts">
                <span>Try a role focus</span>
                {[
                  ["MBA roles", "mba"],
                  ["Consulting", "consultant associate"],
                  ["Corporate finance", "finance"],
                  ["Brand & growth", "marketing growth"],
                  ["Climate & energy", "energy sustainability"],
                ].map(([label, query]) => (
                  <button
                    key={label}
                    disabled={busy || working}
                    onClick={() => {
                      const next = { ...prefs, query };
                      setPrefs(next);
                      void search(next);
                    }}
                  >
                    {label}
                  </button>
                ))}
                <small>Uses your selected sectors and locations.</small>
              </div>
              <details className="filters" open>
                <summary>
                  <SlidersHorizontal size={16} />
                  Your search brief <ChevronDown size={16} />
                </summary>
                <div className="filter-content">
                  <div>
                    <label>LOCATION</label>
                    <div className="chips">
                      {["West Coast", "East Coast"].map((x) => (
                        <button
                          className={prefs.regions.includes(x) ? "chosen" : ""}
                          onClick={() => toggle("regions", x)}
                          key={x}
                        >
                          {prefs.regions.includes(x) && <Check size={13} />} {x}
                        </button>
                      ))}
                    </div>
                    <label className="check-label">
                      <input
                        type="checkbox"
                        checked={prefs.remote_ok}
                        onChange={(e) =>
                          setPrefs({ ...prefs, remote_ok: e.target.checked })
                        }
                      />{" "}
                      Include US-remote
                    </label>
                    <input
                      className="small-input"
                      aria-label="Additional location"
                      placeholder="Add a city; press Enter"
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && e.currentTarget.value) {
                          setPrefs({
                            ...prefs,
                            regions: [...prefs.regions, e.currentTarget.value],
                          });
                          e.currentTarget.value = "";
                        }
                      }}
                    />
                    {prefs.regions
                      .filter((x) => !["West Coast", "East Coast"].includes(x))
                      .map((x) => (
                        <button
                          className="mini-tag"
                          onClick={() => toggle("regions", x)}
                          key={x}
                        >
                          {x} ×
                        </button>
                      ))}
                  </div>
                  <div>
                    <label>COMPANY SECTOR</label>
                    <div className="chips">
                      {(status?.industries || defaults.industries).map(
                        (x: string) => (
                          <button
                            className={
                              prefs.industries.includes(x) ? "chosen" : ""
                            }
                            aria-pressed={prefs.industries.includes(x)}
                            onClick={() => toggle("industries", x)}
                            key={x}
                          >
                            {prefs.industries.includes(x) && (
                              <Check size={13} />
                            )}{" "}
                            {x}
                          </button>
                        ),
                      )}
                    </div>
                    <p className="sector-note">
                      More paths for MBA recruiting. These are employer sectors,
                      not a guarantee of MBA eligibility.
                    </p>
                    <label>OPPORTUNITY TYPE</label>
                    <select
                      aria-label="Opportunity type"
                      value={prefs.job_type}
                      onChange={(e) =>
                        setPrefs({ ...prefs, job_type: e.target.value })
                      }
                    >
                      <option value="any">
                        Internships + full-time + unknown
                      </option>
                      <option value="internship">Internships only</option>
                      <option value="full-time">Explicit full-time only</option>
                    </select>
                  </div>
                  <div>
                    <label>LEAVE OUT</label>
                    <input
                      aria-label="Excluded terms"
                      aria-describedby="exclusion-help"
                      value={prefs.exclude.join(", ")}
                      onChange={(e) =>
                        setPrefs({
                          ...prefs,
                          exclude: e.target.value
                            .split(",")
                            .map((x) => x.trim())
                            .filter(Boolean),
                        })
                      }
                    />
                    <p className="sector-note" id="exclusion-help">
                      Full posting also excludes mentions of past experience.
                      Choose title only to keep consulting roles that mention banking experience.
                    </p>
                    <select aria-label="Exclusion scope" value={prefs.exclude_scope || "full_posting"} onChange={e => setPrefs({...prefs, exclude_scope: e.target.value as "full_posting" | "title_only"})}>
                      <option value="full_posting">Exclude from full posting</option>
                      <option value="title_only">Exclude from role title only</option>
                    </select>
                    <label>MINIMUM PUBLISHED BASE PAY / YEAR</label>
                    <input
                      type="number"
                      aria-label="Minimum salary"
                      min="0"
                      max="1000000"
                      value={prefs.minimum_salary || ""}
                      placeholder="Any · unknown pay included"
                      onChange={(e) =>
                        setPrefs({
                          ...prefs,
                          minimum_salary: Number(e.target.value),
                        })
                      }
                    />
                  </div>
                </div>
              </details>
              <div className="results-head">
                <div>
                  <strong>{searchInfo?.total_matches ?? "—"} {searchInfo?.total_matches === 1 ? "role" : "roles"}</strong>
                  <span>
                    from {searchInfo?.screened ?? 0} stored postings ·{" "}
                    {searchInfo?.excluded ?? 0} filtered out
                  </span>
                </div>
                <button
                  className="text-button"
                  disabled={busy}
                  onClick={() => search(prefs, true)}
                >
                  <RefreshCw size={14} className={busy ? "spin" : ""} /> Refresh
                  employer feeds
                </button>
              </div>
              {searchInfo?.sources?.some((s: any) => s.status !== "ok") && (
                <div className="banner error">
                  Some employer feeds are unavailable. Stored snapshots remain
                  visible; verify openings at the source.
                </div>
              )}
              <div className="results-layout">
                <section className="job-list" aria-label="Job matches">
                  {busy && <div className="loading-bar" />}
                  {jobs.map((j) => (
                    <article
                      key={j.id}
                      className={
                        "job-card " + (selected?.id === j.id ? "selected" : "")
                      }
                    >
                      <button
                        className="job-select"
                        disabled={working}
                        onClick={() => {
                          setSelected(j);
                          setRun(null);
                          if (window.innerWidth < 900)
                            requestAnimationFrame(() =>
                              document
                                .querySelector(".fit-panel")
                                ?.scrollIntoView({ behavior: "smooth" }),
                            );
                        }}
                      >
                        <div className="card-top">
                          <span
                            className={
                              "company-logo " +
                              (j.industry === "Healthcare" ? "health" : "")
                            }
                          >
                            {j.company.slice(0, 1)}
                          </span>
                          <div>
                            <strong>{j.company}</strong>
                            <span>{j.industry}</span>
                          </div>
                          <span className="match">
                            {j.score === null ? "—" : j.score}
                            <small>FIT</small>
                          </span>
                        </div>
                        <h3>{j.title}</h3>
                        <p className="location">
                          <MapPin size={13} />
                          {j.location}
                        </p>
                        <div className="job-meta">
                          <span>
                            {j.salary_min
                              ? money(j.salary_min) +
                                (j.salary_max ? "–" + money(j.salary_max) : "")
                              : "Pay not parsed"}
                          </span>
                          <span>
                            {j.job_type === "unknown"
                              ? "Type not stated"
                              : j.job_type}
                          </span>
                        </div>
                        <div className="card-bottom">
                          <span>Source checked {date(j.retrieved_at)}</span>
                          <ArrowUpRight size={16} />
                        </div>
                      </button>
                      <button
                        className={
                          "save-job " +
                          (track.some((t) => t.job_id === j.id) ? "saved" : "")
                        }
                        title="Save role"
                        aria-label={"Save " + j.title}
                        onClick={() => saveJob(j)}
                      >
                        <Bookmark size={16} />
                      </button>
                    </article>
                  ))}
                  {!busy && !jobs.length && (
                    <div className="empty">
                      <Search size={30} />
                      <h3>No roles meet this brief.</h3>
                      <p>
                        Try fewer keywords or broader locations, refresh the
                        feeds, or add a posting yourself. We won’t invent
                        alternatives.
                      </p>
                    </div>
                  )}
                  <p className="fine">
                    Showing up to {searchInfo?.returned_cap || 100} matches.
                    Snapshot dates are retrieval dates, not posting dates.
                    Company sectors are curated labels. Open the employer page
                    to confirm availability and eligibility.
                  </p>
                </section>
                <aside className="fit-panel">
                  {selected ? (
                    <>
                      <button
                        className="text-button mobile-back"
                        onClick={() =>
                          document
                            .querySelector(".results-head")
                            ?.scrollIntoView({ behavior: "smooth" })
                        }
                      >
                        ↑ Back to matches
                      </button>
                      <div className="section-head">
                        <span className="eyebrow">THE FIT, EXPLAINED</span>
                        <span className="round-icon">
                          <Sparkles size={17} />
                        </span>
                      </div>
                      <h2>{selected.title}</h2>
                      <p className="muted">
                        {selected.company} · {selected.location}
                      </p>
                      <div className="score-hero">
                        <div
                          className="score-ring"
                          style={
                            { "--score": (selected.score || 0) + "%" } as any
                          }
                        >
                          <span>
                            {selected.score ?? "—"}
                            <small>/ 100</small>
                          </span>
                        </div>
                        <div>
                          <strong>Evidence overlap</strong>
                          <p>
                            A transparent signal.
                            <br />
                            Not your chance of getting hired.
                          </p>
                        </div>
                      </div>
                      <div className="score-parts">
                        {Object.entries(selected.breakdown || {}).map(
                          ([key, v]) => (
                            <div key={key}>
                              <span>
                                {
                                  (
                                    {
                                      resume_skills: "Resume skills",
                                      transferable_evidence:
                                        "Transferable evidence",
                                      role_focus: "Your role focus",
                                    } as any
                                  )[key]
                                }
                              </span>
                              <strong>
                                {v} /{" "}
                                {key === "resume_skills"
                                  ? 50
                                  : key === "transferable_evidence"
                                    ? 30
                                    : 20}
                              </strong>
                            </div>
                          ),
                        )}
                      </div>
                      <section className="application-checks" aria-label="Check before applying">
                        <span className="eyebrow">BEFORE YOU INVEST THE TIME</span>
                        <h3>Check before applying</h3>
                        <p>A high overlap score can hide a qualification gap. These excerpts flag wording to review, including preferred or conditional criteria.</p>
                        {selected.application_checks?.length ? selected.application_checks.map(check => (
                          <details key={check.kind}>
                            <summary>{check.label}<span>Review</span></summary>
                            <blockquote>{check.source_quote}</blockquote>
                            <p>{check.question}</p>
                          </details>
                        )) : <p>No screening phrases detected. Read the full posting; this is not an eligibility clearance.</p>}
                        <small>Source-based screening. No AI call, no eligibility verdict.</small>
                      </section>
                      <h4>What connects</h4>
                      {selected.evidence?.length ? (
                        selected.evidence.slice(0, 3).map((e) => (
                          <div className="connection" key={e.fact_id}>
                            <CheckCircle2 size={16} />
                            <div>
                              <strong>{e.title}</strong>
                              <p>{e.terms.slice(0, 5).join(" · ")}</p>
                              <small>Resume fact {e.fact_id}</small>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="muted">
                          Add a reviewed resume to connect your experience to
                          this role.
                        </p>
                      )}
                      <details className="score-method">
                        <summary>How is this score calculated?</summary>
                        <p>
                          50 points for the proportion of your skill terms found
                          in the posting; up to 30 for three
                          experience/education facts with overlapping terms; 20
                          for search keywords in the job title. Keyword overlap
                          can overstate fit. AI review checks the connections
                          and gaps; it does not set this score.
                        </p>
                      </details>
                      <button
                        className="button primary full"
                        disabled={!profile?.confirmed || working}
                        onClick={analyze}
                      >
                        <Sparkles size={16} />
                        {working
                          ? "Reviewing the evidence…"
                          : "Get an AI evidence review"}
                      </button>
                      <p className="fine">
                        Sends professional facts and this posting to{" "}
                        {status?.model || "the model"}. Contact and sensitive
                        answers are excluded.
                      </p>
                      <Feed />
                      {run?.kind === "fit" &&
                        profile?.confirmed &&
                        run.result &&
                        analysisJobId === selected.id && (
                          <div className="analysis">
                            <h4>Analyst’s view</h4>
                            <p>{run.result.summary}</p>
                            {run.result.evidence?.map((e: any, i: number) => (
                              <blockquote key={i}>
                                <strong>{e.fact_id} → employer evidence</strong>
                                <p>“{e.job_quote}”</p>
                                <small>{e.connection}</small>
                              </blockquote>
                            ))}
                            <h4>Not yet evidenced</h4>
                            <ul>
                              {run.result.gaps?.map((g: string) => (
                                <li key={g}>{g}</li>
                              ))}
                            </ul>
                            <h4>Questions worth asking</h4>
                            <ul>
                              {run.result.questions?.map((g: string) => (
                                <li key={g}>{g}</li>
                              ))}
                            </ul>
                            <h4>Interview preparation</h4>
                            <ul>
                              {run.result.interview_angles?.map((g: string) => (
                                <li key={g}>{g}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      <div className="detail-actions">
                        <button
                          className="button secondary"
                          onClick={() => saveJob(selected)}
                        >
                          <Bookmark size={16} />
                          Save role
                        </button>
                        <a
                          className="button secondary"
                          target="_blank"
                          rel="noreferrer"
                          href={selected.url}
                        >
                          Employer page
                          <ExternalLink size={15} />
                        </a>
                      </div>
                      <details className="description">
                        <summary>Read the source posting</summary>
                        <p>{selected.description}</p>
                      </details>
                    </>
                  ) : (
                    <div className="empty">
                      <FileText />
                      <h3>Choose a role</h3>
                      <p>We’ll show the source evidence and the gaps here.</p>
                    </div>
                  )}
                </aside>
              </div>
            </>
          )}
          {tab === "profile" && (
            <>
              <div className="page-heading">
                <div className="eyebrow">YOUR EXPERIENCE, ON THE RECORD</div>
                <h1>
                  Start with <em>your evidence.</em>
                </h1>
                <p>One reviewed profile. A clear source for every claim.</p>
              </div>
              <div className="two-col">
                <section>
                  <div className="panel">
                    <h2>Bring your resume</h2>
                    <p>
                      PDF, DOCX or text · up to 4 MB · scanned PDFs need pasted
                      text.
                    </p>
                    <label className="upload">
                      <Upload size={28} />
                      <strong>{upload?.name || "Choose your resume"}</strong>
                      <span>
                        We process the file in memory, not an uploads folder.
                      </span>
                      <input
                        aria-label="Upload resume"
                        type="file"
                        accept=".pdf,.docx,.txt"
                        onChange={(e) => setUpload(e.target.files?.[0] || null)}
                      />
                    </label>
                    <details>
                      <summary>Or paste your resume text</summary>
                      <textarea
                        aria-label="Resume text"
                        rows={7}
                        value={resumeText}
                        onChange={(e) => {
                          setResumeText(e.target.value);
                          setUpload(null);
                        }}
                        placeholder="Paste the text of your resume here…"
                      />
                    </details>
                    <label className="check-label">
                      <input
                        type="checkbox"
                        checked={consent}
                        onChange={(e) => setConsent(e.target.checked)}
                      />
                      I agree to send this resume text to the configured AI
                      provider for extraction. I’ll review the result.
                    </label>
                    <button
                      className="button primary full"
                      disabled={busy || working || !consent}
                      onClick={extract}
                    >
                      <Sparkles size={17} />
                      {working ? "Extracting facts…" : "Extract my resume"}
                    </button>
                    <button className="text-button demo-link" onClick={demo}>
                      Try the fictional demo instead →
                    </button>
                    <Feed />
                  </div>
                  <div className="panel privacy">
                    <ShieldCheck />
                    <h3>Some answers belong to you.</h3>
                    <p>
                      Veteran status, work authorization and employer consent
                      are never guessed from your resume. Your local workspace
                      is separate from other browser sessions.
                    </p>
                    <p>
                      Original files aren’t saved. Extracted text and reviewed
                      fields remain in the local database until you delete them.
                      This is a local personal tool, not a shared hosted account
                      service.
                    </p>
                  </div>
                </section>
                <section className="panel">
                  {profile ? (
                    <>
                      <div className="section-head">
                        <h2>
                          {profile.confirmed
                            ? "Your reviewed profile"
                            : "Review extracted facts"}
                        </h2>
                        <span className="tag">
                          {profile.demo
                            ? "FICTIONAL DEMO"
                            : profile.confirmed
                              ? "REVIEWED"
                              : "DRAFT"}
                        </span>
                      </div>
                      {profile.warnings.map((x) => (
                        <p className="warning" key={x}>
                          {x}
                        </p>
                      ))}
                      <div className="fields">
                        {[
                          ["full_name", "Full name"],
                          ["first_name", "Given name for forms (optional)"],
                          ["last_name", "Family name for forms (optional)"],
                          ["email", "Email"],
                          ["phone", "Phone"],
                          ["location", "Location"],
                          ["linkedin", "LinkedIn / portfolio"],
                        ].map(([key, label]) => (
                          <label key={key}>
                            {label}
                            <input
                              value={(profile as any)[key] || ""}
                              onChange={(e) =>
                                setProfile({
                                  ...profile,
                                  [key]: e.target.value,
                                  confirmed: false,
                                })
                              }
                            />
                          </label>
                        ))}
                      </div>
                      <h3>Professional facts</h3>
                      {profile.facts.map((fact, i) => (
                        <details className="fact" key={fact.id} open={i === 0}>
                          <summary>
                            <span className="fact-id">{fact.id}</span>
                            {fact.title}
                            <small>{fact.kind}</small>
                          </summary>
                          <label>
                            Fact type
                            <select
                              value={fact.kind}
                              onChange={(e) =>
                                setProfile({
                                  ...profile,
                                  confirmed: false,
                                  facts: profile.facts.map((f, k) =>
                                    k === i
                                      ? { ...f, kind: e.target.value as any }
                                      : f,
                                  ),
                                })
                              }
                            >
                              {[
                                "experience",
                                "education",
                                "skill",
                                "language",
                              ].map((x) => (
                                <option key={x}>{x}</option>
                              ))}
                            </select>
                          </label>
                          <div className="fields">
                            {[
                              "title",
                              "organization",
                              "start",
                              "end",
                              "description",
                            ].map((key) => (
                              <label key={key}>
                                {key}
                                <input
                                  value={(fact as any)[key]}
                                  onChange={(e) =>
                                    setProfile({
                                      ...profile,
                                      confirmed: false,
                                      facts: profile.facts.map((f, k) =>
                                        k === i
                                          ? { ...f, [key]: e.target.value }
                                          : f,
                                      ),
                                    })
                                  }
                                />
                              </label>
                            ))}
                          </div>
                          <blockquote>{fact.evidence_quote}</blockquote>
                          <small>
                            Original resume excerpt. Review corrections before
                            use.
                          </small>
                          <button
                            className="text-button danger"
                            onClick={() =>
                              setProfile({
                                ...profile,
                                confirmed: false,
                                facts: profile.facts.filter((_, k) => k !== i),
                              })
                            }
                          >
                            Remove fact
                          </button>
                        </details>
                      ))}
                      <button
                        className="button secondary"
                        onClick={() => {
                          const ids = new Set(profile.facts.map((f) => f.id));
                          let i = 1;
                          while (ids.has("U" + i)) i++;
                          setProfile({
                            ...profile,
                            confirmed: false,
                            facts: [
                              ...profile.facts,
                              {
                                id: "U" + i,
                                kind: "skill",
                                title: "New skill",
                                organization: "",
                                start: "",
                                end: "",
                                description: "",
                                evidence_quote:
                                  "User-entered fact; verify before using.",
                              },
                            ],
                          });
                        }}
                      >
                        <Plus size={16} />
                        Add a fact
                      </button>
                      <h3>Optional application answers</h3>
                      <p className="fine">
                        Not used for scoring or sent to the analyst. You choose
                        whether to fill these on each application.
                      </p>
                      <label>
                        Veteran status
                        <select
                          value={profile.veteran_status || ""}
                          onChange={(e) =>
                            setProfile({
                              ...profile,
                              veteran_status: e.target.value || null,
                              confirmed: false,
                            })
                          }
                        >
                          <option value="">Not provided — always ask me</option>
                          <option>I am not a protected veteran</option>
                          <option>I identify as a protected veteran</option>
                          <option>I do not wish to answer</option>
                        </select>
                      </label>
                      <label>
                        Work authorization (your exact answer)
                        <input
                          value={profile.work_authorization || ""}
                          onChange={(e) =>
                            setProfile({
                              ...profile,
                              work_authorization: e.target.value || null,
                              confirmed: false,
                            })
                          }
                          placeholder="Optional; never inferred"
                        />
                      </label>
                      <button
                        className="button primary full"
                        disabled={busy}
                        onClick={saveProfile}
                      >
                        <Check size={16} />I reviewed these facts — save profile
                      </button>
                    </>
                  ) : (
                    <div className="empty">
                      <FileText size={34} />
                      <h2>Your profile will appear here.</h2>
                      <p>
                        You’ll check names, dates and supporting quotes before
                        the app uses them.
                      </p>
                    </div>
                  )}
                </section>
              </div>
            </>
          )}
          {tab === "kit" && (
            <>
              <div className="page-heading">
                <div className="eyebrow">LESS RE-TYPING. MORE CONTROL.</div>
                <h1>
                  Application <em>kit.</em>
                </h1>
                <p>
                  Reuse your work history and education. Review every answer
                  before it leaves your browser.
                </p>
              </div>
              <div className="kit-hero">
                <div>
                  <span className="tag">REVIEW → FILL → CHECK</span>
                  <h2>
                    The repetitive fields,
                    <br />
                    taken off your plate.
                  </h2>
                  <p>
                    Export your reviewed profile, preview the current
                    application’s fields, and fill only the values you approve.
                  </p>
                  <div className="actions">
                    <button
                      className="button primary"
                      disabled={!profile?.confirmed}
                      onClick={packet}
                    >
                      <Download size={17} />
                      Export private profile
                    </button>
                    <a
                      className="button secondary"
                      href="/application-lab.html"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Try the practice lab <ArrowUpRight size={17} />
                    </a>
                  </div>
                </div>
                <div className="paper-mock">
                  <span>YOUR VERIFIED FACTS</span>
                  <div>
                    <CheckCircle2 /> Work experience{" "}
                    <small>Ready to review</small>
                  </div>
                  <div>
                    <CheckCircle2 /> Education <small>Ready to review</small>
                  </div>
                  <div>
                    <CheckCircle2 /> Languages <small>Only if provided</small>
                  </div>
                  <div className="manual">
                    <ShieldCheck /> Consent & signature{" "}
                    <small>You decide, each time</small>
                  </div>
                </div>
              </div>
              <div className="three-col">
                <section className="panel">
                  <span className="step">01</span>
                  <h3>Install the helper</h3>
                  <p>
                    Download and unzip the extension. In Chrome, open{" "}
                    <code>chrome://extensions</code>, enable Developer mode and
                    choose Load unpacked.
                  </p>
                  <a className="text-button" href="/api/extension.zip">
                    Download extension <Download size={15} />
                  </a>
                </section>
                <section className="panel">
                  <span className="step">02</span>
                  <h3>Preview this page</h3>
                  <p>
                    Import your private profile packet into the extension, then
                    open the employer’s form and click Preview this page. It
                    uses only the active tab.
                  </p>
                </section>
                <section className="panel">
                  <span className="step">03</span>
                  <h3>Fill what you approve</h3>
                  <p>
                    Review each proposed value. Sensitive answers start
                    unchecked. Existing answers are protected. Confirm dates,
                    consent and custom widgets yourself.
                  </p>
                </section>
              </div>
              <div className="panel">
                <h3>Where it works—and what stays manual</h3>
                <p>
                  Supports common labeled text fields, text areas, exact-match
                  dropdowns and repeated work-history sections, including some
                  Workday field patterns. Workday portals vary: custom controls,
                  cross-origin frames, uploads, logins and CAPTCHA may need
                  manual entry. The practice lab proves the shared filling code
                  on a local fixture, not universal Workday compatibility.
                </p>
                <p>
                  <strong>
                    No automatic application submission, legal agreement
                    acceptance, signature, demographic inference or employer
                    contact.
                  </strong>
                </p>
              </div>
            </>
          )}
          {tab === "tracker" && (
            <>
              <div className="page-heading">
                <div className="eyebrow">YOUR NEXT MOVES, IN ONE PLACE</div>
                <h1>
                  Keep the <em>momentum.</em>
                </h1>
                <p>
                  Save the roles worth your time. Track the work you actually
                  do.
                </p>
              </div>
              <div className="pipeline-counts">
                {stages.map((s) => (
                  <div key={s}>
                    <span>{s}</span>
                    <strong>{track.filter((t) => t.stage === s).length}</strong>
                  </div>
                ))}
              </div>
              {!track.length ? (
                <div className="empty panel">
                  <Bookmark />
                  <h2>Your pipeline starts with one good role.</h2>
                  <p>
                    Save a role from Discover to keep notes and track your next
                    step.
                  </p>
                  <button
                    className="button primary"
                    onClick={() => setTab("discover")}
                  >
                    Discover roles
                    <ArrowRight size={17} />
                  </button>
                </div>
              ) : (
                track.map((t) => (
                  <article className="tracker-card" key={t.job_id}>
                    <div>
                      <span className="eyebrow">
                        {t.job?.company || "Posting no longer available"}
                      </span>
                      <h3>{t.job?.title || t.job_id}</h3>
                      <p>{t.job?.location}</p>
                      {t.job && (
                        <a href={t.job.url} target="_blank" rel="noreferrer">
                          Employer posting ↗
                        </a>
                      )}
                    </div>
                    <div>
                      <label>
                        Stage
                        <select
                          disabled={!t.job}
                          value={t.stage}
                          onChange={(e) =>
                            saveJob(t.job, e.target.value, t.note, t.follow_up)
                          }
                        >
                          {stages.map((s) => (
                            <option key={s}>{s}</option>
                          ))}
                        </select>
                      </label>
                      <label>
                        Follow up
                        <input
                          type="date"
                          defaultValue={t.follow_up}
                          onBlur={(e) =>
                            t.job &&
                            saveJob(t.job, t.stage, t.note, e.target.value)
                          }
                        />
                      </label>
                    </div>
                    <label>
                      Private notes
                      <textarea
                        defaultValue={t.note}
                        rows={3}
                        placeholder="Referral, deadline, interview prep…"
                        onBlur={(e) =>
                          t.job &&
                          saveJob(t.job, t.stage, e.target.value, t.follow_up)
                        }
                      />
                    </label>
                  </article>
                ))
              )}
              <p className="fine">
                Changing a stage records your own progress. It does not submit
                an application or contact an employer.
              </p>
            </>
          )}
          {tab === "evidence" && (
            <>
              <div className="page-heading">
                <div className="eyebrow">THE WORK BEHIND THE WORK</div>
                <h1>
                  Useful, <em>and accountable.</em>
                </h1>
                <p>
                  Real usage from this workspace. Clear boundaries around what
                  the app can do.
                </p>
              </div>
              <div className="metric-grid">
                {[
                  ["Input tokens", metrics?.input_tokens || 0],
                  ["Output tokens", metrics?.output_tokens || 0],
                  ["Cached assessments", metrics?.cache_hits || 0],
                  [
                    "Estimated model cost",
                    "$" + (metrics?.total_cost || 0).toFixed(5),
                  ],
                ].map(([label, value]) => (
                  <div className="metric" key={label}>
                    <span>{label}</span>
                    <strong>{value.toLocaleString()}</strong>
                  </div>
                ))}
              </div>
              <div className="two-col">
                <section className="panel">
                  <h2>Measured, not invented</h2>
                  <p>{metrics?.cost_note}</p>
                  <p>
                    Model: <strong>{status?.model}</strong>. Cached input:{" "}
                    {metrics?.cached_tokens || 0} tokens. Local overlap scoring
                    and form filling make zero model calls.
                  </p>
                  <p>
                    Daily shared admission budget:{" "}
                    {status?.limits?.daily_ai_runs} AI runs. Each run: up to{" "}
                    {status?.limits?.requests_per_run} requests and{" "}
                    {status?.limits?.tokens_per_run?.toLocaleString()} tokens,
                    with a {status?.limits?.timeout_seconds}-second timeout.
                  </p>
                  <a
                    href={metrics?.price_source}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Pricing source · checked {metrics?.price_checked} ↗
                  </a>
                  <button
                    className="button secondary"
                    onClick={() => download(metrics, "pivot-usage.json")}
                  >
                    Export usage counts
                    <Download size={16} />
                  </button>
                </section>
                <section className="panel privacy">
                  <ShieldCheck />
                  <h2>Your review is the boundary</h2>
                  <p>
                    Hard filters run before AI. Employer text is untrusted.
                    Evidence citations must refer to actual resume fact IDs and
                    exact posting excerpts. Application consent and submission
                    stay manual.
                  </p>
                  <p>
                    The local database is not encrypted. Use this on your own
                    device; do not expose the server publicly. No secrets or
                    personal resumes belong in the submission repo.
                  </p>
                  <button
                    className="button secondary danger"
                    disabled={working}
                    onClick={async () => {
                      if (
                        window.confirm(
                          "Delete this browser workspace’s profile, resume text, matches and notes? Anonymous usage totals remain for budget enforcement.",
                        )
                      ) {
                        try {
                          await api("/private", { method: "DELETE" });
                          setProfile(null);
                          setRun(null);
                          await boot();
                          setNotice("Private workspace data deleted.");
                        } catch (e) {
                          setError(String(e));
                        }
                      }
                    }}
                  >
                    <Trash2 size={15} />
                    Delete my private data
                  </button>
                </section>
              </div>
              <section className="panel">
                <h2>AI run ledger</h2>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Run</th>
                        <th>Input</th>
                        <th>Cached input</th>
                        <th>Output</th>
                        <th>Requests</th>
                        <th>Estimated cost</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metrics?.runs?.map((r: any) => (
                        <tr key={r.run_id}>
                          <td>{r.run_id.slice(0, 8)}</td>
                          <td>{r.input_tokens}</td>
                          <td>{r.cached_tokens}</td>
                          <td>{r.output_tokens}</td>
                          <td>{r.requests}</td>
                          <td>${r.cost.toFixed(6)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {!metrics?.runs?.length && (
                    <p>No model calls in this workspace yet.</p>
                  )}
                </div>
              </section>
            </>
          )}
          <footer>
            <span className="brand-word">pivot desk ↗</span>
            <span>Your next chapter. Your final say.</span>
            <span>AI Foundations · Final Project</span>
          </footer>
        </div>
      </div>
      {showImport && (
        <div className="modal-backdrop" role="presentation">
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="import-title"
          >
            <button
              className="close"
              aria-label="Close posting import"
              onClick={() => setShowImport(false)}
            >
              <X />
            </button>
            <h2 id="import-title">Bring a role to your desk.</h2>
            <p>
              Paste a posting from Workday or another employer site. We won’t
              scrape a private application page.
            </p>
            {Object.entries(importData).map(([key, value]) => (
              <label key={key}>
                {key === "url" ? "Original HTTPS posting link" : key}
                {key === "description" ? (
                  <textarea
                    rows={6}
                    value={value}
                    onChange={(e) =>
                      setImportData({ ...importData, [key]: e.target.value })
                    }
                  />
                ) : (
                  <input
                    value={value}
                    onChange={(e) =>
                      setImportData({ ...importData, [key]: e.target.value })
                    }
                  />
                )}
              </label>
            ))}
            <button className="button primary" onClick={importJob}>
              Add to my workspace
              <Plus size={17} />
            </button>
          </section>
        </div>
      )}
    </div>
  );
}
