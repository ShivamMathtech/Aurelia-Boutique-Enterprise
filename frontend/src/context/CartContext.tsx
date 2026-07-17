import {createContext,useContext,useEffect,useState,type ReactNode} from 'react'
import {api} from '../services/api'
import {useAuth} from './AuthContext'
import type {Cart} from '../types'

const empty:Cart={items:[],subtotal:'0',count:0}
type CartValue={cart:Cart;loading:boolean;refresh:()=>Promise<void>;add:(productId:number,variantId:number,quantity?:number)=>Promise<void>;update:(id:number,quantity:number)=>Promise<void>;remove:(id:number)=>Promise<void>}
const CartContext=createContext<CartValue|null>(null)

export function CartProvider({children}:{children:ReactNode}){
 const{user}=useAuth();const[cart,setCart]=useState(empty);const[loading,setLoading]=useState(false)
 const refresh=async()=>{if(!user){setCart(empty);return}setLoading(true);try{setCart(await api<Cart>('/cart'))}finally{setLoading(false)}}
 useEffect(()=>{void refresh()},[user])
 return <CartContext.Provider value={{
  cart,loading,refresh,
  add:async(productId,variantId,quantity=1)=>setCart(await api<Cart>('/cart/items',{method:'POST',body:JSON.stringify({product_id:productId,variant_id:variantId,quantity})})),
  update:async(id,quantity)=>setCart(await api<Cart>(`/cart/items/${id}`,{method:'PATCH',body:JSON.stringify({quantity})})),
  remove:async id=>setCart(await api<Cart>(`/cart/items/${id}`,{method:'DELETE'})),
 }}>{children}</CartContext.Provider>
}
export function useCart(){const ctx=useContext(CartContext);if(!ctx)throw new Error('CartProvider missing');return ctx}
