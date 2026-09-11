import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Search, ShieldAlert, ShieldCheck, Building2, MapPin, Banknote, GraduationCap } from 'lucide-react'

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
        <h3 style={{margin:0}}>企业背景调研 · 真实数据</h3>
        <div style={{fontSize:12, color:'#065f46', marginTop:6, background:'#ecfdf5', padding:8, borderRadius:8, border:'1px solid #a7f3d0'}}>
          ✅ 64 家来自 <b>湖南科技大学2027届计算机类专场招聘会（fair_id 30003）</b> 官方接口 <code>list_jobfair_company</code>，每家均已抓取 <code>detail/job?id=publish_id</code> 的薪资/要求/福利与 <code>detail/company?id=company_id</code> 企业背景，无 mock。
        </div>
        <div style={{marginTop:10, display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', alignItems:'center', gap:8, border:'1px solid #e2e8f0', borderRadius:12, padding:'8px 12px'}}>
            <Search size={16} />
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="搜索64家中：例 赢时胜、平安、联域光电" style={{border:'none', outline:'none', flex:1}} />
          </div>
          <button onClick={fetchList} style={{padding:'8px 16px', borderRadius:10, background:'#1E55AF', color:'#fff', border:'none', fontWeight:700}}>搜索</button>
        </div>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>当前展示 {list.length} 家参会岗位（64 条岗位 = 64 行），点击卡片查看薪资、要求、福利与企业工商背景。</div>
      </div>

      {detail && (
        <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'grid', gap:10}}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h3 style={{margin:0, display:'flex', alignItems:'center', gap:8}}><Building2 size={18} /> {detail.company_name} {detail.fair_id && <span style={{fontSize:12, background:'#ecfdf5', color:'#065f46', padding:'2px 8px', borderRadius:999, border:'1px solid #a7f3d0'}}>fair 30003 已核验</span>}</h3>
            <button onClick={()=>setDetail(null)} style={{padding:'6px 10px', borderRadius:8, border:'1px solid #e2e8f0', background:'#fff'}}>关闭</button>
          </div>

          {detail.fair_id ? (
            <div style={{display:'grid', gap:12}}>
              <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
                <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                  <div style={{fontWeight:700, marginBottom:6, display:'flex', alignItems:'center', gap:6}}>
                    {detail.risk_assessment?.verified ? <ShieldCheck size={16} color="#10b981" /> : <ShieldAlert size={16} color="#f59e0b" />}
                    企业背景（官方审核）
                  </div>
                  <div style={{fontSize:13, color:'#334155', lineHeight:1.6}}>
                    <div>行业：{detail.basic_info?.industry || '—'} {detail.basic_info?.company_property? `· ${detail.basic_info.company_property}`:''}</div>
                    <div>规模：{detail.basic_info?.scale || '—'} · 城市：{detail.basic_info?.city || '—'}</div>
                    <div>浏览：{detail.basic_info?.view_count || '—'} 次</div>
                    {detail.basic_info?.intro_excerpt && <div style={{marginTop:8, background:'#fff', padding:8, borderRadius:8, border:'1px solid #e2e8f0', fontSize:12, color:'#475569', maxHeight:120, overflow:'auto'}}>{detail.basic_info.intro_excerpt.slice(0,600)}</div>}
                  </div>
                </div>
                <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                  <div style={{fontWeight:700}}>岗位信息（真实抓取）</div>
                  <div style={{fontSize:13, color:'#334155', lineHeight:1.6, marginTop:6}}>
                    <div>岗位：{detail.job_info?.job_name || '—'} <a href={detail.job_info?.detail_url} target="_blank" style={{fontSize:12, color:'#1E55AF'}}>查看原帖</a></div>
                    <div style={{display:'flex', gap:10, flexWrap:'wrap', marginTop:6}}>
                      <span style={{display:'flex', alignItems:'center', gap:4}}><Banknote size={14} /> {detail.job_info?.salary || '—'}</span>
                      <span style={{display:'flex', alignItems:'center', gap:4}}><GraduationCap size={14} /> {detail.job_info?.degree_require || '—'}</span>
                      <span style={{display:'flex', alignItems:'center', gap:4}}><MapPin size={14} /> {detail.job_info?.about_major || '—'}</span>
                    </div>
                    <div>招聘人数：{detail.job_info?.job_number || '—'}</div>
                    {detail.job_info?.benefits?.length>0 && <div style={{marginTop:8}}>福利：{detail.job_info.benefits.map((b:string)=> <span key={b} style={{background:'#eef2ff', color:'#1E55AF', padding:'2px 8px', borderRadius:999, fontSize:12, marginRight:6}}>{b}</span>)}</div>}
                  </div>
                </div>
              </div>
              <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                <div style={{fontWeight:700}}>要求</div>
                <div style={{fontSize:13, color:'#334155', whiteSpace:'pre-wrap', marginTop:6}}>{detail.job_info?.requirements || '详见原帖'}</div>
              </div>
              <div style={{background:'#f8fafc', borderRadius:12, padding:12}}>
                <div style={{fontWeight:700}}>职位描述</div>
                <div style={{fontSize:13, color:'#334155', whiteSpace:'pre-wrap', marginTop:6}}>{detail.job_info?.description || detail.job_info?.sections?.['职位描述'] || '详见原帖'}</div>
              </div>
              <div style={{fontSize:12, color:'#94a3b8'}}>来源：{detail.provenance?.api} · 岗位详情：{detail.provenance?.job_detail_url} · 企业详情：{detail.provenance?.company_detail_url} · 已验证 {detail.provenance?.verified ? '✅' : '—'}</div>
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

      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))', gap:10}}>
        {loading ? <div>加载中…</div> : list.map((c:any)=>(
          <div key={c.publish_id || c.name} onClick={()=>open(c.name)} style={{background:'#fff', borderRadius:14, padding:14, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', cursor:'pointer', border: c.from==='fair30003_real'?'1px solid #a7f3d0':undefined}}>
            <div style={{fontWeight:700, display:'flex', alignItems:'center', gap:6}}><Building2 size={14} /> {c.name}</div>
            <div style={{fontSize:12, color:'#1E55AF', marginTop:4, fontWeight:600}}>{c.job_name || ''} {c.salary? `· ${c.salary}`:''}</div>
            <div style={{fontSize:12, color:'#64748b', marginTop:4}}>{c.industry || '—'} · {c.scale || c.staff_count_range || '—'} · {c.city || ''} {c.from==='fair30003_real' && '· 已核验✅'}</div>
            <div style={{marginTop:8, fontSize:12, color:'#1E55AF'}}>点击查看薪资/要求/福利与企业背景 →</div>
          </div>
        ))}
        {!loading && list.length===0 && <div style={{color:'#64748b'}}>暂无数据。</div>}
      </div>
    </div>
  )
}
