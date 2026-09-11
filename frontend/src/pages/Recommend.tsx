import { useEffect, useState } from 'react'
import { api, Job } from '../api/client'

type Preset = { major:string; degree:string; skills:string[]; preferred_cities:string[]; preferred_categories:string[] }

export default function Recommend(){
  const [presets, setPresets] = useState<Record<string, Preset> | null>(null)
  const [form, setForm] = useState<Preset>({ major:'计算机科学与技术', degree:'本科', skills:['Java','Python','Vue','SpringBoot','MySQL'], preferred_cities:['长沙','深圳'], preferred_categories:['技术开发'] })
  const [result, setResult] = useState<{recommendations: (Job & {reasons:string[]})[]} | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
    api.get('/api/recommend/presets').then(r=>{
      setPresets(r.data)
      setForm(r.data.cs_undergrad)
    })
  },[])

  const submit = async () => {
    setLoading(true)
    const r = await api.post('/api/recommend?limit=12', form)
    setResult(r.data)
    setLoading(false)
  }
  useEffect(()=>{ if(presets) submit() }, [presets])

  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>智能推荐 · 基于画像 + 协同思路</h3>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>输入你的专业/技能/偏好城市与类别，系统做 Jaccard 技能匹配 + 城市/类别加权，输出 Top 匹配度并附理由；支持一键切换计科各方向预设。</div>
        {presets && (
          <div style={{marginTop:10, display:'flex', gap:8, flexWrap:'wrap'}}>
            <button onClick={()=>setForm(presets.cs_undergrad)} style={btn}>计科通用</button>
            <button onClick={()=>setForm(presets.security)} style={btn}>信息安全</button>
            <button onClick={()=>setForm(presets.ai_bigdata)} style={btn}>大数据/AI</button>
          </div>
        )}
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, marginTop:12}}>
          <Field label="专业"><input value={form.major} onChange={e=>setForm({...form, major:e.target.value})} style={inp} /></Field>
          <Field label="学历"><input value={form.degree} onChange={e=>setForm({...form, degree:e.target.value})} style={inp} /></Field>
          <Field label="技能（逗号分隔）"><input value={form.skills.join(',')} onChange={e=>setForm({...form, skills:e.target.value.split(',').map(s=>s.trim()).filter(Boolean)})} style={inp} /></Field>
          <Field label="偏好城市（逗号）"><input value={form.preferred_cities.join(',')} onChange={e=>setForm({...form, preferred_cities:e.target.value.split(',').map(s=>s.trim()).filter(Boolean)})} style={inp} /></Field>
          <Field label="偏好类别（逗号）"><input value={form.preferred_categories.join(',')} onChange={e=>setForm({...form, preferred_categories:e.target.value.split(',').map(s=>s.trim()).filter(Boolean)})} style={inp} /></Field>
          <div style={{display:'flex', alignItems:'end'}}><button onClick={submit} style={{padding:'10px 18px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:800, width:'100%'}}>{loading?'推荐中…':'生成推荐'}</button></div>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:12}}>
        {result?.recommendations.map(job=>(
          <div key={job.id} style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8}}>
            <div style={{fontWeight:800}}>{job.title}</div>
            <div style={{fontSize:13, color:'#334155'}}>{job.company_name} · {job.category} {job._score ? <span style={{background:'#eef2ff', color:'#1E55AF', padding:'2px 8px', borderRadius:999, fontSize:11, marginLeft:6}}>匹配 {job._score}</span> : null}</div>
            <div style={{fontSize:12, color:'#475569'}}>📍 {job.location_city || job.location_raw || '待定'} · 💰 {job.salary_raw || (job.salary_min? `${job.salary_min}-${job.salary_max}`:'面议')}</div>
            <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>
              {(job.skills||[]).slice(0,4).map(s=><span key={s.name} style={{background:'#f1f5f9', padding:'4px 8px', borderRadius:999, fontSize:11}}>{s.name}</span>)}
            </div>
            <div style={{fontSize:12, color:'#0ea5e9'}}>{job.reasons?.join(' · ')}</div>
            {job.source_url && <a href={job.source_url} target="_blank" rel="noreferrer" style={{fontSize:12, color:'#1E55AF'}}>溯源链接 →</a>}
          </div>
        ))}
      </div>
    </div>
  )
}
const inp:React.CSSProperties = { width:'100%', padding:'8px 10px', borderRadius:10, border:'1px solid #e2e8f0' }
const btn:React.CSSProperties = { padding:'6px 10px', borderRadius:999, border:'1px solid #e2e8f0', background:'#fff', fontSize:12 }
function Field(props:{label:string; children:React.ReactNode}){ return <label style={{fontSize:12, color:'#475569'}}>{props.label}<div style={{marginTop:4}}>{props.children}</div></label> }
