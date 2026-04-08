import request from '../request';

export interface DashboardTrendPoint {
  date: string;
  customerIncrement: number;
  orderIncrement: number;
}

export interface DashboardTrendData {
  startDate: string;
  endDate: string;
  days: number;
  customerIncrementTotal: number;
  orderIncrementTotal: number;
  points: DashboardTrendPoint[];
}

export const dashboardApi = {
  getTrend(params: {
    startDate?: string;
    endDate?: string;
    days?: number;
  }) {
    return request.post<DashboardTrendData>('/dashboard/trend', params);
  }
};

