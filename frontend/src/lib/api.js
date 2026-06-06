import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api' })

export const authenticate = (github_token, groq_key) =>
  api.post('/auth', { github_token, groq_key })

export const listRepos = (github_token, groq_key) =>
  api.post('/repos', { github_token, groq_key })

export const getContents = (github_token, repo_name, path = '') =>
  api.post('/repos/contents', { github_token, repo_name, path })

export const pushFile = (data) => api.post('/push', data)

export const analyzeRepo = (data) => api.post('/analyze', data)

export const generateReadme = (data) => api.post('/readme', data)

export const createRepo = (data) => api.post('/create-repo', data)
export const deleteFile = (data) => api.post('/delete-file', data)
export const deleteRepo = (data) => api.post('/delete-repo', data)
