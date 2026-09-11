import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Careers from './pages/Careers'
import Jobfairs from './pages/Jobfairs'
import Jobs from './pages/Jobs'
import Companies from './pages/Companies'
import Analysis from './pages/Analysis'
import Recommend from './pages/Recommend'
import About from './pages/About'

export default function App(){
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/careers" element={<Careers />} />
          <Route path="/jobfairs" element={<Jobfairs />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/companies" element={<Companies />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/recommend" element={<Recommend />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
