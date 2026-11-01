const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
export function getToken(){ return localStorage.getItem('sc_token') }
async function request(path, options={}) {
  const headers = {...(options.body instanceof FormData ? {} : {'Content-Type':'application/json'}), ...(options.headers||{})}
  if(getToken()) headers.Authorization = `Bearer ${getToken()}`
  const res = await fetch(`${BASE}${path}`, {...options, headers})
  const data = res.status===204 ? null : await res.json().catch(()=>({detail:'Unexpected server response'}))
  if(!res.ok) throw new Error(data?.detail || `Request failed (${res.status})`)
  return data
}
export const api = {
  register: (payload)=>request('/auth/register',{method:'POST',body:JSON.stringify(payload)}),
  login: (payload)=>request('/auth/login',{method:'POST',body:JSON.stringify(payload)}),
  me: ()=>request('/auth/me'),
  complaints: ()=>request('/complaints'),
  createComplaint: (form)=>request('/complaints',{method:'POST',body:form}),
  updateComplaint: (id,payload)=>request(`/complaints/${id}`,{method:'PATCH',body:JSON.stringify(payload)}),
  stats: ()=>request('/stats')
}
