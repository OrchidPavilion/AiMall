import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ProductQuery } from '@/types';

export const useProductStore = defineStore('product', () => {
  const searchParams = ref<ProductQuery>({
    page: 1,
    pageSize: 20,
    keyword: '',
    categoryId: undefined,
    status: undefined,
    hasStock: undefined
  });
  
  const editingProductId = ref<number | null>(null);
  
  function setSearchParams(params: Partial<ProductQuery>) {
    Object.assign(searchParams.value, params);
  }
  
  function resetSearchParams() {
    searchParams.value = {
      page: 1,
      pageSize: 20,
      keyword: '',
      categoryId: undefined,
      status: undefined,
      hasStock: undefined
    };
  }
  
  function setEditingProductId(id: number | null) {
    editingProductId.value = id;
  }
  
  return {
    searchParams,
    editingProductId,
    setSearchParams,
    resetSearchParams,
    setEditingProductId
  };
});