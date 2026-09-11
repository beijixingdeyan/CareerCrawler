import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Search, ShieldAlert, ShieldCheck, Building2 } from 'lucide-react'

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
        <h3 style={{margin:0}}>企业背景调研</h3>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>支持模糊搜索，点击企业进入深度调研（含工商信息、风险评估、舆情与员工评价）。离线启发式可用，后续可接入天眼查/企查查真实 API。</div>
        <div style={{marginTop:10, display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="搜索公司：例 奇安信、华为、字节跳动" style={{border:'none', outline:'none', flex:1}} />
          </div>
          <button onClick={fetchList} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
      </div>

      {detail && (
        <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:10}}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h3 style={{margin:0, display:'flex', alignItems:'center', gap:8}}><Building2 size={18} /> {detail.company_name}</h3>
            <button onClick={()=>setDetail(null)} style={{padding:'6px 10px', borderRadius:8, border:'1px solid #e2e8f0', background:'#fff'}}>关闭</button>
          </div>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
            <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
              <div style={{fontWeight:700, marginBottom:6, display:'flex', alignItems:'center', gap:6}}>
                {detail.risk_assessment?.risk_level==='low' ? <ShieldCheck size={16} color="#10b981" /> : <ShieldAlert size={16} color="#f59e0b" />}
                风险评估：{detail.risk_assessment?.risk_level}（{detail.risk_assessment?.risk_score}分）
              </div>
              <div style={{fontSize:13, color:'#334155'}}>{detail.risk_assessment?.suggestion}</div>
              <div style={{marginTop:8, fontSize:12, color:'#475569'}}>
                <div>行业：{detail.basic_info?.industry} / {detail.basic_info?.sub_industry}</div>
                <div>规模：{detail.basic_info?.staff_count_range}</div>
                <div>状态：{detail.basic_info?.business_status}</div>
                <div>成立：{detail.basic_info?.establishment_date}</div>
              </div>
            </div>
            <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
              <div style={{fontWeight:700}}>综合评分：{detail.overall_score ?? '—'} / 5</div>
              <div style={{fontSize:12, color:'#475569', marginTop:6}}>员工评价参考：{detail.employee_reviews?.overall_rating ?? '—'} 分 · 关键词：{(detail.employee_reviews?.keywords||[]).join(' / ') || '—'}</div>
              <div style={{fontSize:12, color:'#475569', marginTop:6}}>行业前景：{detail.industry_analysis?.prospect ?? '—'} · 参考薪资：{detail.industry_analysis?.avg_salary_reference ?? '—'}</div>
              <div style={{fontSize:12, color:'#64748b', marginTop:8}}>计科建议：{detail.advice_for_cs}</div>
            </div>
          </div>
          <div style={{fontSize:12, color:'#94a3b8'}}>调研时间：{detail.research_time} · 模式：{detail.mode || 'heuristic-offline'} · 真实工商数据待接入 API 后替换</div>
        </div>
      )}

      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))', gap:10}}>
        {loading ? <div>加载中…</div> : list.map((c:any)=>(
          <div key={c.name} onClick={()=>open(c.name)} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', cursor:'pointer'}}>
            <div style={{fontWeight:700, display:'flex', alignItems:'center', gap:6}}><Building2 size={14} /> {c.name}</div>
            <div style={{fontSize:12, color:'#64748b', marginTop:4}}>{c.industry || '—'} · {c.staff_count_range || '—'} · 风险：{c.risk_level || 'unknown'}</div>
            <div style={{marginTop:8, fontSize:12, color:'#1E55AF'}}>点击查看深度调研 →</div>
          </div>
        ))}
        {!loading && list.length===0 && <div style={{color:'#64748b'}}>暂无数据，请尝试刷新或搜索。</div>}
      </div>
    </div>
  )
}
