import { useState, useEffect } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import apiClient from '../api/client';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function TicketCharts() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sentimentTrends, setSentimentTrends] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, trendsRes] = await Promise.all([
        apiClient.get('/support/stats'),
        apiClient.get('/support/sentiment-trends?days=7'),
      ]);

      setStats(statsRes.data);
      setSentimentTrends(trendsRes.data);
    } catch (error) {
      console.error('Error fetching chart data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getColor = (isDark) => {
    return isDark ? '#f1f5f9' : '#1e293b';
  };

  const isDarkMode = document.documentElement.classList.contains('dark');

  if (loading) {
    return <div className="text-gray-500 dark:text-slate-400">Loading charts...</div>;
  }

  // Check if there's data
  const hasIntentData = stats?.intent_breakdown && Object.keys(stats.intent_breakdown).length > 0;
  const hasSentimentData = sentimentTrends?.distribution && 
    (sentimentTrends.distribution.positive > 0 || 
     sentimentTrends.distribution.neutral > 0 || 
     sentimentTrends.distribution.negative > 0);
  const hasStatusData = stats?.status_breakdown && Object.keys(stats.status_breakdown).length > 0;

  const intentData = {
    labels: stats?.intent_breakdown ? Object.keys(stats.intent_breakdown) : ['No Data'],
    datasets: [
      {
        label: 'Tickets by Intent',
        data: stats?.intent_breakdown ? Object.values(stats.intent_breakdown) : [0],
        backgroundColor: ['#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#6b7280'],
        borderColor: ['#2563eb', '#7c3aed', '#d97706', '#dc2626', '#4b5563'],
        borderWidth: 1,
      },
    ],
  };

  const sentimentData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        label: 'Sentiment Distribution',
        data: [
          sentimentTrends?.distribution?.positive || 0,
          sentimentTrends?.distribution?.neutral || 0,
          sentimentTrends?.distribution?.negative || 0,
        ],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderColor: ['#059669', '#d97706', '#dc2626'],
        borderWidth: 1,
      },
    ],
  };

  const statusData = {
    labels: stats?.status_breakdown ? Object.keys(stats.status_breakdown) : ['No Data'],
    datasets: [
      {
        label: 'Tickets by Status',
        data: stats?.status_breakdown ? Object.values(stats.status_breakdown) : [0],
        backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#6b7280'],
        borderColor: ['#d97706', '#2563eb', '#059669', '#4b5563'],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: getColor(isDarkMode),
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: getColor(isDarkMode),
          stepSize: 1,
        },
      },
      x: {
        ticks: {
          color: getColor(isDarkMode),
        },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: getColor(isDarkMode),
        },
      },
    },
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Intent Distribution</h3>
          {hasIntentData ? (
            <Bar data={intentData} options={options} />
          ) : (
            <p className="text-gray-500 dark:text-slate-400 text-sm">No intent data available</p>
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Sentiment Distribution</h3>
          {hasSentimentData ? (
            <Doughnut data={sentimentData} options={doughnutOptions} />
          ) : (
            <p className="text-gray-500 dark:text-slate-400 text-sm">No sentiment data available</p>
          )}
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Status Breakdown</h3>
          {hasStatusData ? (
            <Bar data={statusData} options={options} />
          ) : (
            <p className="text-gray-500 dark:text-slate-400 text-sm">No status data available</p>
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Quick Stats</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
              <span className="text-sm text-gray-600 dark:text-slate-300">Total Tickets</span>
              <span className="text-xl font-bold text-gray-900 dark:text-slate-100">{stats?.total_tickets || 0}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
              <span className="text-sm text-gray-600 dark:text-slate-300">Escalated</span>
              <span className="text-xl font-bold text-red-600 dark:text-red-400">{stats?.escalated_count || 0}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
              <span className="text-sm text-gray-600 dark:text-slate-300">Escalation Rate</span>
              <span className="text-xl font-bold text-primary-600 dark:text-primary-400">{stats?.escalation_rate || 0}%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
              <span className="text-sm text-gray-600 dark:text-slate-300">Open Tickets</span>
              <span className="text-xl font-bold text-yellow-600 dark:text-yellow-400">{stats?.status_breakdown?.new || 0}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <span className="text-sm text-gray-600 dark:text-slate-300">SLA Breached</span>
              <span className="text-xl font-bold text-red-600 dark:text-red-400">{stats?.sla_breached || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}