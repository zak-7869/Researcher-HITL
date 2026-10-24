"use client";
import { FormEvent, useState } from "react";
type Source = { title: string; url: string; content: string };
type Result = { run_id: string; topic: string; status: string; report: string; sources: Source[]; iterations: number; evaluation: Record<string, unknown> };
const API = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
export default function Home() {
 const [topic,setTopic]=useState(""); const [iterations,setIterations]=useState(2);
 const [result,setResult]=useState<Result|null>(null); const [busy,setBusy]=useState(false);
 const [error,setError]=useState(""); const [reviewMessage,setReviewMessage]=useState("");
 async function submit(e:FormEvent){e.preventDefault();setBusy(true);setError("");setResult(null);setReviewMessage("");
  try{const r=await fetch(`${API}/api/research`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic,max_iterations:iterations})});
   const d=await r.json();if(!r.ok)throw new Error(d.detail||"Research request failed");setResult(d);
  }catch(err){setError(err instanceof Error?err.message:"Cannot reach API. Check backend URL and CORS.");}finally{setBusy(false);}}
 async function review(decision:"approve"|"request_changes"){if(!result)return;try{
  const r=await fetch(`${API}/api/research/${result.run_id}/review`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({decision,comment:""})});
  const d=await r.json();if(!r.ok)throw new Error(d.detail||"Review failed");setResult({...result,status:d.status});setReviewMessage(`Report status: ${d.status.replaceAll("_"," ")}`);
 }catch(err){setReviewMessage(err instanceof Error?err.message:"Review failed");}}
 return <main className="shell">
  <header className="topbar"><div className="brand">R</div><div><strong>Researcher AI</strong><span>Evidence-first research workspace</span></div><span className="tag">LANGGRAPH · GROQ · TAVILY</span></header>
  <section className="hero"><p className="eyebrow">RESEARCH AGENT WORKSPACE</p><h1>Turn a question into<br/><em>a sourced report.</em></h1><p className="subhead">Bounded research loops, visible evidence, and human review built into the workflow.</p></section>
  <section className="panel"><form onSubmit={submit}><label htmlFor="topic">What would you like to research?</label>
   <textarea id="topic" value={topic} onChange={e=>setTopic(e.target.value)} minLength={3} maxLength={500} required placeholder="e.g. Compare methods for evaluating AI agents and their trade-offs"/>
   <div className="formBottom"><label className="iteration">Research passes <select value={iterations} onChange={e=>setIterations(Number(e.target.value))}><option value={1}>1</option><option value={2}>2</option><option value={3}>3</option></select></label>
   <button disabled={busy||topic.trim().length<3}>{busy?"Researching…":"Run research →"}</button></div><p className="hint">Public web results are treated as untrusted evidence, never instructions.</p></form></section>
  {error&&<div className="notice error">{error}</div>}{busy&&<div className="notice">Planning, searching, evaluating evidence, and drafting the report…</div>}
  {result&&<section className="results"><div className="resultHead"><div><p className="eyebrow">RESEARCH REPORT</p><h2>{result.topic}</h2></div><span className={`status ${result.status}`}>{result.status.replaceAll("_"," ")}</span></div>
   <div className="stats"><div><small>Sources</small><strong>{result.sources.length}</strong></div><div><small>Research passes</small><strong>{result.iterations}</strong></div><div><small>Evidence sufficient</small><strong>{String(result.evaluation.evidence_sufficient??false)}</strong></div></div>
   <article className="report">{result.report.split("\n").map((line,i)=>line.startsWith("# ")?<h2 key={i}>{line.slice(2)}</h2>:line.startsWith("## ")?<h3 key={i}>{line.slice(3)}</h3>:line.trim()?<p key={i}>{line.replace(/\*\*(.*?)\*\*/g,"$1")}</p>:null)}</article>
   <div className="sourceBlock"><h3>Retrieved sources</h3>{result.sources.map((s,i)=><a className="source" key={s.url} href={s.url} target="_blank" rel="noreferrer"><b>{i+1}</b><span><strong>{s.title}</strong><small>{s.url}</small></span>↗</a>)}</div>
   {result.status==="pending_review"&&<div className="review"><div><h3>Human review</h3><p>Approve the report or request changes.</p></div><div className="actions"><button className="secondary" onClick={()=>review("request_changes")}>Request changes</button><button onClick={()=>review("approve")}>Approve report ✓</button></div></div>}
   {reviewMessage&&<div className="notice">{reviewMessage}</div>}<p className="runId">Run ID: {result.run_id}</p></section>}
  <footer><span>Researcher AI · Engineering starter</span><span>Grounded in sources. Reviewed by people.</span></footer>
 </main>;
}
