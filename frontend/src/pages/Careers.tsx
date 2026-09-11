import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Calendar, MapPin, Users, ExternalLink, Search } from 'lucide-react'

export default function Careers(){
  const [q,setQ]=useState('')
  const [page,setPage]=useState(1)
  const [data,setData]=useState<any>({total:0, items:[]})
  const [loading,setLoading]=useState(false)
  const pageSize=12

  const load=async ()=>{
    setLoading(true)
    const r=await api.get('/api/careers', {params:{q: q||undefined, page, page_size: pageSize}})
    setData(r.data)
    setLoading(false)
  }
  useEffect(()=>{ load() }, [page])
  const totalPages=Math.max(1, Math.ceil((data.total||0)/pageSize))

  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>宣讲会 · 500 场真实</h3>
        <div style={{fontSize:12, color:'#065f46', marginTop:6, background:'#ecfdf5', padding:8, borderRadius:8, border:'1px solid #a7f3d0'}}>
          ✅ 直连 <code>jy.hnust.edu.cn/module/getcareers</code> <code>is_total=500</code> 全量分页，已落库 <code>data/real/careers.json</code>，含时间/地点/专业/薪资，零 mock。
        </div>
        <div style={{marginTop:10, display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="搜索宣讲会：公司/主题/地点" style={{border:'none', outline:'none', flex:1}} onKeyDown={e=>e.key==='Enter'&&(setPage(1),load())} />
          </div>
          <button onClick={()=>{setPage(1); load()}} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>共 {data.total} 场 · 第 {page}/{totalPages} 页 · 每页 {pageSize} 条</div>
      </div>

      {loading ? <div style={{background:'#fff', padding:20, borderRadius:12}}>加载中…</div> : (
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:10}}>
          {data.items.map((c:any)=>(
            <div key={c.career_talk_id || c.id} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8}}>
              <div style={{fontWeight:700, fontSize:14, lineHeight:1.4}}>{c.company_name || c.title}</div>
              <div style={{fontSize:12, color:'#1E55AF', fontWeight:600}}>{c.title && c.company_name ? c.title : (c.meet_name || '')}</div>
              <div style={{fontSize:12, color:'#64748b', display:'flex', gap:10, flexWrap:'wrap'}}>
                <span style={{display:'flex', alignItems:'center', gap:4}}><Calendar size={12}/>{c.meet_day || c.publish_time || c.hold_date || '—'}</span>
                <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={12}/>{c.address || c.meet_place || c.city || '—'}</span>
                <span style={{display:'flex', alignItems:'center', gap:4}}><Users size={12}/>{c.professionals || c.majors || '全专业'}</span>
              </div>
              {c.salary && <div style={{fontSize:12, color:'#065f46', background:'#ecfdf5', padding:'4px 8px', borderRadius:999, alignSelf:'start'}}>薪资 {c.salary}</div>}
              <div style={{display:'flex', gap:8, marginTop:4}}>
                <a href={c.detail_url || `https://jy.hnust.edu.cn/detail/career?id=${c.career_talk_id}`} target="_blank" style={{fontSize:12, color:'#1E55AF', display:'flex', alignItems:'center', gap:4}}>查看原帖 <ExternalLink size={12}/></a>
                <span style={{fontSize:12, color:'#94a3b8'}}>ID {c.career_talk_id || c.publish_id || '—'}</span>
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
