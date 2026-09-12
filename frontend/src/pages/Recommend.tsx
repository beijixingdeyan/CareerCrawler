import { useEffect, useState } from 'react'
import { api, Job } from '../api/client'

type Preset = { major:string; degree:string; skills:string[]; preferred_cities:string[]; preferred_categories:string[] }

const INDUSTRIES = ["全部","制造业","教育","信息传输、软件和信息技术服务业","建筑业","批发和零售业","电力、热力、燃气及水生产和供应业","采矿业","科学研究和技术服务业","交通运输、仓储和邮政业","农、林、牧、渔业","住宿和餐饮业","文化、体育和娱乐业","金融业","水利、环境和公共设施管理业","公共管理、社会保障和社会组织","租赁和商务服务业","其它"]
export default function Recommend(){
  const [presets, setPresets] = useState<Record<string, Preset> | null>(null)
  const [form, setForm] = useState<Preset & {preferred_industries?: string[]}>({ major:'计算机科学与技术', degree:'本科', skills:['Java','Python','Vue','SpringBoot','MySQL'], preferred_cities:['长沙','深圳'], preferred_categories:['技术开发'], preferred_industries: [] } as any)
  const [industry,setIndustry]=useState('全部')
  const [result, setResult] = useState<{recommendations: (Job & {reasons:string[]})[], total?:number, total_pool?:number, page?:number, page_size?:number} | null>(null)
  const [loading, setLoading] = useState(false)
  const [page,setPage]=useState(1)
  const pageSize=12

  useEffect(()=>{
    api.get('/api/recommend/presets').then(r=>{
      setPresets(r.data)
      setForm(r.data.cs_undergrad)
    })
  },[])

  const submit = async (p=page) => {
    setLoading(true)
    let clicked: string[] = []
    try{ clicked = JSON.parse(localStorage.getItem('clicked_fair_ids')||'[]') }catch{}
    const payload:any = { ...form, clicked_fair_ids: clicked, preferred_industries: industry==='全部'? [] : [industry] }
    if(industry!=='全部') payload.preferred_industries=[industry]
    const r = await api.post(`/api/recommend?limit=1000&page=${p}&page_size=${pageSize}${industry!=='全部'?'&industry='+encodeURIComponent(industry):''}`, payload)
    setResult(r.data)
    setLoading(false)
  }
  useEffect(()=>{ if(presets) { setPage(1); submit(1) } }, [presets])
  useEffect(()=>{ if(presets) submit(page) }, [page, industry])

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
        <div style={{marginTop:10, display:'flex', gap:6, flexWrap:'wrap', alignItems:'center'}}>
          <span style={{fontSize:12, color:'#475569'}}>行业筛选：</span>
          {INDUSTRIES.map(ind=>(
            <button key={ind} onClick={()=>setIndustry(ind)} style={{padding:'6px 12px', borderRadius:999, border: industry===ind?'1px solid #1E55AF':'1px solid #e2e8f0', background: industry===ind?'#1E55AF':'#fff', color: industry===ind?'#fff':'#475569', fontSize:12, fontWeight:600}}>{ind}</button>
          ))}
        </div>
        <div style={{fontSize:11, color:'#64748b', marginTop:6}}>推荐池已包含 <b>宣讲会 500</b> + <b>已点双选会企业</b>（点击双选会卡片即记录，当前已记录 {(() => { try{ return JSON.parse(localStorage.getItem('clicked_fair_ids')||'[]').length }catch{ return 0 } })()} 场），按行业/技能/城市/类别加权，无虚假数据</div>
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, marginTop:12}}>
          <Field label="专业"><input value={form.major} onChange={e=>setForm({...form, major:e.target.value})} style={inp} /></Field>
          <Field label="学历"><input value={form.degree} onChange={e=>setForm({...form, degree:e.target.value})} style={inp} /></Field>
          <Field label="技能（逗号分隔）"><input value={form.skills.join(',')} onChange={e=>setForm({...form, skills:e.target.value.split(',').map(s=>s.trim()).filter(Boolean)})} style={inp} /></Field>
          <Field label="偏好城市（逗号）"><input value={form.preferred_cities.join(',')} onChange={e=>setForm({...form, preferred_cities:e.target.value.split(',').map(s=>s.trim()).filter(Boolean)})} style={inp} /></Field>
          <Field label="偏好类别（逗号）"><input value={form.preferred_categories.join(',')} onChange={e=>setForm({...form, preferred_categories:e.target.value.split(',').map(s=>s.trim()).filter(Boolean)})} style={inp} /></Field>
          <div style={{display:'flex', alignItems:'end'}}><button onClick={()=>{ setPage(1); submit(1)}} style={{padding:'10px 18px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:800, width:'100%'}}>{loading?'推荐中…':'生成推荐'}</button></div>
        </div>
      </div>
      <div style={{fontSize:12, color:'#64748b', textAlign:'center'}}>共 {result?.total ?? 0} 条推荐（池 {result?.total_pool ?? 0}：宣讲会500 + 已点双选会{ (result?.total_pool ?? 0) - 500 }）· 第 {result?.page ?? page} / {Math.max(1, Math.ceil((result?.total ?? 0)/pageSize))} 页 {result?.total !== result?.total_pool ? '· 已按行业/去重筛选' : ''}</div>
      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:12}}>
        {result?.recommendations.map((job:any)=>(
          <div key={job.id} style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8}}>
            <div style={{fontWeight:800}}>{job.title}</div>
            <div style={{fontSize:13, color:'#334155'}}>{job.company_name} · {job.category} {job.industry ? <span style={{background:'#fef3c7', padding:'2px 6px', borderRadius:999, fontSize:11, marginLeft:6}}>{job.industry}</span> : null} {job._score ? <span style={{background:'#eef2ff', color:'#1E55AF', padding:'2px 8px', borderRadius:999, fontSize:11, marginLeft:6}}>匹配 {job._score}</span> : null}</div>
            <div style={{fontSize:12, color:'#475569'}}>📍 {job.location_city || job.location_raw || '待定'} · 💰 {job.salary_raw || (job.salary_min? `${job.salary_min}-${job.salary_max}`:'面议')}</div>
            <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>
              {(job.skills||[]).slice(0,4).map((s:any)=><span key={s.name} style={{background:'#f1f5f9', padding:'4px 8px', borderRadius:999, fontSize:11}}>{s.name}</span>)}
            </div>
            <div style={{fontSize:12, color:'#0ea5e9'}}>{job.reasons?.join(' · ')}</div>
            {job.source_url && <a href={job.source_url} target="_blank" rel="noreferrer" style={{fontSize:12, color:'#1E55AF'}}>溯源链接 →</a>}
          </div>
        ))}
      </div>
      <div style={{display:'flex', gap:8, justifyContent:'center', marginTop:8}}>
        <button disabled={(result?.page ?? page) <=1} onClick={()=>setPage(p=>Math.max(1,p-1))} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: (result?.page ?? page)<=1?'#f1f5f9':'#fff'}}>上一页</button>
        <span style={{padding:'6px 12px', fontSize:12, color:'#64748b'}}>{result?.page ?? page} / {Math.max(1, Math.ceil((result?.total ?? 0)/pageSize))}</span>
        <button disabled={(result?.page ?? page) >= Math.max(1, Math.ceil((result?.total ?? 0)/pageSize))} onClick={()=>setPage(p=>p+1)} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: (result?.page ?? page) >= Math.max(1, Math.ceil((result?.total ?? 0)/pageSize))?'#f1f5f9':'#fff'}}>下一页</button>
      </div>
    </div>
  )
}
const inp:React.CSSProperties = { width:'100%', padding:'8px 10px', borderRadius:10, border:'1px solid #e2e8f0' }
const btn:React.CSSProperties = { padding:'6px 10px', borderRadius:999, border:'1px solid #e2e8f0', background:'#fff', fontSize:12 }
function Field(props:{label:string; children:React.ReactNode}){ return <label style={{fontSize:12, color:'#475569'}}>{props.label}<div style={{marginTop:4}}>{props.children}</div></label> }
