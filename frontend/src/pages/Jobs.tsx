import { useEffect, useState } from 'react'
import { api, Job } from '../api/client'
import { Search, MapPin, Tag, Building2 } from 'lucide-react'

export default function Jobs(){
  const [q, setQ] = useState('')
  const [category, setCategory] = useState('')
  const [city, setCity] = useState('')
  const [skill, setSkill] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<{total:number; items:Job[]; from?:string} | null>(null)
  const [loading, setLoading] = useState(false)

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
  // 首次
  useEffect(()=>{ fetch() }, [])

  const onSearch = () => { setPage(1); fetch() }

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
        <div style={{fontSize:12, color:'#64748b'}}>数据来源：jy.hnust.edu.cn 宣讲会/岗位/双选会；支持离线样本兜底。点击卡片可查看详情与溯源链接。</div>
      </div>

      {loading ? <div style={{padding:20}}>加载中…</div> : (
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:12}}>
          {data?.items.map(job=>(
            <a key={job.id} href={job.source_url || '#'} target="_blank" rel="noreferrer" style={{textDecoration:'none', color:'inherit'}}>
              <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:8, height:'100%'}}>
                <div style={{fontWeight:800, lineHeight:1.3, display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden'}}>{job.title}</div>
                <div style={{display:'flex', alignItems:'center', gap:6, color:'#334155', fontSize:13}}><Building2 size={14} /> {job.company_name} <span style={{background:'#eef2ff', color:'#1E55AF', padding:'2px 8px', borderRadius:999, fontSize:11}}>{job.category}</span></div>
                <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>
                  {(job.skills||[]).slice(0,5).map(s=>(
                    <span key={s.name} style={{background:'#f1f5f9', padding:'4px 8px', borderRadius:999, fontSize:11, display:'flex', alignItems:'center', gap:4}}><Tag size={10} /> {s.name}</span>
                  ))}
                  {(job.skills||[]).length===0 && <span style={{fontSize:12, color:'#94a3b8'}}>待解析技能</span>}
                </div>
                <div style={{display:'flex', gap:8, flexWrap:'wrap', fontSize:12, color:'#475569'}}>
                  <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={12} /> {job.location_city || job.location_raw || '地点待定'}</span>
                  <span>💰 {job.salary_raw || (job.salary_min ? `${job.salary_min}-${job.salary_max}` : '面议')}</span>
                  {job.publish_date && <span>📅 {job.publish_date}</span>}
                </div>
                {job.description && <div style={{fontSize:12, color:'#64748b', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden'}}>{job.description.slice(0,120)}</div>}
                <div style={{fontSize:11, color:'#94a3b8'}}>来源：{job.source_type || job.source} · 点击溯源</div>
              </div>
            </a>
          ))}
        </div>
      )}
      {data && (
        <div style={{display:'flex', justifyContent:'center', gap:8, alignItems:'center', padding:10}}>
          <button disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))} style={{padding:'8px 12px', borderRadius:10, border:'1px solid #e2e8f0', background:'#fff'}}>上一页</button>
          <span style={{fontSize:13, color:'#475569'}}>第 {page} 页 / 共 {Math.ceil(data.total/12)} 页 · 总计 {data.total} 条 {data.from==='sample' ? '（样本）' : ''}</span>
          <button disabled={page>=Math.ceil(data.total/12)} onClick={()=>setPage(p=>p+1)} style={{padding:'8px 12px', borderRadius:10, border:'1px solid #e2e8f0', background:'#fff'}}>下一页</button>
        </div>
      )}
    </div>
  )
}
