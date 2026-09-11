import { Link, useLocation } from 'react-router-dom'
import { GraduationCap, LayoutDashboard, Briefcase, Building2, LineChart, Sparkles, Info, Calendar, Users } from 'lucide-react'

const nav = [
  { to: '/', label: '数据大屏', icon: LayoutDashboard },
  { to: '/careers', label: '宣讲会 500', icon: Calendar },
  { to: '/jobfairs', label: '双选会 64/806', icon: Users },
  { to: '/jobs', label: '岗位广场', icon: Briefcase },
  { to: '/companies', label: '企业库', icon: Building2 },
  { to: '/analysis', label: '趋势分析', icon: LineChart },
  { to: '/recommend', label: '智能推荐', icon: Sparkles },
  { to: '/about', label: '专场说明', icon: Info },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const loc = useLocation()
  return (
    <div style={{ minHeight: '100vh', background: '#f6f7f9', color: '#111' }}>
      <header style={{ background: 'linear-gradient(135deg,#1E55AF 0%,#2a7ae2 100%)', color: '#fff', position: 'sticky', top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#fff', textDecoration: 'none' }}>
            <div style={{ background: '#fff', color: '#1E55AF', width: 36, height: 36, borderRadius: 10, display: 'grid', placeItems: 'center' }}><GraduationCap size={22} /></div>
            <div>
              <div style={{ fontWeight: 800, letterSpacing: 0.5 }}>CareerCrawler</div>
              <div style={{ fontSize: 12, opacity: 0.9, marginTop: -2 }}>湖南科技大学 · 计算机学院 2027届专场 · 爬取机会，洞察未来</div>
            </div>
          </Link>
          <nav style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {nav.map(n => {
              const active = loc.pathname === n.to || (n.to !== '/' && loc.pathname.startsWith(n.to))
              const Icon = n.icon
              return (
                <Link key={n.to} to={n.to} style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  padding: '8px 12px', borderRadius: 10,
                  background: active ? 'rgba(255,255,255,0.18)' : 'transparent',
                  color: '#fff', textDecoration: 'none', fontSize: 14, fontWeight: active ? 700 : 500,
                  border: active ? '1px solid rgba(255,255,255,0.25)' : '1px solid transparent'
                }}>
                  <Icon size={16} /> {n.label}
                </Link>
              )
            })}
          </nav>
        </div>
        <div style={{ background: 'rgba(0,0,0,0.12)', padding: '6px 20px', fontSize: 12, textAlign: 'center' }}>
          专场时间：2026-09-22 14:30 · 地点：敏行楼 C212 · 报名截止：09-18 23:59 · 本项目已对接 jy.hnust.edu.cn 真实爬取 + 本地样本兜底，保证离线可用
        </div>
      </header>
      <main style={{ maxWidth: 1280, margin: '0 auto', padding: '20px' }}>
        {children}
      </main>
      <footer style={{ textAlign: 'center', padding: '18px 12px', color: '#666', fontSize: 12 }}>
        © {new Date().getFullYear()} CareerCrawler · 湖南科技大学 · 计科专业定制 · 数据来源：jy.hnust.edu.cn · 仅供学习展示，已做去隐私处理
      </footer>
    </div>
  )
}
