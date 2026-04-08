import type { FieldConfigItem, FieldConfigSchema } from '@/types';

type LocalSchemaFormField = {
  prop: string;
  label: string;
  type: 'input' | 'textarea' | 'select' | 'radio' | 'checkbox' | 'date' | 'datetime' | 'number' | 'switch' | 'custom';
  className?: string;
  placeholder?: string;
  options?: Array<{ label: string; value: string | number | boolean }>;
  rows?: number;
  valueFormat?: string;
  format?: string;
};

export function getFieldConfigItem(schema: FieldConfigSchema | null | undefined, key: string) {
  if (!schema) return null;
  return [...(schema.baseFields || []), ...(schema.customFields || [])].find((item) => item.key === key) || null;
}

export function isFieldVisible(schema: FieldConfigSchema | null | undefined, key: string, defaultVisible = true) {
  const item = getFieldConfigItem(schema, key);
  return item?.visible ?? defaultVisible;
}

export function getFieldLabel(schema: FieldConfigSchema | null | undefined, key: string, fallback: string) {
  const item = getFieldConfigItem(schema, key);
  return item?.displayName || fallback;
}

export function applyFieldConfigToSchemaFields<T extends { prop: string; label: string }>(
  fields: T[],
  schema: FieldConfigSchema | null | undefined
) {
  return fields
    .filter((field) => isFieldVisible(schema, field.prop, true))
    .map((field) => ({
      ...field,
      label: getFieldLabel(schema, field.prop, field.label)
    }));
}

export function buildCustomSchemaFields(schema: FieldConfigSchema | null | undefined): LocalSchemaFormField[] {
  const customFields = Array.isArray(schema?.customFields) ? schema!.customFields : [];
  return customFields
    .filter((item) => item && item.visible !== false)
    .map(mapFieldConfigItemToSchemaField)
    .filter(Boolean) as LocalSchemaFormField[];
}

export function mapFieldConfigItemToSchemaField(item: FieldConfigItem): LocalSchemaFormField | null {
  const typeMap: Record<string, LocalSchemaFormField['type']> = {
    TEXT: 'input',
    TEXTAREA: 'textarea',
    NUMBER: 'number',
    DATE: 'date',
    DATETIME: 'datetime',
    RADIO: 'radio',
    CHECKBOX: 'checkbox',
    SELECT: 'select'
  };
  const type = typeMap[item.fieldType];
  if (!type) return null;

  return {
    prop: item.key,
    label: item.displayName || item.systemName || item.key,
    type,
    className: ['select', 'date', 'datetime'].includes(type) ? 'w-100' : undefined,
    placeholder: getFieldPlaceholder(type, item.displayName || item.systemName || item.key),
    options: Array.isArray(item.options)
      ? item.options.map((o) => ({ label: o.label, value: o.value }))
      : undefined,
    rows: type === 'textarea' ? 3 : undefined,
    valueFormat: type === 'date' ? 'YYYY-MM-DD' : (type === 'datetime' ? 'YYYY-MM-DD HH:mm:ss' : undefined),
    format: type === 'date' ? 'YYYY-MM-DD' : (type === 'datetime' ? 'YYYY-MM-DD HH:mm:ss' : undefined)
  };
}

export function formatFieldConfigValue(item: FieldConfigItem | undefined | null, rawValue: any): string {
  if (rawValue == null || rawValue === '') return '-';
  if (!item) return String(rawValue);
  if (['RADIO', 'SELECT'].includes(item.fieldType)) {
    const opt = item.options?.find((o) => String(o.value) === String(rawValue));
    return opt?.label || String(rawValue);
  }
  if (item.fieldType === 'CHECKBOX') {
    const values = Array.isArray(rawValue) ? rawValue : [rawValue];
    const labels = values.map((v) => item.options?.find((o) => String(o.value) === String(v))?.label || String(v));
    return labels.join('、') || '-';
  }
  return String(rawValue);
}

function getFieldPlaceholder(type: LocalSchemaFormField['type'], label: string) {
  if (type === 'select' || type === 'radio' || type === 'checkbox') return `请选择${label}`;
  if (type === 'date' || type === 'datetime') return `请选择${label}`;
  return `请输入${label}`;
}
