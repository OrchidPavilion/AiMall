export interface MallUserProfile {
  id: number
  name: string
  phone: string
  age?: number | null
  hobby?: string
  address?: string
  avatar?: string
}

const KEY = 'aimall_mall_user'

export function getMallUser(): MallUserProfile | null {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function setMallUser(user: MallUserProfile) {
  localStorage.setItem(KEY, JSON.stringify(user))
  window.dispatchEvent(new Event('aimall-auth-changed'))
}

export function clearMallUser() {
  localStorage.removeItem(KEY)
  window.dispatchEvent(new Event('aimall-auth-changed'))
}

export function getMallCustomerId(): number | null {
  return getMallUser()?.id ?? null
}

export function ensureMallCustomerId(): number {
  const id = getMallCustomerId()
  if (!id) throw new Error('请先登录')
  return id
}
