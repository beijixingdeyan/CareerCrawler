import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Search, ShieldAlert, ShieldCheck, Building2, MapPin, Banknote, GraduationCap, ExternalLink } from 'lucide-react'

export default function Companies(){
  const [q, setQ] = useState('')
  const [list, setList] = useState<any[]>([])
  const [detail, setDetail] = useState<any|null>(null)
  const [loading, setLoading] = useState(false)

  const fetchList = async () => {
    setLoading(true)
    const r = await api.get('/api/companies', { params: q?{q}:{} })
    setList(r.data)
    setLoading(false)
  }
  useEffect(()=>{ fetchList() }, [])

  const open = async (name:string) => {
    const r = await api.get(`/api/companies/${encodeURIComponent(name)}`)
    setDetail(r.data)
    window.scrollTo({ top:0, behavior:'smooth' })
  }

  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>企业库 · 权威大厂 + 参会审核</h3>
        <div style={{fontSize:12, color:'#065f46', marginTop:6, background:'#ecfdf5', padding:8, borderRadius:8, border:'1px solid #a7f3d0'}}>
          ✅ 初始展示 <b>权威大厂库 17 家</b>（华为/腾讯/阿里/字节/百度/小米/美团/京东/网易/拼多多/比亚迪/平安/中兴/大疆/商汤 + <b>Kimi/DeepSeek</b>，含真实介绍、排名与官方招聘链接，来源官网/年报/维基百科 & Fortune中国500强2024），搜索时同时匹配 <b>宣讲会 500 家</b>与<b>参会 64 家</b>的排名/介绍。点击卡片直接看背景，无需跳转。
        </div>
        <div style={{marginTop:10, display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="搜索：华为、腾讯、字节、平安、赢时胜…" style={{border:'none', outline:'none', flex:1}} />
          </div>
          <button onClick={fetchList} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>当前 {list.length} 家 · 点击卡片看企业做什么、规模、招聘链接与背景调查</div>
      </div>

      {detail && (
        <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:10}}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h3 style={{margin:0, display:'flex', alignItems:'center', gap:8}}><Building2 size={18} /> {detail.company_name} {detail.provenance?.verified && <span style={{fontSize:12, background:'#ecfdf5', color:'#065f46', padding:'2px 8px', borderRadius:999, border:'1px solid #a7f3d0'}}>已核验 ✅</span>}</h3>
            <button onClick={()=>setDetail(null)} style={{padding:'6px 10px', borderRadius:8, border:'1px solid #e2e8f0', background:'#fff'}}>关闭</button>
          </div>

          {detail.basic_info?.intro || detail.basic_info?.intro_excerpt ? (
            <div style={{display:'grid', gap:12}}>
              <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                <div style={{fontWeight:700, marginBottom:6, display:'flex', alignItems:'center', gap:6}}>
                  <ShieldCheck size={16} color="#10b981" /> 企业介绍（权威来源）
                  {(detail.basic_info.ranking || detail.ranking) && (detail.basic_info.ranking !== '未上榜' && detail.ranking !== '未上榜') && <span style={{marginLeft:6, background:'#fef3c7', color:'#92400e', padding:'2px 8px', borderRadius:999, fontSize:11, fontWeight:700}}>中国500强 #{detail.basic_info.ranking || detail.ranking} · {detail.basic_info.ranking_source || detail.ranking_source || 'Fortune中国500强2024'}</span>}
                  {(detail.basic_info.ranking === '未上榜' || detail.ranking === '未上榜') && <span style={{background:'#f1f5f9', padding:'2px 8px', borderRadius:999, fontSize:11}}>未上榜 · {detail.basic_info.ranking_source || '500强外'}</span>}
                  {detail.basic_info.ranking && typeof detail.basic_info.ranking === 'string' && detail.basic_info.ranking.includes('独角兽') && <span style={{background:'#ede9fe', color:'#6d28d9', padding:'2px 8px', borderRadius:999, fontSize:11}}>{detail.basic_info.ranking}</span>}
                </div>
                <div style={{fontSize:13, color:'#334155', lineHeight:1.7, whiteSpace:'pre-wrap'}}>{detail.basic_info.intro || detail.basic_info.intro_excerpt}</div>
                {detail.basic_info.products && <div style={{marginTop:8, fontSize:12, color:'#475569'}}><b>主营：</b>{detail.basic_info.products}</div>}
                <div style={{marginTop:8, fontSize:12, color:'#475569', display:'flex', gap:12, flexWrap:'wrap'}}>
                  <span>行业：{detail.basic_info.industry || '—'}</span>
                  <span>规模：{detail.basic_info.scale || '—'}</span>
                  <span>城市：{detail.basic_info.city || '—'}</span>
                  <span>性质：{detail.basic_info.company_property || '—'}</span>
                </div>
                <div style={{marginTop:8, display:'flex', gap:8, flexWrap:'wrap'}}>
                  {detail.basic_info.official_url && <a href={detail.basic_info.official_url} target="_blank" style={{fontSize:12, color:'#1E55AF', border:'1px solid #1E55AF', padding:'6px 12px', borderRadius:999, textDecoration:'none', display:'inline-flex', alignItems:'center', gap:4}}>官网 <ExternalLink size={12}/></a>}
                  {detail.basic_info.recruitment_url && <a href={detail.basic_info.recruitment_url} target="_blank" style={{fontSize:12, color:'#fff', background:'#1E55AF', padding:'6px 12px', borderRadius:999, textDecoration:'none', display:'inline-flex', alignItems:'center', gap:4}}>官方招聘页 <ExternalLink size={12}/></a>}
                </div>
                {detail.basic_info.source && <div style={{marginTop:6, fontSize:11, color:'#94a3b8'}}>来源：{detail.basic_info.source} {detail.provenance?.recruitment_url && `· ${detail.provenance.recruitment_url}`}</div>}
              </div>

              {detail.job_info && (
                <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                  <div style={{fontWeight:700}}>参会岗位信息（真实抓取）</div>
                  <div style={{fontSize:13, color:'#334155', lineHeight:1.6, marginTop:6}}>
                    <div>岗位：{detail.job_info.job_name || '—'} <span style={{marginLeft:8, background:'#eef2ff', padding:'2px 8px', borderRadius:999}}>{detail.job_info.salary || '—'}</span></div>
                    <div style={{display:'flex', gap:10, flexWrap:'wrap', marginTop:6}}>
                      <span style={{display:'flex', alignItems:'center', gap:4}}><Banknote size={14} /> {detail.job_info.salary || '—'}</span>
                      <span style={{display:'flex', alignItems:'center', gap:4}}><GraduationCap size={14} /> {detail.job_info.degree_require || '—'}</span>
                      <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={14} /> {detail.job_info.about_major || '—'}</span>
                    </div>
                    {detail.job_info.benefits?.length>0 && <div style={{marginTop:8, display:'flex', gap:6, flexWrap:'wrap'}}>{detail.job_info.benefits.map((b:string)=><span key={b} style={{background:'#eef2ff', color:'#1E55AF', padding:'2px 8px', borderRadius:999, fontSize:12}}>{b}</span>)}</div>}
                    <div style={{marginTop:8, whiteSpace:'pre-wrap', background:'#fff', padding:8, borderRadius:8, border:'1px solid #e2e8f0'}}><b>要求：</b>{detail.job_info.requirements || '—'}</div>
                    <div style={{marginTop:8, whiteSpace:'pre-wrap', background:'#fff', padding:8, borderRadius:8, border:'1px solid #e2e8f0'}}><b>描述：</b>{detail.job_info.description || '—'}</div>
                  </div>
                </div>
              )}
              {detail.risk_assessment && <div style={{fontSize:12, color:'#475569', background:'#fff7ed', padding:8, borderRadius:8, border:'1px solid #fed7aa'}}>{detail.risk_assessment.suggestion}</div>}
            </div>
          ) : (
            <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
              <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                <div style={{fontWeight:700, marginBottom:6, display:'flex', alignItems:'center', gap:6}}>
                  {detail.risk_assessment?.risk_level==='low' ? <ShieldCheck size={16} color="#10b981" /> : <ShieldAlert size={16} color="#f59e0b" />}
                  风险评估：{detail.risk_assessment?.risk_level}（{detail.risk_assessment?.risk_score}分）
                </div>
                <div style={{fontSize:13, color:'#334155'}}>{detail.risk_assessment?.suggestion}</div>
              </div>
              <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                <div style={{fontWeight:700}}>综合评分：{detail.overall_score ?? '—'} / 5</div>
                <div style={{fontSize:12, color:'#475569', marginTop:6}}>员工评价：{detail.employee_reviews?.overall_rating ?? '—'} 分</div>
              </div>
            </div>
          )}
        </div>
      )}

      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(300px,1fr))', gap:10}}>
        {loading ? <div>加载中…</div> : list.map((c:any)=>(
          <div key={c.name} onClick={()=>open(c.name)} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', cursor:'pointer', display:'grid', gap:6}}>
            <div style={{fontWeight:700, display:'flex', alignItems:'center', gap:6}}><Building2 size={14} /> {c.name} {c.ranking && c.ranking !== '未上榜' && typeof c.ranking === 'number' && <span style={{fontSize:11, background:'#fef3c7', color:'#92400e', padding:'2px 6px', borderRadius:999}}>500强 #{c.ranking}</span>} {c.ranking && typeof c.ranking === 'string' && c.ranking.includes('独角兽') && <span style={{fontSize:11, background:'#ede9fe', color:'#6d28d9', padding:'2px 6px', borderRadius:999}}>{c.ranking}</span>}</div>
            <div style={{fontSize:12, color:'#1E55AF', fontWeight:600}}>{c.intro ? c.intro.slice(0,60) : (c.industry || '')} </div>
            <div style={{fontSize:12, color:'#64748b'}}>{c.industry || '—'} · {c.scale || '—'} · {c.city || ''} {c.verified && '· 已核验✅'}</div>
            <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>{c.official_url && <span style={{fontSize:11, color:'#1E55AF', border:'1px solid #bfdbfe', padding:'2px 6px', borderRadius:999}}>官网</span>}{c.recruitment_url && <span style={{fontSize:11, color:'#065f46', background:'#ecfdf5', padding:'2px 6px', borderRadius:999, border:'1px solid #a7f3d0'}}>招聘</span>}</div>
            <div style={{marginTop:4, fontSize:12, color:'#1E55AF'}}>点击看介绍、排名与招聘链接 →</div>
          </div>
        ))}
        {!loading && list.length===0 && <div style={{color:'#64748b'}}>暂无数据。</div>}
      </div>
    </div>
  )
}
