import { useEffect, useState } from 'react'
import { api, Job } from '../api/client'
import { Search, MapPin, Tag, Building2, X, Banknote, GraduationCap } from 'lucide-react'

export default function Jobs(){
  const [q, setQ] = useState('')
  const [category, setCategory] = useState('')
  const [city, setCity] = useState('')
  const [skill, setSkill] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<{total:number; items:Job[]; from?:string} | null>(null)
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<any|null>(null)
  const [companyDetail, setCompanyDetail] = useState<any|null>(null)

  const fetch = async () => {
    setLoading(true)
    const params:any = { page, page_size: 12 }
    if (q) params.q = q
    if (category) params.category = category
    if (city) params.city = city
    if (skill) params.skill = skill
    const r = await api.get('/api/jobs', { params })
    setData(r.data)
    setLoading(false)
  }
  useEffect(()=>{ fetch() }, [page])
  useEffect(()=>{ fetch() }, [])

  const onSearch = () => { setPage(1); fetch() }

  const openJob = async (job: Job) => {
    // 尝试取详情（若后端有该岗位的富化数据，会返回 requirements/benefits）
    setDetail({ ...job, _loading: true })
    try{
      const r = await api.get(`/api/jobs/${encodeURIComponent(job.id)}`)
      setDetail(r.data)
    } catch{
      setDetail(job)
    }
  }
  const openCompany = async (name: string) => {
    setCompanyDetail({ _loading: true, company_name: name })
    try{
      const r = await api.get(`/api/companies/${encodeURIComponent(name)}`)
      setCompanyDetail(r.data)
    } catch{
      setCompanyDetail(null)
    }
  }

  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:10}}>
        <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
          <div style={{flex:'1 1 260px', display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="搜索：标题 / 公司 / 关键词（例：Java、算法、安全）" style={{border:'none', outline:'none', flex:1}} />
          </div>
          <select value={category} onChange={e=>setCategory(e.target.value)} style={{padding:'8px 10px', borderRadius:10, border:'1px solid #e2e8f0'}}>
            <option value="">全部分类</option>
            <option value="技术开发">技术开发</option>
            <option value="安全类">安全类</option>
            <option value="产品设计">产品设计</option>
            <option value="运营市场">运营市场</option>
            <option value="其他">其他</option>
          </select>
          <select value={city} onChange={e=>setCity(e.target.value)} style={{padding:'8px 10px', borderRadius:10, border:'1px solid #e2e8f0'}}>
            <option value="">全部城市</option>
            <option value="长沙">长沙</option>
            <option value="湘潭">湘潭</option>
            <option value="深圳">深圳</option>
            <option value="广州">广州</option>
            <option value="北京">北京</option>
            <option value="杭州">杭州</option>
          </select>
          <input value={skill} onChange={e=>setSkill(e.target.value)} placeholder="技能：Python / Java / React" style={{padding:'8px 12px', borderRadius:10, border:'1px solid #e2e8f0', width:160}} />
          <button onClick={onSearch} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
        <div style={{fontSize:12, color:'#64748b'}}>点击岗位卡片直接查看 <b>要求/福利/薪资</b>，点击公司名查看 <b>真实企业背景</b>（权威机构大厂库 + 参会企业审核数据），无需跳转原帖。</div>
      </div>

      {detail && (
        <div style={{position:'fixed', inset:0, background:'rgba(0,0,0,0.4)', display:'grid', placeItems:'center', zIndex:50, padding:20}} onClick={()=>setDetail(null)}>
          <div style={{background:'#fff', borderRadius:16, padding:20, maxWidth:700, width:'100%', maxHeight:'85vh', overflow:'auto', display:'grid', gap:12}} onClick={e=>e.stopPropagation()}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
              <h3 style={{margin:0}}>{detail.title}</h3>
              <button onClick={()=>setDetail(null)} style={{padding:'6px', borderRadius:8, border:'1px solid #e2e8f0', background:'#fff'}}><X size={16}/></button>
            </div>
            <div style={{display:'flex', gap:8, flexWrap:'wrap', fontSize:12, color:'#475569'}}>
              <span style={{display:'flex', alignItems:'center', gap:4}}><Building2 size={12}/><span onClick={()=>openCompany(detail.company_name)} style={{color:'#1E55AF', cursor:'pointer', textDecoration:'underline'}}>{detail.company_name}</span></span>
              <span style={{display:'flex', alignItems:'center', gap:4}}><Banknote size={12}/>{detail.salary_raw || (detail.salary_min ? `${Math.round(detail.salary_min/1000)}K-${Math.round(detail.salary_max/1000)}K` : '面议')}</span>
              <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={12}/>{detail.location_city || detail.location_raw || '地点待定'}</span>
              {detail.publish_date && <span>📅 {detail.publish_date}</span>}
            </div>
            {(detail.skills||[]).length>0 && <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>{detail.skills.map((s:any)=><span key={s.name} style={{background:'#eef2ff', padding:'4px 8px', borderRadius:999, fontSize:12}}>{s.name}</span>)}</div>}
            <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
              <div style={{fontWeight:700}}>岗位要求</div>
              <div style={{fontSize:13, color:'#334155', whiteSpace:'pre-wrap', marginTop:6}}>{detail.requirements || detail.description || '暂无，详见企业背景中的岗位信息'}</div>
            </div>
            <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
              <div style={{fontWeight:700}}>福利待遇</div>
              <div style={{fontSize:13, color:'#334155', marginTop:6}}>{detail.benefits?.join(' / ') || detail.salary_raw || '五险一金、带薪年假等（以企业公布为准）'}</div>
            </div>
            <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
              <div style={{fontWeight:700}}>职位描述</div>
              <div style={{fontSize:13, color:'#334155', whiteSpace:'pre-wrap', marginTop:6}}>{detail.description || '—'}</div>
            </div>
            <div style={{display:'flex', gap:8}}>
              <button onClick={()=>openCompany(detail.company_name)} style={{padding:'8px 14px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:600}}>查看企业真实背景</button>
              {detail.source_url && <a href={detail.source_url} target="_blank" style={{padding:'8px 14px', borderRadius:10, border:'1px solid #e2e8f0', background:'#fff', color:'#1E55AF', textDecoration:'none'}}>原帖（可选）</a>}
            </div>
          </div>
        </div>
      )}

      {companyDetail && (
        <div style={{position:'fixed', inset:0, background:'rgba(0,0,0,0.4)', display:'grid', placeItems:'center', zIndex:51, padding:20}} onClick={()=>setCompanyDetail(null)}>
          <div style={{background:'#fff', borderRadius:16, padding:20, maxWidth:700, width:'100%', maxHeight:'85vh', overflow:'auto', display:'grid', gap:12}} onClick={e=>e.stopPropagation()}>
            <div style={{display:'flex', justifyContent:'space-between'}}><h3 style={{margin:0}}>{companyDetail.company_name}</h3><button onClick={()=>setCompanyDetail(null)} style={{padding:'6px', borderRadius:8, border:'1px solid #e2e8f0', background:'#fff'}}><X size={16}/></button></div>
            {companyDetail._loading ? <div>加载中…</div> : (
              <>
                <div style={{fontSize:13, color:'#334155', lineHeight:1.6}}>
                  <div>行业：{companyDetail.basic_info?.industry || '—'} · 规模：{companyDetail.basic_info?.scale || '—'} · 城市：{companyDetail.basic_info?.city || '—'}</div>
                  <div style={{marginTop:8, background:'#f8fafc', padding:10, borderRadius:8, fontSize:12, whiteSpace:'pre-wrap'}}>{companyDetail.basic_info?.intro || companyDetail.basic_info?.intro_excerpt || '—'}</div>
                  {companyDetail.basic_info?.products && <div style={{marginTop:6, fontSize:12, color:'#475569'}}>主营：{companyDetail.basic_info.products}</div>}
                  {companyDetail.basic_info?.recruitment_url && <a href={companyDetail.basic_info.recruitment_url} target="_blank" style={{fontSize:12, color:'#1E55AF'}}>官方招聘页 →</a>}
                </div>
                {companyDetail.job_info && <div style={{background:'#f8fafc', padding:10, borderRadius:8}}><div style={{fontWeight:600}}>参会岗位 {companyDetail.job_info.job_name} · {companyDetail.job_info.salary}</div><div style={{fontSize:12, whiteSpace:'pre-wrap'}}>{companyDetail.job_info.requirements?.slice(0,300)}</div></div>}
              </>
            )}
          </div>
        </div>
      )}

      {loading ? <div style={{padding:20}}>加载中…</div> : (
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:12}}>
          {data?.items.map(job=>(
            <div key={job.id} onClick={()=>openJob(job)} style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8, cursor:'pointer', border:'1px solid transparent'}}>
              <div style={{fontWeight:800, lineHeight:1.3}}>{job.title}</div>
              <div style={{display:'flex', alignItems:'center', gap:6, color:'#334155', fontSize:13}}>
                <span onClick={(e)=>{e.stopPropagation(); openCompany(job.company_name)}} style={{color:'#1E55AF', textDecoration:'underline', cursor:'pointer', display:'flex', alignItems:'center', gap:4}}><Building2 size={14} />{job.company_name}</span>
                <span style={{background:'#eef2ff', color:'#1E55AF', padding:'2px 8px', borderRadius:999, fontSize:11}}>{job.category}</span>
              </div>
              <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>
                {(job.skills||[]).slice(0,5).map(s=>(
                  <span key={s.name} style={{background:'#f1f5f9', padding:'4px 8px', borderRadius:999, fontSize:11, display:'flex', alignItems:'center', gap:4}}><Tag size={10} /> {s.name}</span>
                ))}
                {(job.skills||[]).length===0 && <span style={{fontSize:12, color:'#94a3b8'}}>点击查看要求与福利 →</span>}
              </div>
              <div style={{display:'flex', gap:8, flexWrap:'wrap', fontSize:12, color:'#475569'}}>
                <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={12} /> {job.location_city || job.location_raw || '地点待定'}</span>
                <span>💰 {job.salary_raw || (job.salary_min ? `${Math.round(job.salary_min/1000)}K-${Math.round((job.salary_max||job.salary_min)/1000)}K` : '面议')}</span>
                {job.publish_date && <span>📅 {job.publish_date.slice(0,10)}</span>}
              </div>
              {job.description && <div style={{fontSize:12, color:'#64748b', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden'}}>{job.description.slice(0,120)}</div>}
              <div style={{fontSize:11, color:'#1E55AF'}}>点击直接查看要求/福利 · 企业背景可点公司名</div>
            </div>
          ))}
        </div>
      )}
      {data && (
        <div style={{display:'flex', justifyContent:'center', gap:8, alignItems:'center', padding:10}}>
          <button disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))} style={{padding:'8px 12px', borderRadius:10, border:'1px solid #e2e8f0', background:'#fff'}}>上一页</button>
          <span style={{fontSize:13, color:'#475569'}}>第 {page} 页 / 共 {Math.ceil(data.total/12)} 页 · 总计 {data.total} 条</span>
          <button disabled={page>=Math.ceil(data.total/12)} onClick={()=>setPage(p=>p+1)} style={{padding:'8px 12px', borderRadius:10, border:'1px solid #e2e8f0', background:'#fff'}}>下一页</button>
        </div>
      )}
    </div>
  )
}
