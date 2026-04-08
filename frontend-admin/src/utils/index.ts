export * from './format';
export * from './validate';
export * from './auth';
export * from './constant';
export * from './time';

// 通用工具函数
import { ElMessage, ElMessageBox } from 'element-plus';

/**
 * 显示成功消息
 */
export function showSuccess(message: string) {
  ElMessage.success(message);
}

/**
 * 显示失败消息
 */
export function showError(message: string) {
  ElMessage.error(message);
}

/**
 * 显示警告消息
 */
export function showWarning(message: string) {
  ElMessage.warning(message);
}

/**
 * 显示信息消息
 */
export function showInfo(message: string) {
  ElMessage.info(message);
}

/**
 * 确认对话框
 */
export async function confirm(message: string, title?: string): Promise<boolean> {
  try {
    await ElMessageBox.confirm(message, title || '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * 深拷贝
 */
export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return function (this: any, ...args: Parameters<T>) {
    clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  return function (this: any, ...args: Parameters<T>) {
    if (timer) return;
    timer = setTimeout(() => {
      fn.apply(this, args);
      timer = null;
    }, wait);
  };
}
