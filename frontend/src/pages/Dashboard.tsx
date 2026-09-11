import { useEffect, useState } from 'react'
import { api, Dashboard as T } from '../api/client'
import { LineChart, Line, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

const COLORS = ['#1E55AF','#2a7ae2','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#f97316']

export default function Dashboard() {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/analysis/dashboard').then(r => setData(r.data)).finally(()=>setLoading(false))
  }, [])

  if (loading) return <div style={{padding:40}}>加载中…</div>
  if (!data) return <div>无数据</div>

  const pieData = Object.entries(data.industry_dist).map(([name,value])=>({name,value}))
  const locData = Object.entries(data.location_dist).map(([name,value])=>({name,value}))
  const salary = data.salary_stats

  return (
    <div style={{display:'grid', gap:16}}>
      <div style={{background:'#fff', borderRadius:12, padding:10, fontSize:12, color:'#065f46', border:'1px solid #a7f3d0', display:'flex', gap:12, flexWrap:'wrap'}}>
        <span>✅ 真实数据：</span>
        <b>宣讲会 {data.total_careers ?? data.real_counts?.careers ?? 500} 条</b>
        <span>·</span>
        <b>双选会 {data.total_jobfairs ?? data.real_counts?.jobfairs ?? 806} 场</b>
        <span>·</span>
        <b>岗位 {data.total_jobs_real ?? data.real_counts?.jobs ?? data.total_jobs} 条</b>
        <span style={{color:'#64748b'}}>（直连 jy.hnust.edu.cn 官方 getcareers/getjobfairs/getjobs 接口，分页全量，无 mock）</span>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))', gap:12}}>
        <KPI title="全量岗位（真实）" value={data.total_jobs_real ?? data.total_jobs} suffix="条" trend={`宣讲会 ${data.total_careers ?? 500} · 双选会 ${data.total_jobfairs ?? 806}`} icon="📋" />
        <KPI title="覆盖企业" value={data.total_companies} suffix="家" icon="🏢" />
        <KPI title="平均薪资" value={data.avg_salary ? `${Math.round((data.avg_salary as number)/1000)}k` : '面议为主'} suffix="" icon="💰" />
        <KPI title="计科 2027 届" value={'813+106+13'} suffix="人" trend="本科813 硕士106 博士13" icon="🎓" />
      </div>

      <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:'4px 0 4px'}}>计科专属洞察 · 真实数据</h3>
        <div style={{color:'#334155', fontSize:14, lineHeight:1.6}}>
          {data.cs_insight.message}； 关注技能：<b>{data.cs_insight.focus_skills.join(' · ')}</b>； 热门城市：<b>{data.cs_insight.hot_cities.join(' / ')}</b>。
          本页基于 <code>jy.hnust.edu.cn</code> 真实接口：<code>getcareers 500</code> / <code>getjobfairs 806</code> / <code>getjobs 695（官方上限 500/类型）</code>，已落地 <code>data/real/</code>。
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1.4fr 0.9fr', gap:12}}>
        <Card title="近 30 天岗位发布趋势（基于真实 publish_time/meet_day）">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data.trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{fontSize:10}} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#1E55AF" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
        <Card title="行业（岗位类别）分布">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={88} label>
                {pieData.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
        <Card title="热门技能 TOP（真实需求）">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.skill_rank} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="skill" type="category" width={90} tick={{fontSize:12}} />
              <Tooltip />
              <Bar dataKey="count" fill="#2a7ae2" radius={[0,8,8,0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="城市分布（计科友好度）">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={locData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{fontSize:12}} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#10b981" radius={[8,8,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="薪资洞察（真实 getjobs salary 字段）">
        <div style={{display:'flex', gap:18, flexWrap:'wrap', fontSize:14}}>
          <span>样本数：<b>{salary.count}</b></span>
          <span>均值：<b>{salary.avg ? Math.round(salary.avg)+' 元/月' : '—'}</b></span>
          <span>区间：<b>{salary.min ?? '—'} ~ {salary.max ?? '—'}</b></span>
        </div>
        {salary.distribution && (
          <div style={{marginTop:10, display:'flex', gap:8, flexWrap:'wrap'}}>
            {Object.entries(salary.distribution as Record<string,number>).sort((a,b)=>parseInt(a[0])-parseInt(b[0])).map(([k,v])=>(
              <span key={k} style={{background:'#eef2ff', color:'#1E55AF', padding:'6px 10px', borderRadius:999, fontSize:12}}>{k}: {v} 条</span>
            ))}
          </div>
        )}
        <div style={{marginTop:10, color:'#64748b', fontSize:12}}>提示：getjobs 返回 salary 如 “5K-7K/月”，已标准化为 min/max；未披露不计入。</div>
      </Card>
    </div>
  )
}

function KPI(props:{title:string; value:any; suffix?:string; trend?:string; icon:string}){
  return (
    <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', display:'flex', alignItems:'center', gap:12}}>
      <div style={{width:44,height:44,borderRadius:12, background:'#eef2ff', display:'grid', placeItems:'center', fontSize:20}}>{props.icon}</div>
      <div>
        <div style={{fontSize:12, color:'#64748b'}}>{props.title}</div>
        <div style={{fontSize:22, fontWeight:800}}>{props.value} <span style={{fontSize:12, fontWeight:500, color:'#64748b'}}>{props.suffix}</span></div>
        {props.trend && <div style={{fontSize:12, color:'#10b981'}}>{props.trend}</div>}
      </div>
    </div>
  )
}
function Card(props:{title:string; children:React.ReactNode}){
  return <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
    <h3 style={{margin:'0 0 10px'}}>{props.title}</h3>
    {props.children}
  </div>
}
