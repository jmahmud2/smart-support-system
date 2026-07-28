import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import TicketCharts from '../components/TicketCharts';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [recentTickets, setRecentTickets] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [sentimentTrends, setSentimentTrends] = useState(null);
  const [aiSummary, setAiSummary] = useState(null);
  const [showSummary, setShowSummary] = useState(false);

  const exampleMessages = [
    "My laptop screen is cracked. I need a replacement urgently.",
    "When will my order arrive? It's been 3 days since I placed it.",
    "Which laptop do you recommend for programming and gaming?",
    "The product I received is defective. I want a full refund.",
    "I love my new headphones! They sound amazing."
  ];

  useEffect(() => {
    fetchDashboardData();
    fetchSentimentTrends();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const statsResponse = await apiClient.get('/support/stats');
      setStats(statsResponse.data);

      const ticketsResponse = await apiClient.get('/support/tickets?limit=5');
      
      let ticketsData = [];
      if (ticketsResponse.data) {
        if (ticketsResponse.data.data && Array.isArray(ticketsResponse.data.data)) {
          ticketsData = ticketsResponse.data.data;
        } else if (ticketsResponse.data.value && Array.isArray(ticketsResponse.data.value)) {
          ticketsData = ticketsResponse.data.value;
        } else if (Array.isArray(ticketsResponse.data)) {
          ticketsData = ticketsResponse.data;
        }
      }
      
      setRecentTickets(ticketsData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setRecentTickets([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSentimentTrends = async () => {
    try {
      const response = await apiClient.get('/support/sentiment-trends?days=7');
      setSentimentTrends(response.data);
    } catch (error) {
      console.error('Error fetching sentiment trends:', error);
    }
  };

  const fetchAiSummary = async () => {
    try {
      const response = await apiClient.get('/support/summary?days=7');
      setAiSummary(response.data);
      setShowSummary(true);
    } catch (error) {
      console.error('Error fetching AI summary:', error);
      alert('Failed to generate AI summary');
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
      
      setSaveSuccess(true);
      fetchDashboardData();
      setRecentTickets(prev => {
        const newTickets = [response.data, ...prev.slice(0, 4)];
        return newTickets;
      });
      
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

  const loadExample = () => {
    const randomIndex = Math.floor(Math.random() * exampleMessages.length);
    setMessage(exampleMessages[randomIndex]);
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
    if (type === 'intent') {
      switch(value) {
        case 'refund': return 'badge-purple';
        case 'shipping': return 'badge-blue';
        case 'product_inquiry': return 'badge-cyan';
        case 'complaint': return 'badge-red';
        case 'general': return 'badge-gray';
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
        <div className="text-gray-500 dark:text-slate-400">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Dashboard</h1>
        <p className="text-gray-600 dark:text-slate-400 mt-1">AI-powered support overview and analytics</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-slate-400">Total Tickets</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-slate-100">{stats?.total_tickets || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-slate-400">Open Tickets</p>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats?.status_breakdown?.new || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-slate-400">Escalated</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats?.escalated_count || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-slate-400">Escalation Rate</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{stats?.escalation_rate || 0}%</p>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="card mb-8">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Analytics Dashboard</h2>
        <TicketCharts />
      </div>

      {sentimentTrends && (
        <div className="card mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Sentiment Distribution</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-sm font-medium text-gray-600 dark:text-slate-300">Positive</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {sentimentTrends?.distribution?.positive || 0}
              </p>
            </div>
            <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <p className="text-sm font-medium text-gray-600 dark:text-slate-300">Neutral</p>
              <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                {sentimentTrends?.distribution?.neutral || 0}
              </p>
            </div>
            <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <p className="text-sm font-medium text-gray-600 dark:text-slate-300">Negative</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                {sentimentTrends?.distribution?.negative || 0}
              </p>
            </div>
          </div>
          <p className="text-xs text-gray-500 dark:text-slate-400 text-center mt-2">{sentimentTrends?.period}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <div className="mb-2">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">AI Demo Tool</h2>
            <p className="text-xs text-gray-500 dark:text-slate-400">Test the AI analysis before creating tickets. Analysis is automatically applied when tickets are created.</p>
          </div>
          
          <div className="space-y-4">
            <textarea
              className="input min-h-[100px]"
              placeholder="Enter customer message to analyze..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            
            <div className="flex flex-wrap gap-2">
              <button
                className="btn btn-secondary btn-sm"
                onClick={loadExample}
              >
                Load Example
              </button>
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

            {analyzing && (
              <div className="flex items-center justify-center p-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <span className="ml-2 text-gray-600 dark:text-slate-300">Analyzing message...</span>
              </div>
            )}

            {analysisResult && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-slate-700 rounded-lg space-y-3">
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
                <p className="text-sm font-medium text-gray-700 dark:text-slate-200">Intent: {analysisResult.intent}</p>
                
                {analysisResult.sentiment_explanation && (
                  <p className="text-sm text-gray-600 dark:text-slate-300">
                    <span className="font-medium">Sentiment reason:</span> {analysisResult.sentiment_explanation}
                  </p>
                )}
                
                {analysisResult.priority_reasoning && (
                  <p className="text-sm text-gray-600 dark:text-slate-300">
                    <span className="font-medium">Priority reason:</span> {analysisResult.priority_reasoning}
                  </p>
                )}
                
                {analysisResult.escalate_reasoning && (
                  <p className="text-sm text-gray-600 dark:text-slate-300">
                    <span className="font-medium">Escalation reason:</span> {analysisResult.escalate_reasoning}
                  </p>
                )}
                
                {analysisResult.ticket_summary && (
                  <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded border border-purple-200 dark:border-purple-800">
                    <p className="text-sm text-purple-700 dark:text-purple-300">
                      <span className="font-medium">Summary:</span> {analysisResult.ticket_summary}
                    </p>
                  </div>
                )}
                
                {analysisResult.assigned_agent && (
                  <p className="text-sm text-gray-600 dark:text-slate-300">
                    <span className="font-medium">Assigned to:</span> {analysisResult.assigned_agent}
                  </p>
                )}
                
                {analysisResult.recommended_products && analysisResult.recommended_products.length > 0 && (
                  <div className="mt-2">
                    <p className="text-sm font-medium text-gray-700 dark:text-slate-200">Recommended Products:</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {analysisResult.recommended_products.map((product, index) => (
                        <span key={index} className="badge badge-blue">
                          {product}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="p-3 bg-white dark:bg-slate-600 rounded border border-gray-200 dark:border-slate-500">
                  <p className="text-sm text-gray-700 dark:text-slate-200">{analysisResult.response}</p>
                </div>
                
                <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-200 dark:border-slate-600">
                  <button
                    className="btn btn-primary flex-1"
                    onClick={handleSaveTicket}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Create Ticket from Analysis'}
                  </button>
                </div>
                
                {saveSuccess && (
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <p className="text-green-700 dark:text-green-300 text-sm font-medium">Ticket saved successfully!</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Recent Tickets</h2>
            <button 
              onClick={fetchDashboardData}
              className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
            >
              Refresh
            </button>
          </div>

          {recentTickets.length === 0 ? (
            <p className="text-gray-500 dark:text-slate-400 text-sm">No tickets found</p>
          ) : (
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {recentTickets.map((ticket) => (
                <div key={ticket.id} className="p-3 bg-gray-50 dark:bg-slate-700 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-600 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                        {ticket.ticket_summary || ticket.customer_message?.substring(0, 60)}...
                      </p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        <span className={`badge ${getBadgeColor('status', ticket.status)}`}>
                          {ticket.status}
                        </span>
                        <span className={`badge ${getBadgeColor('intent', ticket.intent)}`}>
                          {ticket.intent}
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
                    <span className="text-xs text-gray-500 dark:text-slate-400 ml-2 whitespace-nowrap">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">AI Ticket Summary</h2>
          <button
            className="btn btn-primary btn-sm"
            onClick={fetchAiSummary}
          >
            {showSummary ? 'Refresh Summary' : 'Generate Summary'}
          </button>
        </div>

        {showSummary && aiSummary ? (
          <div className="space-y-4">
            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-slate-300">
              <span>{aiSummary.period}</span>
              <span>{aiSummary.total_tickets} tickets analyzed</span>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-slate-700 rounded-lg whitespace-pre-wrap">
              <p className="text-gray-700 dark:text-slate-200">{aiSummary.summary}</p>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 dark:text-slate-400 text-sm">
            Click "Generate Summary" to get an AI-powered summary of recent tickets.
          </p>
        )}
      </div>

      {stats?.intent_breakdown && (
        <div className="card mt-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Intent Distribution</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(stats.intent_breakdown).map(([intent, count]) => (
              <div key={intent} className="text-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
                <p className="text-sm font-medium text-gray-600 dark:text-slate-300">{intent}</p>
                <p className="text-xl font-bold text-gray-900 dark:text-slate-100">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}