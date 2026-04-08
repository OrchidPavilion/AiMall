import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { CustomerQuery, Customer } from '@/types';

export const useCustomerStore = defineStore('customer', () => {
  const searchParams = ref<CustomerQuery>({
    page: 1,
    pageSize: 20,
    keyword: '',
    level: undefined,
    status: undefined,
    assigneeId: undefined
  });
  
  const selectedCustomers = ref<Set<number>>(new Set());
  
  function setSearchParams(params: Partial<CustomerQuery>) {
    Object.assign(searchParams.value, params);
  }
  
  function resetSearchParams() {
    searchParams.value = {
      page: 1,
      pageSize: 20,
      keyword: '',
      level: undefined,
      status: undefined,
      assigneeId: undefined
    };
  }
  
  function addSelectedCustomer(id: number) {
    selectedCustomers.value.add(id);
  }
  
  function removeSelectedCustomer(id: number) {
    selectedCustomers.value.delete(id);
  }
  
  function toggleSelectedCustomer(id: number) {
    if (selectedCustomers.value.has(id)) {
      selectedCustomers.value.delete(id);
    } else {
      selectedCustomers.value.add(id);
    }
  }
  
  function clearSelectedCustomers() {
    selectedCustomers.value.clear();
  }
  
  function getSelectedCustomers(): number[] {
    return Array.from(selectedCustomers.value);
  }
  
  return {
    searchParams,
    selectedCustomers,
    setSearchParams,
    resetSearchParams,
    addSelectedCustomer,
    removeSelectedCustomer,
    toggleSelectedCustomer,
    clearSelectedCustomers,
    getSelectedCustomers
  };
});