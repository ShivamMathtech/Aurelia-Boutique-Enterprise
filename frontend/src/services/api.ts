const API_URL=import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1'
export class ApiError extends Error{constructor(public status:number,message:string){super(message)}}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const token=localStorage.getItem('aurelia_token');const headers=new Headers(options.headers)
 if(!(options.body instanceof FormData))headers.set('Content-Type','application/json')
 if(token)headers.set('Authorization',`Bearer ${token}`)
 const response=await fetch(`${API_URL}${path}`,{...options,headers})
 if(!response.ok){let detail='Request failed';try{const body=await response.json();detail=body.detail||detail}catch{}throw new ApiError(response.status,detail)}
 if(response.status===204)return undefined as T
 return response.json()
}
