import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Calendar, MapPin, ExternalLink, Search, Building2, Banknote } from 'lucide-react'

export default function Jobfairs(){
  const [tab,setTab]=useState<'all'|'cs64'>('cs64')
  const [q,setQ]=useState('')
  const [page,setPage]=useState(1)
  const [data,setData]=useState<any>({total:0, items:[]})
  const [cs,setCs]=useState<any>({total:0, companies:[]})
  const [loading,setLoading]=useState(false)
  const pageSize=12

  const loadAll=async ()=>{
    setLoading(true)
    const r=await api.get('/api/jobfairs', {params:{q: q||undefined, page, page_size: pageSize}})
    setData(r.data)
    setLoading(false)
  }
  const loadCs=async ()=>{
    setLoading(true)
    const r=await api.get('/api/jobfairs/30003/companies')
    // 前端分页
    const all=r.data.companies || []
    const filtered=q ? all.filter((x:any)=> (x.company_name+x.job_name).toLowerCase().includes(q.toLowerCase())) : all
    const start=(page-1)*pageSize
    setCs({total: filtered.length, companies: filtered.slice(start, start+pageSize), all: filtered})
    setLoading(false)
  }
  useEffect(()=>{ if(tab==='all') loadAll(); else loadCs() }, [tab, page])

  const total = tab==='all' ? data.total : cs.total
  const totalPages=Math.max(1, Math.ceil(total/pageSize))

  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <div style={{display:'flex', gap:8}}>
          <button onClick={()=>{setTab('cs64'); setPage(1)}} style={{padding:'8px 14px', borderRadius:999, border: tab==='cs64'?'1px solid #1E55AF':'1px solid #e2e8f0', background: tab==='cs64'?'#1E55AF':'#fff', color: tab==='cs64'?'#fff':'#111', fontWeight:700}}>计科专场 64 家 ★</button>
          <button onClick={()=>{setTab('all'); setPage(1)}} style={{padding:'8px 14px', borderRadius:999, border: tab==='all'?'1px solid #1E55AF':'1px solid #e2e8f0', background: tab==='all'?'#1E55AF':'#fff', color: tab==='all'?'#fff':'#111', fontWeight:700}}>全校双选会 806 场</button>
        </div>
        <div style={{fontSize:12, marginTop:8, background: tab==='cs64'?'#ecfdf5':'#eff6ff', padding:8, borderRadius:8, border: tab==='cs64'?'1px solid #a7f3d0':'1px solid #bfdbfe', color: tab==='cs64'?'#065f46':'#1e40af'}}>
          {tab==='cs64' ? (
            <>✅ 计科专场 <b>64</b> 家来自 <code>list_jobfair_company?fair_id=30003</code>，每家已抓 <code>detail/job</code> 薪资/要求/福利 + <code>detail/company</code> 背景，零 mock。点击岗位可跳原帖。</>
          ) : (
            <>全校双选会 <b>806</b> 场来自 <code>getjobfairs is_total=806</code> 全量，分页浏览。</>
          )}
        </div>
        <div style={{marginTop:10, display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder={tab==='cs64' ? "搜索64家里：公司/岗位" : "搜索双选会：标题/地点"} style={{border:'none', outline:'none', flex:1}} onKeyDown={e=>e.key==='Enter'&&(setPage(1), tab==='all'?loadAll():loadCs())} />
          </div>
          <button onClick={()=>{setPage(1); tab==='all'?loadAll():loadCs()}} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>共 {total} 条 · 第 {page}/{totalPages} 页</div>
      </div>

      {loading ? <div style={{background:'#fff', padding:20, borderRadius:12}}>加载中…</div> : (
        tab==='all' ? (
          <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:10}}>
            {data.items.map((f:any)=>(
              <div key={f.fair_id || f.id} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8}}>
                <div style={{fontWeight:700}}>{f.title || f.meet_name || '双选会'}</div>
                <div style={{fontSize:12, color:'#64748b', display:'flex', gap:10, flexWrap:'wrap'}}>
                  <span style={{display:'flex', alignItems:'center', gap:4}}><Calendar size={12}/>{f.meet_day || f.hold_date || '—'}</span>
                  <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={12}/>{f.address || f.place || '—'}</span>
                </div>
                <div style={{fontSize:12, color:'#475569'}}>参会企业数 {f.company_count || f.fact_c_count || '—'}</div>
                <a href={`https://jy.hnust.edu.cn/detail/jobfair?id=${f.fair_id || f.id}`} target="_blank" style={{fontSize:12, color:'#1E55AF', display:'flex', alignItems:'center', gap:4}}>查看原帖 <ExternalLink size={12}/></a>
              </div>
            ))}
          </div>
        ) : (
          <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:10}}>
            {cs.companies.map((c:any)=>(
              <div key={c.publish_id} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:6, border:'1px solid #a7f3d0'}}>
                <div style={{fontWeight:700, display:'flex', alignItems:'center', gap:6}}><Building2 size={14}/> {c.company_name}</div>
                <div style={{fontSize:13, color:'#1E55AF', fontWeight:600}}>{c.job_name}</div>
                <div style={{fontSize:12, color:'#64748b'}}>{c.industry_category} · {c.scale} · {c.city_name}</div>
                <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
                  <span style={{display:'flex', alignItems:'center', gap:4, fontSize:12, background:'#ecfdf5', padding:'2px 8px', borderRadius:999}}><Banknote size={12}/>{c.salary || '—'}</span>
                  <span style={{fontSize:12, background:'#eff6ff', padding:'2px 8px', borderRadius:999}}>{c.degree_require || '—'}</span>
                </div>
                {c.job_detail?.benefits_parsed?.length>0 && <div style={{fontSize:12, color:'#065f46'}}>福利：{c.job_detail.benefits_parsed.slice(0,3).join(' / ')}</div>}
                <div style={{fontSize:12, color:'#475569', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{(c.job_detail?.sections?.['岗位要求'] || c.requirements || '').slice(0,60) || '—'}</div>
                <a href={c.job_detail?.detail_url || `https://jy.hnust.edu.cn/detail/job?id=${c.publish_id}`} target="_blank" style={{fontSize:12, color:'#1E55AF', display:'flex', alignItems:'center', gap:4}}>查看岗位原帖 <ExternalLink size={12}/></a>
              </div>
            ))}
          </div>
        )
      )}
      <div style={{display:'flex', gap:8, justifyContent:'center'}}>
        <button disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: page<=1?'#f1f5f9':'#fff'}}>上一页</button>
        <span style={{padding:'6px 12px', fontSize:12, color:'#64748b'}}>{page}/{totalPages}</span>
        <button disabled={page>=totalPages} onClick={()=>setPage(p=>p+1)} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: page>=totalPages?'#f1f5f9':'#fff'}}>下一页</button>
      </div>
    </div>
  )
}
