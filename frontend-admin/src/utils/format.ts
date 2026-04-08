import { format as dateFnsFormat, formatDistance, parseISO } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { formatBeijingDateTime } from './time';

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 * @param formatStr 格式化字符串，默认 'yyyy-MM-dd HH:mm:ss'
 * @returns 格式化后的日期字符串
 */
export function formatDateTime(date: string | Date | null | undefined, formatStr: string = 'yyyy-MM-dd HH:mm:ss'): string {
  if (!date) return '-';
  // Project-wide unified requirement: always display full Beijing datetime.
  // Keep the signature for compatibility with existing callers.
  const unified = formatBeijingDateTime(date as any);
  if (unified) return unified;

  try {
    const d = typeof date === 'string' ? parseISO(date) : date;
    return dateFnsFormat(d, formatStr, { locale: zhCN });
  } catch (error) {
    console.error('Format date error:', error);
    return '-';
  }
}

/**
 * 格式化日期（仅日期）
 */
export function formatDate(date: string | Date | null | undefined): string {
  const formatted = formatBeijingDateTime(date as any);
  return formatted || '-';
}

/**
 * 格式化金额（分转元，保留两位小数）
 * @param amount 金额（单位：分）
 * @param withSymbol 是否包含货币符号
 * @returns 格式化后的金额字符串
 */
export function formatAmount(amount: number | null | undefined, withSymbol: boolean = false): string {
  if (amount === null || amount === undefined) return '-';
  
  const yuan = (amount / 100).toFixed(2);
  const value = Number(yuan).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  
  return withSymbol ? `¥${value}` : value;
}

/**
 * 格式化百分比
 * @param value 值 (0-1)
 * @param decimals 小数位数
 */
export function formatPercent(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return '-';
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * 格式化手机号（脱敏）
 * @param phone 手机号
 * @param maskChar 脱敏字符，默认 '*'
 */
export function formatPhone(phone: string | null | undefined, maskChar: string = '*'): string {
  if (!phone) return '-';
  
  const phoneStr = String(phone);
  if (/^\d{11}$/.test(phoneStr)) {
    return phoneStr.slice(0, 3) + maskChar.repeat(4) + phoneStr.slice(7);
  }

  const prefixed = phoneStr.match(/^\+(\d{1,5})(\d{5,20})$/);
  if (prefixed) {
    const [, prefix, number] = prefixed;
    if (number.length >= 7) {
      return `+${prefix}${number.slice(0, 3)}${maskChar.repeat(4)}${number.slice(-4)}`;
    }
  }

  return phoneStr;
}

/**
 * 相对时间描述
 * @param date 日期
 * @param locale 语言环境
 */
export function formatRelativeTime(date: string | Date, locale: 'zh' | 'en' = 'zh'): string {
  try {
    const d = typeof date === 'string' ? parseISO(date) : date;
    return formatDistance(d, new Date(), { locale: locale === 'zh' ? zhCN : undefined });
  } catch (error) {
    return '-';
  }
}

/**
 * 文件大小格式化
 * @param bytes 字节数
 * @param decimals 小数位数
 */
export function formatFileSize(bytes: number | null | undefined, decimals: number = 2): string {
  if (bytes === null || bytes === undefined) return '-';
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 格式化订单号（添加空格提高可读性）
 * @param orderNo 订单号
 */
export function formatOrderNo(orderNo: string): string {
  if (!orderNo) return '';
  return orderNo.replace(/(.{4})/g, '$1 ').trim();
}

// 兼容旧代码的别名
export { formatPhone as maskPhone };
