import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { OrderQuery } from '@/types';

export const useOrderStore = defineStore('order', () => {
  const searchParams = ref<OrderQuery>({
    page: 1,
    pageSize: 20,
    keyword: '',
    status: undefined,
    paymentStatus: undefined,
    startTime: undefined,
    endTime: undefined
  });
  
  const batchActionType = ref<'SHIP' | 'REFUND' | 'CANCEL' | null>(null);
  const batchSelectedOrders = ref<Set<number>>(new Set());
  
  function setSearchParams(params: Partial<OrderQuery>) {
    Object.assign(searchParams.value, params);
  }
  
  function resetSearchParams() {
    searchParams.value = {
      page: 1,
      pageSize: 20,
      keyword: '',
      status: undefined,
      paymentStatus: undefined,
      startTime: undefined,
      endTime: undefined
    };
  }
  
  function setBatchAction(type: 'SHIP' | 'REFUND' | 'CANCEL') {
    batchActionType.value = type;
  }
  
  function clearBatchAction() {
    batchActionType.value = null;
    batchSelectedOrders.value.clear();
  }
  
  function toggleBatchOrder(id: number) {
    if (batchSelectedOrders.value.has(id)) {
      batchSelectedOrders.value.delete(id);
    } else {
      batchSelectedOrders.value.add(id);
    }
  }
  
  function getBatchSelectedOrders(): number[] {
    return Array.from(batchSelectedOrders.value);
  }
  
  function hasBatchSelected(): boolean {
    return batchSelectedOrders.value.size > 0;
  }
  
  return {
    searchParams,
    batchActionType,
    batchSelectedOrders,
    setSearchParams,
    resetSearchParams,
    setBatchAction,
    clearBatchAction,
    toggleBatchOrder,
    getBatchSelectedOrders,
    hasBatchSelected
  };
});