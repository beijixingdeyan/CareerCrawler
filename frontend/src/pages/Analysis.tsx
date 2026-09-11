import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function Analysis(){
  const [trend, setTrend] = useState<any>(null)
  const [salary, setSalary] = useState<any>(null)
  useEffect(()=>{
    api.get('/api/analysis/trend').then(r=>setTrend(r.data))
    api.get('/api/analysis/salary').then(r=>setSalary(r.data))
  },[])
  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>趋势分析 · 面向计科 2027 届</h3>
        <div style={{fontSize:12, color:'#64748b', marginTop:6}}>基于宣讲会/岗位发布时间聚合，预判 9 月为高峰；正式岗与实习岗并行，关注“双选会”落地转化。</div>
      </div>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
        <Card title="发布趋势（按日）">
          {trend ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trend.trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{fontSize:10}} />
                <YAxis />
                <Tooltip />
                <Line dataKey="count" stroke="#1E55AF" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : '加载中…'}
        </Card>
        <Card title="行业（类别）占比">
          {trend ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={Object.entries(trend.industry).map(([name,value])=>({name, value})) as any}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{fontSize:11}} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8b5cf6" radius={[8,8,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : '加载中…'}
        </Card>
      </div>
      <Card title="技能热度排行（计科重点：Java/Python/前后端/数据库/安全/大数据）">
        {salary ? (
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={salary.skill_rank} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="skill" type="category" width={100} tick={{fontSize:12}} />
              <Tooltip />
              <Bar dataKey="count" fill="#06b6d4" radius={[0,8,8,0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : '加载中…'}
      </Card>
      <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', fontSize:13, color:'#334155', lineHeight:1.6}}>
        <b>导出</b>：后端已提供 <code>/api/jobs</code> 与 <code>/api/analysis/*</code> ，可直接以 JSON 导出；前端“岗位广场”支持分页与筛选；后续可扩展 PDF/Excel（前端 jsPDF + 后端 openpyxl）。
      </div>
    </div>
  )
}
function Card(props:{title:string; children:any}){
  return <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}><h3 style={{margin:'0 0 10px'}}>{props.title}</h3>{props.children}</div>
}
