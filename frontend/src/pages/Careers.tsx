import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Calendar, MapPin, Users, ExternalLink, Search, X, Building2 } from 'lucide-react'

export default function Careers(){
  const [q,setQ]=useState('')
  const [page,setPage]=useState(1)
  const [data,setData]=useState<any>({total:0, items:[]})
  const [loading,setLoading]=useState(false)
  const [companyDetail,setCompanyDetail]=useState<any|null>(null)
  const pageSize=12

  const load=async ()=>{
    setLoading(true)
    const r=await api.get('/api/careers', {params:{q: q||undefined, page, page_size: pageSize}})
    setData(r.data)
    setLoading(false)
  }
  useEffect(()=>{ load() }, [page])
  const totalPages=Math.max(1, Math.ceil((data.total||0)/pageSize))

  const openCompany=async (name:string)=>{
    setCompanyDetail({_loading:true, company_name:name})
    try{
      const r=await api.get(`/api/companies/${encodeURIComponent(name)}`)
      setCompanyDetail(r.data)
    } catch{ setCompanyDetail(null) }
  }

  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>宣讲会 · 500 场真实</h3>
        <div style={{fontSize:12, color:'#065f46', marginTop:6, background:'#ecfdf5', padding:8, borderRadius:8, border:'1px solid #a7f3d0'}}>
          ✅ 直连 <code>getcareers is_total=500</code> 全量，点击公司名直接看 <b>真实企业背景</b>（权威大厂库 + 参会审核），无需跳转原帖。
        </div>
        <div style={{marginTop:10, display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="搜索宣讲会：公司/主题/地点" style={{border:'none', outline:'none', flex:1}} onKeyDown={e=>e.key==='Enter'&&(setPage(1),load())} />
          </div>
          <button onClick={()=>{setPage(1); load()}} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>共 {data.total} 场 · 第 {page}/{totalPages} 页 · 点击公司名看背景</div>
      </div>

      {companyDetail && (
        <div style={{position:'fixed', inset:0, background:'rgba(0,0,0,0.4)', display:'grid', placeItems:'center', zIndex:50, padding:20}} onClick={()=>setCompanyDetail(null)}>
          <div style={{background:'#fff', borderRadius:16, padding:20, maxWidth:700, width:'100%', maxHeight:'85vh', overflow:'auto', display:'grid', gap:12}} onClick={e=>e.stopPropagation()}>
            <div style={{display:'flex', justifyContent:'space-between'}}><h3 style={{margin:0, display:'flex', alignItems:'center', gap:8}}><Building2 size={18}/>{companyDetail.company_name}</h3><button onClick={()=>setCompanyDetail(null)} style={{padding:'6px', borderRadius:8, border:'1px solid #e2e8f0', background:'#fff'}}><X size={16}/></button></div>
            {companyDetail._loading ? <div>加载中…</div> : (
              <>
                <div style={{fontSize:13, lineHeight:1.6}}>
                  <div>行业：{companyDetail.basic_info?.industry || '—'} · 规模：{companyDetail.basic_info?.scale || '—'} · 城市：{companyDetail.basic_info?.city || '—'}</div>
                  <div style={{marginTop:8, background:'#f8fafc', padding:10, borderRadius:8, fontSize:12, whiteSpace:'pre-wrap'}}>{companyDetail.basic_info?.intro || companyDetail.basic_info?.intro_excerpt || '—'}</div>
                  {companyDetail.basic_info?.products && <div style={{fontSize:12, color:'#475569', marginTop:6}}>主营：{companyDetail.basic_info.products}</div>}
                  {companyDetail.basic_info?.recruitment_url && <a href={companyDetail.basic_info.recruitment_url} target="_blank" style={{fontSize:12, color:'#1E55AF'}}>官方招聘页 →</a>}
                </div>
                {companyDetail.job_info && <div style={{background:'#f8fafc', padding:10, borderRadius:8}}><div style={{fontWeight:600}}>{companyDetail.job_info.job_name} · {companyDetail.job_info.salary}</div><div style={{fontSize:12, marginTop:6, whiteSpace:'pre-wrap'}}><b>要求：</b>{companyDetail.job_info.requirements?.slice(0,400) || '—'}</div><div style={{fontSize:12, marginTop:6}}><b>福利：</b>{companyDetail.job_info.benefits?.join(' / ') || '—'}</div></div>}
              </>
            )}
          </div>
        </div>
      )}

      {loading ? <div style={{background:'#fff', padding:20, borderRadius:12}}>加载中…</div> : (
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:10}}>
          {data.items.map((c:any)=>(
            <div key={c.career_talk_id || c.id} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8}}>
              <div onClick={()=>openCompany(c.company_name)} style={{fontWeight:700, fontSize:14, color:'#1E55AF', cursor:'pointer', textDecoration:'underline'}}>{c.company_name || c.title}</div>
              <div style={{fontSize:12, color:'#1E55AF', fontWeight:600}}>{c.title && c.company_name ? c.title : (c.meet_name || '')}</div>
              <div style={{fontSize:12, color:'#64748b', display:'flex', gap:10, flexWrap:'wrap'}}>
                <span style={{display:'flex', alignItems:'center', gap:4}}><Calendar size={12}/>{c.meet_day || c.publish_time || '—'}</span>
                <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={12}/>{c.address || c.meet_place || '—'}</span>
                <span style={{display:'flex', alignItems:'center', gap:4}}><Users size={12}/>{c.professionals || '全专业'}</span>
              </div>
              {c.salary && <div style={{fontSize:12, color:'#065f46', background:'#ecfdf5', padding:'4px 8px', borderRadius:999, alignSelf:'start'}}>薪资 {c.salary}</div>}
              <div style={{display:'flex', gap:8, marginTop:4}}>
                <button onClick={()=>openCompany(c.company_name)} style={{fontSize:12, color:'#fff', background:'#1E55AF', border:'none', padding:'4px 10px', borderRadius:999, fontWeight:600}}>查看企业背景 →</button>
                <a href={c.detail_url || `https://jy.hnust.edu.cn/detail/career?id=${c.career_talk_id}`} target="_blank" style={{fontSize:12, color:'#64748b'}}>原帖</a>
              </div>
            </div>
          ))}
        </div>
      )}
      <div style={{display:'flex', gap:8, justifyContent:'center', marginTop:4}}>
        <button disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: page<=1?'#f1f5f9':'#fff'}}>上一页</button>
        <span style={{padding:'6px 12px', fontSize:12, color:'#64748b'}}>{page}/{totalPages}</span>
        <button disabled={page>=totalPages} onClick={()=>setPage(p=>p+1)} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: page>=totalPages?'#f1f5f9':'#fff'}}>下一页</button>
      </div>
    </div>
  )
}
