import axios from 'axios'

export const api = axios.create({
  baseURL: '',
  timeout: 15000,
})

export type Job = {
  id: string
  title: string
  company_name: string
  category: string
  skills: { name: string; category: string }[]
  salary_raw?: string
  salary_min?: number
  salary_max?: number
  location_raw?: string
  location_city?: string
  source?: string
  source_url?: string
  source_type?: string
  publish_date?: string
  description?: string
  _score?: number
  reasons?: string[]
}

export type Dashboard = {
  total_jobs: number
  total_companies: number
  today_new: number
  avg_salary: number | null
  industry_dist: Record<string, number>
  skill_rank: { skill: string; count: number }[]
  salary_stats: any
  location_dist: Record<string, number>
  trend: { date: string; count: number }[]
  cs_insight: { message: string; focus_skills: string[]; hot_cities: string[] }
  real_counts?: { careers: number; jobfairs: number; jobs: number }
  total_careers?: number
  total_jobfairs?: number
  total_jobs_real?: number
}
