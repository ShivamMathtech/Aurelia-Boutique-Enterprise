import {BrowserRouter,Route,Routes,useLocation} from 'react-router-dom'
import Layout from './components/Layout'
import {AuthProvider} from './context/AuthContext'
import {CartProvider} from './context/CartContext'
import Admin from './pages/Admin'
import Auth from './pages/Auth'
import Cart from './pages/Cart'
import Catalog from './pages/Catalog'
import Home from './pages/Home'
import Orders from './pages/Orders'
import ProductDetail from './pages/ProductDetail'
function AppRoutes(){const location=useLocation();const isAdmin=location.pathname.startsWith('/admin');const content=<Routes><Route path="/" element={<Home/>}/><Route path="/products" element={<Catalog/>}/><Route path="/products/:slug" element={<ProductDetail/>}/><Route path="/login" element={<Auth/>}/><Route path="/cart" element={<Cart/>}/><Route path="/orders" element={<Orders/>}/><Route path="/admin" element={<Admin/>}/></Routes>;return isAdmin?content:<Layout>{content}</Layout>}
export default function App(){return <BrowserRouter><AuthProvider><CartProvider><AppRoutes/></CartProvider></AuthProvider></BrowserRouter>}
