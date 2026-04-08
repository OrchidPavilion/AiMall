import type { FormItemRule } from 'element-plus';

/**
 * 手机号验证
 */
export function validatePhone(rule: any, value: string, callback: Function) {
  if (!value) {
    callback(new Error('请输入手机号'));
    return;
  }
  
  const phoneReg = /^1[3-9]\d{9}$/;
  if (!phoneReg.test(value)) {
    callback(new Error('请输入正确的手机号'));
  } else {
    callback();
  }
}

/**
 * 邮箱验证
 */
export function validateEmail(rule: any, value: string, callback: Function) {
  if (!value) {
    callback();
    return;
  }
  
  const emailReg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailReg.test(value)) {
    callback(new Error('请输入正确的邮箱地址'));
  } else {
    callback();
  }
}

/**
 * 密码强度验证
 */
export function validatePassword(rule: any, value: string, callback: Function) {
  if (!value) {
    callback(new Error('请输入密码'));
    return;
  }
  
  const minLength = 8;
  const hasUpper = /[A-Z]/.test(value);
  const hasLower = /[a-z]/.test(value);
  const hasNumber = /\d/.test(value);
  
  if (value.length < minLength) {
    callback(new Error(`密码长度不能小于${minLength}位`));
  } else if (!(hasUpper && hasLower && hasNumber)) {
    callback(new Error('密码必须包含大小写字母和数字'));
  } else {
    callback();
  }
}

/**
 * 数值范围验证
 */
export function validateNumberRange(min: number, max: number) {
  return (rule: any, value: number | undefined, callback: Function) => {
    if (value === undefined || value === null) {
      callback(new Error('请输入数值'));
      return;
    }
    
    if (value < min || value > max) {
      callback(new Error(`数值必须在 ${min} 到 ${max} 之间`));
    } else {
      callback();
    }
  };
}

/**
 * 必填项验证
 */
export function validateRequired(rule: any, value: any, callback: Function) {
  if (value === undefined || value === null || value === '') {
    callback(new Error('此项为必填项'));
  } else {
    callback();
  }
}

/**
 * 整数验证
 */
export function validateInteger(rule: any, value: number | string, callback: Function) {
  if (value === undefined || value === null || value === '') {
    callback();
    return;
  }
  
  const num = Number(value);
  if (!Number.isInteger(num)) {
    callback(new Error('必须为整数'));
  } else {
    callback();
  }
}

/**
 * URL 验证
 */
export function validateUrl(rule: any, value: string, callback: Function) {
  if (!value) {
    callback();
    return;
  }
  
  try {
    new URL(value);
    callback();
  } catch (error) {
    callback(new Error('请输入正确的 URL'));
  }
}

/**
 * 上传文件大小限制验证
 */
export function validateFileSize(maxSize: number, unit: 'KB' | 'MB' = 'KB') {
  const sizeInBytes = unit === 'KB' ? maxSize * 1024 : maxSize * 1024 * 1024;
  
  return (rule: any, file: File, callback: Function) => {
    if (file.size > sizeInBytes) {
      callback(new Error(`文件大小不能超过${maxSize}${unit}`));
    } else {
      callback();
    }
  };
}

/**
 * 上传文件类型验证
 */
export function validateFileType(accept: string[]) {
  const mimeTypes = accept.map(type => type.trim());
  
  return (rule: any, file: File, callback: Function) => {
    if (mimeTypes.length === 0) {
      callback();
      return;
    }
    
    const fileType = file.type;
    const isValid = mimeTypes.some(type => {
      if (type.startsWith('.')) {
        // 扩展名匹配
        const ext = '.' + file.name.split('.').pop()?.toLowerCase();
        return ext === type.toLowerCase();
      } else {
        // MIME 类型匹配
        return fileType === type;
      }
    });
    
    if (!isValid) {
      callback(new Error(`文件类型不支持，只支持 ${mimeTypes.join(', ')}`));
    } else {
      callback();
    }
  };
}

/**
 * 创建包含必填验证的规则
 */
export function createRequiredRule(message: string = '此项为必填项'): FormItemRule[] {
  return [
    { required: true, message, trigger: 'blur' },
    { validator: validateRequired, trigger: 'change' }
  ];
}

/**
 * 创建手机号规则
 */
export function createPhoneRule(required: boolean = true): FormItemRule[] {
  const rules: FormItemRule[] = [];
  
  if (required) {
    rules.push({ required: true, message: '请输入手机号', trigger: 'blur' });
  }
  
  rules.push({
    validator: validatePhone,
    trigger: ['blur', 'change']
  });
  
  return rules;
}

/**
 * 创建手机号验证规则
 */
export function createEmailRule(required: boolean = false): FormItemRule[] {
  const rules: FormItemRule[] = [];
  
  if (required) {
    rules.push({ required: true, message: '请输入邮箱地址', trigger: 'blur' });
  } else {
    rules.push({ required: false });
  }
  
  rules.push({
    validator: validateEmail,
    trigger: ['blur', 'change']
  });
  
  return rules;
}

/**
 * 创建密码规则
 */
export function createPasswordRule(required: boolean = true, minLength?: number): FormItemRule[] {
  const rules: FormItemRule[] = [];
  
  if (required) {
    rules.push({ required: true, message: '请输入密码', trigger: 'blur' });
  }
  
  if (minLength) {
    rules.push({ min: minLength, message: `密码长度不能小于${minLength}位`, trigger: 'blur' });
  }
  
  rules.push({
    validator: validatePassword,
    trigger: ['blur', 'change']
  });
  
  return rules;
}
