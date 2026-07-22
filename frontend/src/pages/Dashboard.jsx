import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [recentTickets, setRecentTickets] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Fetch stats and recent tickets on load
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch stats
      const statsResponse = await apiClient.get('/support/stats');
      setStats(statsResponse.data);

      // Fetch recent tickets
      const ticketsResponse = await apiClient.get('/support/tickets?limit=5');
      setRecentTickets(ticketsResponse.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!message.trim()) return;

    setAnalyzing(true);
    setAnalysisResult(null);
    setSaveSuccess(false);

    try {
      const response = await apiClient.post('/support/analyze', {
        message: message
      });
      setAnalysisResult(response.data);
    } catch (error) {
      console.error('Error analyzing message:', error);
      alert('Error analyzing message. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSaveTicket = async () => {
    if (!analysisResult) return;

    setSaving(true);
    setSaveSuccess(false);

    try {
      const ticketData = {
        customer_name: 'Walk-in Customer',
        customer_email: 'customer@example.com',
        customer_message: message,
        product_id: null
      };

      const response = await apiClient.post('/support/tickets', ticketData);
      
      // Show success
      setSaveSuccess(true);
      
      // Refresh recent tickets
      fetchDashboardData();
      
      // Add the new ticket to recent tickets list
      setRecentTickets(prev => [response.data, ...prev.slice(0, 4)]);
      
      // Auto-clear success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
      
    } catch (error) {
      console.error('Error saving ticket:', error);
      alert('Failed to save ticket. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleClear = () => {
    setMessage('');
    setAnalysisResult(null);
    setSaveSuccess(false);
  };

  const getBadgeColor = (type, value) => {
    if (type === 'sentiment') {
      switch(value) {
        case 'positive': return 'badge-green';
        case 'neutral': return 'badge-yellow';
        case 'negative': return 'badge-red';
        default: return 'badge-gray';
      }
    }
    if (type === 'priority') {
      switch(value) {
        case 'urgent': return 'badge-red';
        case 'high': return 'badge-orange';
        case 'medium': return 'badge-yellow';
        case 'low': return 'badge-gray';
        default: return 'badge-gray';
      }
    }
    if (type === 'status') {
      switch(value) {
        case 'new': return 'badge-yellow';
        case 'in_progress': return 'badge-blue';
        case 'resolved': return 'badge-green';
        case 'closed': return 'badge-gray';
        default: return 'badge-gray';
      }
    }
    if (type === 'escalate') {
      return value ? 'badge-red' : 'badge-green';
    }
    return 'badge-gray';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">AI-powered support overview and analytics</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500">Total Tickets</p>
          <p className="text-2xl font-bold text-gray-900">{stats?.total_tickets || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Open Tickets</p>
          <p className="text-2xl font-bold text-yellow-600">{stats?.status_breakdown?.new || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Escalated</p>
          <p className="text-2xl font-bold text-red-600">{stats?.escalated_count || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Escalation Rate</p>
          <p className="text-2xl font-bold text-primary-600">{stats?.escalation_rate || 0}%</p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AI Support Analyzer */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI Support Assistant</h2>
          
          <div className="space-y-4">
            <textarea
              className="input min-h-[100px]"
              placeholder="Enter customer message to analyze..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            
            <div className="flex flex-wrap gap-2">
              <button
                className="btn btn-primary flex-1"
                onClick={handleAnalyze}
                disabled={analyzing || !message.trim()}
              >
                {analyzing ? 'Analyzing...' : 'Analyze Message'}
              </button>
              {message && (
                <button
                  className="btn btn-secondary"
                  onClick={handleClear}
                >
                  Clear
                </button>
              )}
            </div>

            {analysisResult && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-3">
                <div className="flex flex-wrap gap-2">
                  <span className={`badge ${getBadgeColor('sentiment', analysisResult.sentiment)}`}>
                    {analysisResult.sentiment}
                  </span>
                  <span className={`badge ${getBadgeColor('priority', analysisResult.priority)}`}>
                    {analysisResult.priority}
                  </span>
                  <span className={`badge ${getBadgeColor('escalate', analysisResult.escalate)}`}>
                    {analysisResult.escalate ? 'Escalate' : 'Auto-respond'}
                  </span>
                </div>
                <p className="text-sm font-medium text-gray-700">Intent: {analysisResult.intent}</p>
                <p className="text-sm text-gray-600">{analysisResult.reasoning}</p>
                <div className="p-3 bg-white rounded border border-gray-200">
                  <p className="text-sm text-gray-700">{analysisResult.response}</p>
                </div>
                
                {/* Save Ticket Button */}
                <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-200">
                  <button
                    className="btn btn-primary flex-1"
                    onClick={handleSaveTicket}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : '💾 Save as Ticket'}
                  </button>
                </div>
                
                {/* Save Success Message */}
                {saveSuccess && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-green-700 text-sm font-medium">
                      ✅ Ticket saved successfully!
                    </p>
                    <p className="text-green-600 text-sm">
                      The analysis has been saved to the database.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Recent Tickets */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">🎫 Recent Tickets</h2>
            <button 
              onClick={fetchDashboardData}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Refresh
            </button>
          </div>

          {recentTickets.length === 0 ? (
            <p className="text-gray-500 text-sm">No tickets found</p>
          ) : (
            <div className="space-y-3">
              {recentTickets.map((ticket) => (
                <div key={ticket.id} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {ticket.customer_message?.substring(0, 60)}...
                      </p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        <span className={`badge ${getBadgeColor('status', ticket.status)}`}>
                          {ticket.status}
                        </span>
                        <span className={`badge ${getBadgeColor('sentiment', ticket.sentiment)}`}>
                          {ticket.sentiment}
                        </span>
                        <span className={`badge ${getBadgeColor('priority', ticket.priority)}`}>
                          {ticket.priority}
                        </span>
                        {ticket.escalate && (
                          <span className="badge badge-red">Escalated</span>
                        )}
                      </div>
                    </div>
                    <span className="text-xs text-gray-500 ml-2 whitespace-nowrap">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Intent Breakdown */}
      {stats?.intent_breakdown && (
        <div className="card mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Intent Distribution</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(stats.intent_breakdown).map(([intent, count]) => (
              <div key={intent} className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-600">{intent}</p>
                <p className="text-xl font-bold text-gray-900">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}