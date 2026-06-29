import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api' })

export const authenticate = (github_token: string, groq_key: string) =>
  api.post('/auth', { github_token, groq_key })

export const listRepos = (github_token: string, groq_key: string) =>
  api.post('/repos', { github_token, groq_key })

export const getContents = (github_token: string, repo_name: string, path = '') =>
  api.post('/repos/contents', { github_token, repo_name, path })

export const pushFile = (data: Record<string, unknown>) => api.post('/push', data)

export const analyzeRepo = (data: Record<string, unknown>) => api.post('/analyze', data)

export const generateReadme = (data: Record<string, unknown>) => api.post('/readme', data)

export const createRepo = (data: Record<string, unknown>) => api.post('/create-repo', data)

export const deleteFile = (data: Record<string, unknown>) => api.post('/delete-file', data)

export const deleteRepo = (data: Record<string, unknown>) => api.post('/delete-repo', data)
