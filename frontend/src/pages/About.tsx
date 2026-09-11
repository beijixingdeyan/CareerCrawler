export default function About(){
  return (
    <div style={{display:'grid', gap:12}}>
      <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>2027届计算机类毕业生专场招聘会 · 说明</h3>
        <div style={{marginTop:10, fontSize:14, color:'#334155', lineHeight:1.7}}>
          <div><b>时间：</b>2026-09-22 14:30—17:00 · <b>地点：</b>湖南科技大学 敏行楼 C212（校园招聘大厅） · <b>截止报名：</b>2026-09-18 23:59</div>
          <div><b>主办：</b>计算机科学与工程学院 · <b>联系：</b>陈老师 17700228142 · <b>官网：</b><a href="https://jy.hnust.edu.cn/detail/jobfair?id=30003" target="_blank" rel="noreferrer">jy.hnust.edu.cn/detail/jobfair?id=30003</a></div>
          <div style={{marginTop:8}}>
            <b>毕业生规模：</b><br/>
            本科 813 人：软件139（男96女43）· 信安129（男85女44）· 物联网116（男92女24）· 大数据131（85/46）· 计科298（206/92）<br/>
            硕士 106 人：软件52（38/14）· 计科27（20/7）· 计技27（18/9）<br/>
            博士 13 人：软件13（7/6）
          </div>
          <div style={{marginTop:8}}>
            <b>参会提示：</b>每单位 1 展位（1桌2椅，门楣统一），限 70 展位按确认顺序分配；海报/易拉宝自备 180×90cm；报到需提交《招聘工作接洽公函》纸质版；提供晚餐盒饭与饮用水；需要笔面试场地请报名时备注（每单位限 1 间）。
          </div>
        </div>
      </div>

      <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)'}}>
        <h3 style={{margin:0}}>本项目如何对接学校就业网</h3>
        <ul style={{fontSize:13, color:'#334155', lineHeight:1.7}}>
          <li><b>真实爬取：</b><code>crawler/engine.py</code> 直连 <code>jy.hnust.edu.cn/module/careers</code> / <code>jobfairs</code> / <code>jobs</code>，含详情页解析与反爬、分页、去重；双选会详情单点 <code>/detail/jobfair?id=30003</code>。</li>
          <li><b>离线可用：</b>若校园网/反爬导致空结果，前端与后端自动回落到 <code>data/samples/</code> 本地样本，保证演示与评审可用。</li>
          <li><b>数据结构化：</b>薪资解析、技能抽取、地点标准化、岗位分类均在爬虫侧完成；<code>company_researcher.py</code> 提供离线启发式企业调研（可替换为天眼查/企查查 API）。</li>
          <li><b>分析与推荐：</b>后端 <code>/api/analysis/dashboard</code> 等提供大屏与趋势；<code>/api/recommend</code> 提供计科画像推荐。</li>
          <li><b>合规：</b>仅抓取公开信息，遵守 robots 与频率控制，敏感信息已脱敏；已在 <code>.gitignore</code> 中忽略需求文档与本地密钥。</li>
        </ul>
        <div style={{marginTop:10, fontSize:12, color:'#64748b'}}>
          启动：后端 <code>python -m uvicorn backend.app.main:app --reload --port 8000</code>；前端 <code>cd frontend && npm i && npm run dev</code>；一键爬取 <code>python scripts/crawl.py --pages 2</code>。
        </div>
      </div>

      <div style={{background:'#fff', borderRadius:16, padding:16, boxShadow:'0 4px 20px rgba(0,0,0,0.06)', fontSize:12, color:'#64748b'}}>
        技术栈：FastAPI + SQLAlchemy(SQLite) + React 18 + Vite + Recharts · 爬虫：Requests + BeautifulSoup + Playwright(可选) · 可 Docker Compose 一键部署（见 <code>docker-compose.yml</code>）。
      </div>
    </div>
  )
}
