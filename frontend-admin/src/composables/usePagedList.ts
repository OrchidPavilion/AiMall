import { reactive, ref } from 'vue';

interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

interface UsePagedListOptions<TQuery extends Record<string, any>, TItem> {
  initialQuery: TQuery;
  fetcher: (params: TQuery & { page: number; pageSize: number }) => Promise<{
    list?: TItem[];
    total?: number;
  }>;
  pageSize?: number;
  onError?: (error: unknown) => void;
}

export function usePagedList<TQuery extends Record<string, any>, TItem>(
  options: UsePagedListOptions<TQuery, TItem>
) {
  const loading = ref(false);
  const tableData = ref<TItem[]>([]);
  const query = reactive({ ...options.initialQuery }) as TQuery;
  const pagination = reactive<PaginationState>({
    page: 1,
    pageSize: options.pageSize ?? 20,
    total: 0
  });

  const fetchData = async () => {
    loading.value = true;
    try {
      const data = await options.fetcher({
        ...(query as any),
        page: pagination.page,
        pageSize: pagination.pageSize
      });
      tableData.value = data.list || [];
      pagination.total = data.total || 0;
    } catch (error) {
      options.onError?.(error);
    } finally {
      loading.value = false;
    }
  };

  const search = async () => {
    pagination.page = 1;
    await fetchData();
  };

  const reset = async () => {
    Object.assign(query, { ...options.initialQuery });
    pagination.page = 1;
    await fetchData();
  };

  const setPage = async (page: number) => {
    pagination.page = page;
    await fetchData();
  };

  const setPageSize = async (size: number) => {
    pagination.pageSize = size;
    pagination.page = 1;
    await fetchData();
  };

  return {
    loading,
    tableData,
    query,
    pagination,
    fetchData,
    search,
    reset,
    setPage,
    setPageSize
  };
}

