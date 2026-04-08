async function request(path: string, init?: RequestInit) {
  const headers: Record<string, string> = {}
  if (!(init?.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  const res = await fetch(`/api/v1${path}`, {
    ...init,
    headers: {
      ...headers,
      ...(init?.headers || {}),
    },
  })
  const json = await res.json()
  if (!res.ok || json?.code !== 0) {
    throw new Error(json?.message || '请求失败')
  }
  return json.data
}

export const mallApi = {
  mallRegister: (payload: { phone: string; password: string; name?: string }) => request('/mall/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  mallLogin: (payload: { phone: string; password: string }) => request('/mall/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  mallProfile: (customerId: number) => request(`/mall/auth/profile?customer_id=${customerId}`),

  home: () => request('/mall/home'),
  getCategories: () => request('/mall/categories/tree'),
  getRandomProducts: (cursor = 0, size = 20, seed?: number) => request(`/mall/products/random?cursor=${cursor}&size=${size}${seed ? `&seed=${seed}` : ''}`),
  getProducts: (params: { keyword?: string; categoryId?: string | number; page?: number; pageSize?: number }) => {
    const q = new URLSearchParams()
    if (params.keyword) q.set('keyword', params.keyword)
    if (params.categoryId) q.set('category_id', String(params.categoryId))
    q.set('page', String(params.page || 1))
    q.set('page_size', String(params.pageSize || 20))
    return request(`/mall/products?${q.toString()}`)
  },
  getProductDetail: (id: string | number) => request(`/mall/products/${id}`),
  getRecommendations: (customerId: number, size?: number | null, excludeIds: number[] = []) => {
    const q = new URLSearchParams({ customer_id: String(customerId) })
    if (size != null) q.set('size', String(size))
    if (excludeIds.length) q.set('exclude_ids', excludeIds.join(','))
    return request(`/mall/recommendations?${q.toString()}`)
  },
  trackBehavior: (payload: any) => request('/mall/behaviors', { method: 'POST', body: JSON.stringify(payload) }),
  getCartItems: (customerId: number) => request(`/mall/cart/items?customer_id=${customerId}`),
  addCartItem: (payload: any) => request('/mall/cart/items', { method: 'POST', body: JSON.stringify(payload) }),
  updateCartItem: (id: number, payload: any) => request(`/mall/cart/items/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteCartItem: (id: number) => request(`/mall/cart/items/${id}`, { method: 'DELETE' }),
  settlementPreview: (payload: any) => request('/mall/cart/settlement-preview', { method: 'POST', body: JSON.stringify(payload) }),
}
