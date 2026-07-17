import {createContext,useContext,useEffect,useState,type ReactNode} from 'react'
import {api} from '../services/api'
import type {User} from '../types'

type AuthValue={user:User|null; loading:boolean; login:(email:string,password:string)=>Promise<User>; register:(name:string,email:string,password:string)=>Promise<User>; logout:()=>void}
const AuthContext=createContext<AuthValue|null>(null)
export function AuthProvider({children}:{children:ReactNode}){
 const [user,setUser]=useState<User|null>(null); const [loading,setLoading]=useState(true)
 useEffect(()=>{if(!localStorage.getItem('aurelia_token')){setLoading(false);return} api<User>('/auth/me').then(setUser).catch(()=>localStorage.removeItem('aurelia_token')).finally(()=>setLoading(false))},[])
 async function authenticate(path:string,payload:object){const data=await api<{access_token:string;user:User}>(path,{method:'POST',body:JSON.stringify(payload)});localStorage.setItem('aurelia_token',data.access_token);setUser(data.user);return data.user}
 return <AuthContext.Provider value={{user,loading,login:(email,password)=>authenticate('/auth/login',{email,password}),register:(name,email,password)=>authenticate('/auth/register',{name,email,password}),logout:()=>{localStorage.removeItem('aurelia_token');setUser(null)}}}>{children}</AuthContext.Provider>
}
export function useAuth(){const ctx=useContext(AuthContext);if(!ctx)throw new Error('AuthProvider missing');return ctx}
