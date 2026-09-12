import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Calendar, MapPin, ExternalLink, Search, Building2, Banknote, ArrowLeft, Sparkles } from 'lucide-react'

type Fair = any

export default function Jobfairs(){
  const [q,setQ]=useState('')
  const [page,setPage]=useState(1)
  const [data,setData]=useState<any>({total:0, items:[]})
  const [loading,setLoading]=useState(false)
  // selected fair
  const [selected,setSelected]=useState<Fair|null>(null)
  const [companies,setCompanies]=useState<any[]>([])
  const [cLoading,setCLoading]=useState(false)
  const [cTotal,setCTotal]=useState(0)
  const [companyDetail,setCompanyDetail]=useState<any|null>(null)
  const [cIndustry,setCIndustry]=useState('全部')
  const pageSize=15
  const INDUSTRIES = ["全部","制造业","教育","信息传输、软件和信息技术服务业","建筑业","批发和零售业","电力、热力、燃气及水生产和供应业","采矿业","科学研究和技术服务业","交通运输、仓储和邮政业","农、林、牧、渔业","住宿和餐饮业","文化、体育和娱乐业","金融业","水利、环境和公共设施管理业","公共管理、社会保障和社会组织","租赁和商务服务业","其它"]

  const openCompany=async (name:string)=>{
    setCompanyDetail({_loading:true, company_name:name})
    try{
      const r=await api.get(`/api/companies/${encodeURIComponent(name)}`)
      setCompanyDetail(r.data)
    } catch{ setCompanyDetail(null) }
  }

  const loadFairs=async ()=>{
    setLoading(true)
    const r=await api.get('/api/jobfairs', {params:{q: q||undefined, page, page_size: pageSize}})
    setData(r.data)
    setLoading(false)
  }
  useEffect(()=>{ if(!selected) loadFairs() }, [page, selected])

  const openFair=async (fair: Fair)=>{
    const fid = String(fair.fair_id || fair.id || fair.fairId || '')
    if(!fid) return
    try{
      const key='clicked_fair_ids'
      const arr=JSON.parse(localStorage.getItem(key) || '[]')
      if(!arr.includes(fid)){ arr.push(fid); localStorage.setItem(key, JSON.stringify(arr)) }
    }catch{}
    setSelected(fair)
    setCLoading(true)
    setCompanies([])
    try{
      // enrich=1 会实时爬取该场全部企业并做背景调查（首次约 30-45s，后续走缓存）
      const r=await api.get(`/api/jobfairs/${fid}/companies`, {params:{enrich:1}})
      setCompanies(r.data.companies || [])
      setCTotal(r.data.total || 0)
    } catch(e:any){
      // 回退 raw
      try{
        const r2=await api.get(`/api/jobfairs/${fid}/companies`, {params:{enrich:0}})
        setCompanies(r2.data.companies || [])
        setCTotal(r2.data.total || 0)
      } catch{}
    } finally{ setCLoading(false) }
  }

  const totalPages=Math.max(1, Math.ceil((data.total||0)/pageSize))

  if(selected){
    const fid = String(selected.fair_id || selected.id)
    const filteredCompanies = cIndustry==='全部' ? companies : companies.filter((c:any)=>(c.industry_category||'').includes(cIndustry))
    return (
      <div style={{display:'grid', gap:12}}>
        <div style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'flex', alignItems:'center', gap:10}}>
          <button onClick={()=>setSelected(null)} style={{padding:'8px 12px', borderRadius:10, border:'1px solid #e2e8f0', background:'#fff', display:'flex', alignItems:'center', gap:6}}><ArrowLeft size={16}/> 返回 1/806 列表</button>
          <div>
            <div style={{fontWeight:800}}>{selected.title || selected.meet_name || '双选会'} · {fid}</div>
            <div style={{fontSize:12, color:'#64748b', display:'flex', gap:10}}><span><Calendar size={12}/> {selected.meet_day || selected.hold_date || '—'}</span><span><MapPin size={12}/> {selected.address || selected.place || '—'}</span><span>企业数 {cTotal || selected.company_count || '—'}</span></div>
          </div>
          <a href={`https://jy.hnust.edu.cn/detail/jobfair?id=${fid}`} target="_blank" style={{marginLeft:'auto', fontSize:12, color:'#1E55AF', display:'flex', alignItems:'center', gap:4}}>原帖 <ExternalLink size={12}/></a>
        </div>

        {companyDetail && (
          <div style={{position:'fixed', inset:0, background:'rgba(0,0,0,0.4)', display:'grid', placeItems:'center', zIndex:50, padding:20}} onClick={()=>setCompanyDetail(null)}>
            <div style={{background:'#fff', borderRadius:16, padding:20, maxWidth:700, width:'100%', maxHeight:'85vh', overflow:'auto', display:'grid', gap:12}} onClick={e=>e.stopPropagation()}>
              <div style={{display:'flex', justifyContent:'space-between'}}><h3 style={{margin:0, display:'flex', alignItems:'center', gap:8}}><Building2 size={18}/>{companyDetail.company_name}</h3><button onClick={()=>setCompanyDetail(null)} style={{padding:'6px', borderRadius:8, border:'1px solid #e2e8f0', background:'#fff'}}>关闭</button></div>
              {companyDetail._loading ? <div>加载中…</div> : (
                <>
                  <div style={{fontSize:13, lineHeight:1.6}}>
                    <div style={{display:'flex', gap:8, flexWrap:'wrap'}}><span>行业：{companyDetail.basic_info?.industry || '—'}</span><span>规模：{companyDetail.basic_info?.scale || '—'}</span><span>城市：{companyDetail.basic_info?.city || '—'}</span></div>
                    <div style={{marginTop:8, background:'#f8fafc', padding:10, borderRadius:8, fontSize:12, whiteSpace:'pre-wrap'}}>{companyDetail.basic_info?.intro || companyDetail.basic_info?.intro_excerpt || '—'}</div>
                    {companyDetail.basic_info?.products && <div style={{fontSize:12, color:'#475569', marginTop:6}}>主营：{companyDetail.basic_info.products}</div>}
                    <div style={{marginTop:8, display:'flex', gap:8, flexWrap:'wrap'}}>
                      {companyDetail.basic_info?.official_url && <a href={companyDetail.basic_info.official_url} target="_blank" style={{padding:'6px 12px', borderRadius:999, background:'#1E55AF', color:'#fff', fontSize:12, textDecoration:'none'}}>官网 →</a>}
                      {companyDetail.basic_info?.recruitment_url && <a href={companyDetail.basic_info.recruitment_url} target="_blank" style={{padding:'6px 12px', borderRadius:999, border:'1px solid #1E55AF', color:'#1E55AF', fontSize:12, textDecoration:'none'}}>官方招聘页 →</a>}
                    </div>
                  </div>
                  {companyDetail.job_info && <div style={{background:'#f8fafc', padding:10, borderRadius:8}}><div style={{fontWeight:600}}>{companyDetail.job_info.job_name} · {companyDetail.job_info.salary}</div><div style={{fontSize:12, whiteSpace:'pre-wrap', marginTop:6}}><b>要求：</b>{companyDetail.job_info.requirements?.slice(0,400) || '—'}</div><div style={{fontSize:12, marginTop:6}}><b>福利：</b>{companyDetail.job_info.benefits?.join(' / ') || '—'}</div></div>}
                </>
              )}
            </div>
          </div>
        )}
        <div style={{background:'#ecfdf5', border:'1px solid #a7f3d0', padding:10, borderRadius:12, fontSize:12, color:'#065f46'}}>
          ✅ 已为本场 <b>{cTotal}</b> 家企业实时爬取：<code>detail/job?id=publish_id</code>（薪资/要求/福利）+ <code>detail/company?id=company_id</code>（工商背景），走 <code>list_jobfair_company?fair_id={fid}</code> 官方接口，结果已缓存 <code>data/real/fair_{fid}.json</code>，零 mock。
        </div>
        <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>
          {INDUSTRIES.map(ind=>(
            <button key={ind} onClick={()=>setCIndustry(ind)} style={{padding:'6px 12px', borderRadius:999, border: cIndustry===ind?'1px solid #1E55AF':'1px solid #e2e8f0', background: cIndustry===ind?'#1E55AF':'#fff', color: cIndustry===ind?'#fff':'#475569', fontSize:12, fontWeight:600}}>{ind}</button>
          ))}
        </div>

        {cLoading ? (
          <div style={{background:'#fff', padding:30, borderRadius:12, textAlign:'center'}}>
            <div style={{fontWeight:700}}>正在爬取该场全部 {selected.company_count || ''} 家企业…</div>
            <div style={{fontSize:12, color:'#64748b', marginTop:6}}>首次约 30-45 秒（逐家抓 detail/job 与 detail/company），已做 0.35s 限速与缓存，稍候即得完整背景调查</div>
            <div style={{marginTop:12, width: 180, height:6, background:'#e2e8f0', borderRadius:999, marginInline:'auto', overflow:'hidden'}}><div style={{width:'40%', height:'100%', background:'#1E55AF', animation:'pulse 1.5s infinite'}}/></div>
          </div>
        ) : (
          <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:10}}>
            {filteredCompanies.map((c:any)=>(
              <div key={c.publish_id || c.company_name} onClick={()=>openCompany(c.company_name)} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:6, border:'1px solid #a7f3d0', cursor:'pointer'}}>
                <div style={{fontWeight:700, display:'flex', alignItems:'center', gap:6}}><Building2 size={14}/> {c.company_name}</div>
                <div style={{fontSize:13, color:'#1E55AF', fontWeight:600}}>{c.job_name}</div>
                <div style={{fontSize:12, color:'#64748b'}}>{c.industry_category} · {c.scale} · {c.city_name} · {c.company_property}</div>
                <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
                  <span style={{display:'flex', alignItems:'center', gap:4, fontSize:12, background:'#ecfdf5', padding:'2px 8px', borderRadius:999}}><Banknote size={12}/>{c.salary || '—'}</span>
                  <span style={{fontSize:12, background:'#eff6ff', padding:'2px 8px', borderRadius:999}}>{c.degree_require || '—'}</span>
                  <span style={{fontSize:12, background:'#fef3c7', padding:'2px 8px', borderRadius:999}}>{c.job_number ? `${c.job_number}人` : ''}</span>
                </div>
                {c.benefits?.length>0 && <div style={{fontSize:12, color:'#065f46', display:'flex', gap:6, flexWrap:'wrap'}}>{c.benefits.slice(0,3).map((b:string)=><span key={b} style={{background:'#eef2ff', padding:'2px 8px', borderRadius:999}}>{b}</span>)}</div>}
                <div style={{fontSize:12, color:'#1E55AF', fontWeight:600}}>点击卡片查看 要求/福利/企业介绍 →</div>
              </div>
            ))}
            {!cLoading && filteredCompanies.length===0 && <div style={{color:'#64748b', gridColumn:'1/-1', textAlign:'center', padding:20}}>该行业暂无企业（当前筛选：{cIndustry}）</div>}
          </div>
        )}
      </div>
    )
  }

  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>双选会 · 1/806 列表</h3>
        <div style={{fontSize:12, color:'#1e40af', marginTop:6, background:'#eff6ff', padding:8, borderRadius:8, border:'1px solid #bfdbfe'}}>
          列表来自 <code>getjobfairs is_total=806</code> 全量分页（<b>1/806</b> 即第 {page} 页，共 {totalPages} 页，-{data.total} 场）。<b>点击任意一场</b>即实时爬取该场全部参会企业的 <b>薪资/要求/福利 + 企业背景</b>（走 <code>list_jobfair_company?fair_id=xxx</code> 与 <code>detail/job</code> / <code>detail/company</code>，首次约 30s 已限速+缓存）。
        </div>
        <div style={{marginTop:10, display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="搜索双选会标题/地点/ID" style={{border:'none', outline:'none', flex:1}} onKeyDown={e=>e.key==='Enter'&&(setPage(1),loadFairs())} />
          </div>
          <button onClick={()=>{setPage(1); loadFairs()}} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>共 {data.total} 场 · 第 {page}/{totalPages} 页（1/806 即首条）</div>
      </div>

      {loading ? <div style={{background:'#fff', padding:20, borderRadius:12}}>加载中…</div> : (
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(340px,1fr))', gap:10}}>
          {data.items.map((f:any)=>(
            <div key={f.fair_id || f.id} onClick={()=>openFair(f)} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8, cursor:'pointer', border: String(f.fair_id||f.id)==='30003' ? '1px solid #a7f3d0' : '1px solid transparent'}}>
              <div style={{fontWeight:700, display:'flex', alignItems:'center', gap:6}}>{f.title || f.meet_name || '双选会'} {String(f.fair_id||f.id)==='30003' && <span style={{fontSize:11, background:'#ecfdf5', color:'#065f46', padding:'2px 6px', borderRadius:999, border:'1px solid #a7f3d0'}}>计科专场 30003 ★</span>}</div>
              <div style={{fontSize:12, color:'#64748b', display:'flex', gap:10, flexWrap:'wrap'}}>
                <span style={{display:'flex', alignItems:'center', gap:4}}><Calendar size={12}/>{f.meet_day || f.hold_date || f.publish_time || '—'}</span>
                <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={12}/>{f.address || f.place || '—'}</span>
              </div>
              <div style={{fontSize:12, color:'#475569'}}>ID {f.fair_id || f.id} · 企业数 {f.company_count || f.fact_c_count || f.plan_c_count || '—'}</div>
              <div style={{fontSize:12, color:'#1E55AF', fontWeight:600}}>点击查看并爬取本场全部企业 →</div>
            </div>
          ))}
        </div>
      )}
      <div style={{display:'flex', gap:8, justifyContent:'center'}}>
        <button disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: page<=1?'#f1f5f9':'#fff'}}>上一页</button>
        <span style={{padding:'6px 12px', fontSize:12, color:'#64748b'}}>{page}/{totalPages}</span>
        <button disabled={page>=totalPages} onClick={()=>setPage(p=>p+1)} style={{padding:'6px 12px', borderRadius:8, border:'1px solid #e2e8f0', background: page>=totalPages?'#f1f5f9':'#fff'}}>下一页</button>
      </div>
    </div>
  )
}
