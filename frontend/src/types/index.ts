export type User = {id:number;name:string;email:string;role:'customer'|'admin';is_active:boolean}
export type Category = {id:number;name:string;slug:string;description:string;image_url:string;is_active:boolean}
export type Variant = {id:number;sku:string;size:string;color:string;stock:number;additional_price:string;is_active:boolean}
export type Product = {id:number;title:string;slug:string;brand:string;sku:string;description:string;fabric:string;fit:string;care_instructions:string;occasion:string;price:string;compare_at_price?:string|null;stock:number;image_url:string;gallery_urls:string;vendor:string;weight_grams:number;featured:boolean;bestseller:boolean;published:boolean;category_id:number;category:Category;variants:Variant[];average_rating:number;review_count:number}
export type CartItem = {id:number;quantity:number;line_total:string;unit_price:string;variant:Pick<Variant,'id'|'sku'|'size'|'color'|'stock'>;product:Pick<Product,'id'|'title'|'slug'|'brand'|'price'|'image_url'|'stock'>}
export type Cart = {items:CartItem[];subtotal:string;count:number}
export type OrderItem = {id:number;product_id:number;variant_id:number|null;title:string;variant_sku:string;size:string;color:string;unit_price:string;quantity:number}
export type Order = {id:number;order_number:string;status:string;subtotal:string;discount:string;shipping_fee:string;total:string;payment_method:string;payment_status:string;shipping_name:string;shipping_phone:string;shipping_address:string;gift_note:string;created_at:string;items:OrderItem[]}
