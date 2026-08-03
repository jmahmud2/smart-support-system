import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [replyMessage, setReplyMessage] = useState('');
  const [sendingReply, setSendingReply] = useState(false);
  const [customerHistory, setCustomerHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  
  // AI Features state
  const [replyOptions, setReplyOptions] = useState([]);
  const [qualityScore, setQualityScore] = useState(null);
  const [kbArticles, setKbArticles] = useState([]);
  const [churnRisk, setChurnRisk] = useState(null);
  const [followupInfo, setFollowupInfo] = useState(null);
  const [ticketLanguage, setTicketLanguage] = useState(null);
  const [resolutionTime, setResolutionTime] = useState(null);
  const [feedbackAnalysis, setFeedbackAnalysis] = useState(null);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [loadingFeatures, setLoadingFeatures] = useState(false);
  const [featureError, setFeatureError] = useState(null);
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState('');
  const [intentFilter, setIntentFilter] = useState('');
  const [assignedFilter, setAssignedFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Pagination states
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [nextOffset, setNextOffset] = useState(null);
  const [prevOffset, setPrevOffset] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  
  // Agent options (dynamic)
  const [agentOptions, setAgentOptions] = useState([]);
  
  // New ticket form
  const [showNewTicket, setShowNewTicket] = useState(false);
  const [newTicket, setNewTicket] = useState({
    customer_name: '',
    customer_email: '',
    customer_message: '',
    product_id: ''
  });
  const [submitting, setSubmitting] = useState(false);

  // Current agent from login
  const currentAgent = JSON.parse(localStorage.getItem('user') || '{}')?.name || '';

  // Fetch agents on load
  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await apiClient.get('/support/agents');
      setAgentOptions(response.data.map(agent => agent.name));
    } catch (error) {
      console.error('Error fetching agents:', error);
      setAgentOptions([]);
    }
  };

  // Fetch tickets on load and filter changes
  useEffect(() => {
    fetchTickets();
  }, [statusFilter, intentFilter, assignedFilter, offset, limit]);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const params = {
        limit: limit,
        offset: offset
      };
      if (statusFilter) params.status = statusFilter;
      if (intentFilter) params.intent = intentFilter;
      
      const response = await apiClient.get('/support/tickets', { params });
      
      // Handle different response structures
      let ticketsData = [];
      let totalCount = 0;
      
      if (response.data.value && Array.isArray(response.data.value)) {
        ticketsData = response.data.value;
        totalCount = response.data.Count || ticketsData.length;
      } else if (response.data.data && Array.isArray(response.data.data)) {
        ticketsData = response.data.data;
        totalCount = response.data.pagination?.total || ticketsData.length;
      } else if (Array.isArray(response.data)) {
        ticketsData = response.data;
        totalCount = ticketsData.length;
      }
      
      // Client-side search
      if (searchTerm) {
        const search = searchTerm.toLowerCase();
        ticketsData = ticketsData.filter(ticket => 
          (ticket.customer_name || '').toLowerCase().includes(search) ||
          (ticket.customer_email || '').toLowerCase().includes(search) ||
          (ticket.customer_message || '').toLowerCase().includes(search)
        );
      }
      
      // Filter by assignment
      if (assignedFilter === 'unassigned') {
        ticketsData = ticketsData.filter(ticket => !ticket.assigned_to);
      } else if (assignedFilter === 'assigned') {
        ticketsData = ticketsData.filter(ticket => ticket.assigned_to);
      } else if (assignedFilter === 'my') {
        ticketsData = ticketsData.filter(ticket => ticket.assigned_to === currentAgent);
      }
      
      setTickets(ticketsData);
      setTotal(totalCount);
      
      const hasMore = ticketsData.length === limit;
      setNextOffset(hasMore ? offset + limit : null);
      setPrevOffset(offset > 0 ? offset - limit : null);
      setCurrentPage(Math.floor(offset / limit) + 1);
      
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setOffset(0);
    fetchTickets();
  };

  const handlePageChange = (newOffset) => {
    setOffset(newOffset);
  };

  const handleLimitChange = (newLimit) => {
    setLimit(newLimit);
    setOffset(0);
  };

  const handleUpdateStatus = async (ticketId, newStatus) => {
    try {
      await apiClient.patch(`/support/tickets/${ticketId}/status`, null, {
        params: { status: newStatus }
      });
      fetchTickets();
    } catch (error) {
      console.error('Error updating ticket status:', error);
      alert('Failed to update ticket status');
    }
  };

  const handleAssignTicket = async (ticketId, agentName) => {
    try {
      await apiClient.patch(`/support/tickets/${ticketId}/assign`, null, {
        params: { agent_name: agentName }
      });
      fetchTickets();
    } catch (error) {
      console.error('Error assigning ticket:', error);
      alert('Failed to assign ticket');
    }
  };

  const handleSendReply = async (ticketId) => {
    if (!replyMessage.trim()) return;
    
    setSendingReply(true);
    try {
      await apiClient.post(`/support/tickets/${ticketId}/reply`, {
        message: replyMessage
      });
      
      setReplyMessage('');
      fetchTickets();
      setShowDetail(false);
      
      alert('Reply sent successfully!');
    } catch (error) {
      console.error('Error sending reply:', error);
      alert('Failed to send reply. Please try again.');
    } finally {
      setSendingReply(false);
    }
  };

  const fetchCustomerHistory = async (email) => {
    if (!email) {
      alert('No email address available for this customer');
      return;
    }
    
    try {
      const response = await apiClient.get(`/support/tickets/customer/${email}`);
      setCustomerHistory(response.data);
      setShowHistory(true);
    } catch (error) {
      console.error('Error fetching customer history:', error);
      alert('Failed to fetch customer history');
    }
  };

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    if (!newTicket.customer_message.trim()) {
      alert('Please enter a customer message');
      return;
    }
    
    setSubmitting(true);
    try {
      await apiClient.post('/support/tickets', newTicket);
      setNewTicket({
        customer_name: '',
        customer_email: '',
        customer_message: '',
        product_id: ''
      });
      setShowNewTicket(false);
      fetchTickets();
    } catch (error) {
      console.error('Error creating ticket:', error);
      alert('Failed to create ticket');
    } finally {
      setSubmitting(false);
    }
  };

  // ============ AI FEATURES FUNCTIONS ============

  const fetchReplyOptions = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.post(`/support/tickets/${ticketId}/reply-options`);
      setReplyOptions(response.data.options || []);
    } catch (error) {
      console.warn('Reply options failed:', error.message);
      throw error;
    }
  };

  const evaluateResponse = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.post(`/support/tickets/${ticketId}/evaluate-response`);
      setQualityScore(response.data.quality_score);
    } catch (error) {
      console.warn('Response evaluation failed:', error.message);
      throw error;
    }
  };

  const fetchKnowledgeBase = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/knowledge-base`);
      setKbArticles(response.data.articles || []);
    } catch (error) {
      console.warn('Knowledge base search failed:', error.message);
      throw error;
    }
  };

  const fetchChurnRisk = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/churn-risk`);
      setChurnRisk(response.data.churn_risk);
    } catch (error) {
      console.warn('Churn risk prediction failed:', error.message);
      throw error;
    }
  };

  const fetchFollowupInfo = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/followup`);
      setFollowupInfo(response.data.followup);
    } catch (error) {
      console.warn('Follow-up detection failed:', error.message);
      throw error;
    }
  };

  const fetchLanguage = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/language`);
      setTicketLanguage(response.data.language);
    } catch (error) {
      console.warn('Language detection failed:', error.message);
      throw error;
    }
  };

  const fetchResolutionTime = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/resolution-time`);
      setResolutionTime(response.data.resolution_time);
    } catch (error) {
      console.warn('Resolution time prediction failed:', error.message);
      throw error;
    }
  };

  const submitFeedback = async (ticketId) => {
    if (!feedbackText.trim()) {
      alert('Please enter feedback');
      return;
    }
    setAnalyzing(true);
    try {
      const response = await apiClient.post(`/support/tickets/${ticketId}/feedback`, {
        feedback: feedbackText
      });
      setFeedbackAnalysis(response.data.feedback_analysis);
      setShowFeedbackForm(false);
      setFeedbackText('');
      alert('Feedback analyzed successfully!');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to analyze feedback');
    } finally {
      setAnalyzing(false);
    }
  };

  const loadAllAIFeatures = async (ticketId) => {
    if (!ticketId) return;
    setLoadingFeatures(true);
    setFeatureError(null);
    
    try {
      await Promise.all([
        fetchReplyOptions(ticketId),
        evaluateResponse(ticketId),
        fetchKnowledgeBase(ticketId),
        fetchChurnRisk(ticketId),
        fetchFollowupInfo(ticketId),
        fetchLanguage(ticketId),
        fetchResolutionTime(ticketId),
      ]);
    } catch (error) {
      console.warn('Some AI features failed:', error.message);
      setFeatureError('Some AI insights could not be loaded. Please try again.');
    } finally {
      setLoadingFeatures(false);
    }
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
    if (type === 'language') {
      return 'badge-blue';
    }
    if (type === 'sla') {
      switch(value) {
        case 'breached': return 'badge-red';
        case 'approaching': return 'badge-yellow';
        case 'on_track': return 'badge-green';
        default: return 'badge-gray';
      }
    }
    return 'badge-gray';
  };

  const getStatusOptions = () => {
    return ['new', 'in_progress', 'resolved', 'closed'];
  };

  const getIntentOptions = () => {
    return ['refund', 'shipping', 'product_inquiry', 'complaint', 'general'];
  };

  const getTimeAgo = (createdAt) => {
    const hours = Math.floor((Date.now() - new Date(createdAt)) / (1000 * 60 * 60));
    if (hours < 1) return 'Just now';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    return new Date(createdAt).toLocaleDateString();
  };

  const totalPages = Math.ceil(total / limit);

  // Export functions
  const handleExportCSV = async () => {
    if (tickets.length === 0) {
      alert('No tickets to export');
      return;
    }
    try {
      const { exportTicketsToCSV } = await import('../utils/exportUtils');
      exportTicketsToCSV(tickets);
    } catch (error) {
      console.error('Error exporting CSV:', error);
      alert('Failed to export CSV');
    }
  };

  const handleExportExcel = async () => {
    if (tickets.length === 0) {
      alert('No tickets to export');
      return;
    }
    try {
      const { exportTicketsToExcel } = await import('../utils/exportUtils');
      exportTicketsToExcel(tickets);
    } catch (error) {
      console.error('Error exporting Excel:', error);
      alert('Failed to export Excel');
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Support Tickets</h1>
          <p className="text-gray-600 dark:text-slate-400 mt-1">Manage and track customer support tickets</p>
        </div>
        <div className="flex flex-wrap gap-2 mt-4 sm:mt-0">
          <button
            className="btn btn-secondary btn-sm"
            onClick={handleExportCSV}
            disabled={tickets.length === 0}
          >
            Export CSV
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={handleExportExcel}
            disabled={tickets.length === 0}
          >
            Export Excel
          </button>
          <button
            className="btn btn-primary mt-4 sm:mt-0"
            onClick={() => setShowNewTicket(true)}
          >
            + New Ticket
          </button>
        </div>
      </div>

      <div className="card mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Search</label>
            <div className="flex gap-2">
              <input
                type="text"
                className="input"
                placeholder="Search name, email, message..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                className="btn btn-primary btn-sm"
                onClick={handleSearch}
              >
                Search
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Status</label>
            <select
              className="input"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setOffset(0);
              }}
            >
              <option value="">All Statuses</option>
              {getStatusOptions().map((status) => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Intent</label>
            <select
              className="input"
              value={intentFilter}
              onChange={(e) => {
                setIntentFilter(e.target.value);
                setOffset(0);
              }}
            >
              <option value="">All Intents</option>
              {getIntentOptions().map((intent) => (
                <option key={intent} value={intent}>{intent}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Assigned</label>
            <select
              className="input"
              value={assignedFilter}
              onChange={(e) => {
                setAssignedFilter(e.target.value);
                setOffset(0);
              }}
            >
              <option value="">All Tickets</option>
              <option value="unassigned">Unassigned Only</option>
              <option value="assigned">Assigned Only</option>
              <option value="my">My Tickets</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Show</label>
            <select
              className="input"
              value={limit}
              onChange={(e) => {
                handleLimitChange(parseInt(e.target.value));
              }}
            >
              <option value="10">10 per page</option>
              <option value="20">20 per page</option>
              <option value="50">50 per page</option>
            </select>
          </div>
        </div>

        {(statusFilter || intentFilter || assignedFilter || searchTerm) && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-700">
            <button
              className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
              onClick={() => {
                setStatusFilter('');
                setIntentFilter('');
                setAssignedFilter('');
                setSearchTerm('');
                setOffset(0);
              }}
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500 dark:text-slate-400">Loading tickets...</div>
        </div>
      ) : tickets.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 dark:text-slate-400">No tickets found</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-slate-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">Customer</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">Email</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">Message</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">AI Analysis</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">Assigned To</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
              {tickets.map((ticket) => (
                <tr
                  key={ticket.id}
                  className="hover:bg-gray-50 dark:hover:bg-slate-700 cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedTicket(ticket);
                    setShowDetail(true);
                    setCustomerHistory([]);
                    setShowHistory(false);
                    setReplyMessage(ticket.response || '');
                    setReplyOptions([]);
                    setQualityScore(null);
                    setKbArticles([]);
                    setChurnRisk(null);
                    setFollowupInfo(null);
                    setTicketLanguage(null);
                    setResolutionTime(null);
                    setFeedbackAnalysis(null);
                    setShowFeedbackForm(false);
                    setFeedbackText('');
                    setFeatureError(null);
                  }}
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-slate-100">#{ticket.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-900 dark:text-slate-100 max-w-[100px] truncate">
                    {ticket.customer_name || 'Anonymous'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 dark:text-slate-400 max-w-[100px] truncate">
                    {ticket.customer_email || '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-slate-300 max-w-xs truncate">
                    {ticket.customer_message?.substring(0, 60) || 'No message'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      <span className={`badge ${getBadgeColor('intent', ticket.intent)}`}>
                        {ticket.intent || 'unknown'}
                      </span>
                      <span className={`badge ${getBadgeColor('sentiment', ticket.sentiment)}`}>
                        {ticket.sentiment || 'neutral'}
                      </span>
                      <span className={`badge ${getBadgeColor('priority', ticket.priority)}`}>
                        {ticket.priority || 'low'}
                      </span>
                      {ticket.escalate && (
                        <span className="badge badge-red">Escalated</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${getBadgeColor('status', ticket.status)}`}>
                      {ticket.status || 'new'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 dark:text-slate-400 max-w-[100px] truncate">
                    {ticket.assigned_to || 'Unassigned'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      <select
                        className="text-xs border rounded px-2 py-1 max-w-[80px] bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200"
                        value={ticket.assigned_to || ''}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleAssignTicket(ticket.id, e.target.value);
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <option value="">Unassigned</option>
                        {agentOptions.map((agent) => (
                          <option key={agent} value={agent}>{agent}</option>
                        ))}
                      </select>
                      
                      <select
                        className="text-xs border rounded px-2 py-1 bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200"
                        value={ticket.status}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleUpdateStatus(ticket.id, e.target.value);
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        {getStatusOptions().map((status) => (
                          <option key={status} value={status}>{status}</option>
                        ))}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Controls */}
      {total > limit && (
        <div className="flex items-center justify-between mt-4 flex-wrap gap-2">
          <p className="text-sm text-gray-600 dark:text-slate-400">
            Showing {offset + 1} to {Math.min(offset + limit, total)} of {total} tickets
          </p>
          <div className="flex gap-2">
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => handlePageChange(prevOffset)}
              disabled={prevOffset === null}
            >
              Previous
            </button>
            <span className="text-sm text-gray-600 dark:text-slate-400 flex items-center px-2">
              Page {currentPage} of {totalPages}
            </span>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => handlePageChange(nextOffset)}
              disabled={nextOffset === null}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* New Ticket Modal */}
      {showNewTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white dark:bg-slate-800 rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-slate-100">New Support Ticket</h2>
                <button
                  className="text-gray-400 hover:text-gray-600 dark:text-slate-400 dark:hover:text-slate-200 text-2xl"
                  onClick={() => setShowNewTicket(false)}
                >
                  ×
                </button>
              </div>
              
              <form onSubmit={handleCreateTicket}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-slate-300">Customer Name</label>
                    <input
                      type="text"
                      className="input"
                      placeholder="John Doe"
                      value={newTicket.customer_name}
                      onChange={(e) => setNewTicket({...newTicket, customer_name: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-slate-300">Customer Email</label>
                    <input
                      type="email"
                      className="input"
                      placeholder="john@example.com"
                      value={newTicket.customer_email}
                      onChange={(e) => setNewTicket({...newTicket, customer_email: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-slate-300">Message *</label>
                    <textarea
                      className="input min-h-[100px]"
                      placeholder="Describe the issue..."
                      value={newTicket.customer_message}
                      onChange={(e) => setNewTicket({...newTicket, customer_message: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-slate-300">Product ID (optional)</label>
                    <input
                      type="number"
                      className="input"
                      placeholder="Enter product ID"
                      value={newTicket.product_id}
                      onChange={(e) => setNewTicket({...newTicket, product_id: e.target.value})}
                    />
                  </div>
                  
                  <div className="flex gap-3 pt-4">
                    <button
                      type="submit"
                      className="btn btn-primary flex-1"
                      disabled={submitting}
                    >
                      {submitting ? 'Creating...' : 'Create Ticket'}
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setShowNewTicket(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Ticket Detail Modal */}
      {showDetail && selectedTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white dark:bg-slate-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-slate-100">
                    Ticket #{selectedTicket.id}
                  </h2>
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <span className="text-sm text-gray-600 dark:text-slate-300">{selectedTicket.customer_name || 'Anonymous'}</span>
                    <span className="text-sm text-gray-400 dark:text-slate-500">•</span>
                    <span className="text-sm text-gray-600 dark:text-slate-300">{selectedTicket.customer_email || 'No email'}</span>
                    <span className="text-xs text-gray-400 dark:text-slate-500 ml-2">
                      ({getTimeAgo(selectedTicket.created_at)})
                    </span>
                  </div>
                </div>
                <button
                  className="text-gray-400 hover:text-gray-600 dark:text-slate-400 dark:hover:text-slate-200 text-2xl"
                  onClick={() => setShowDetail(false)}
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500 dark:text-slate-400">Message</p>
                  <p className="text-gray-700 dark:text-slate-200 bg-gray-50 dark:bg-slate-700 p-3 rounded-lg">
                    {selectedTicket.customer_message || 'No message'}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Intent</p>
                    <span className={`badge ${getBadgeColor('intent', selectedTicket.intent)}`}>
                      {selectedTicket.intent || 'unknown'}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Sentiment</p>
                    <span className={`badge ${getBadgeColor('sentiment', selectedTicket.sentiment)}`}>
                      {selectedTicket.sentiment || 'neutral'}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Priority</p>
                    <span className={`badge ${getBadgeColor('priority', selectedTicket.priority)}`}>
                      {selectedTicket.priority || 'low'}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Escalate</p>
                    <span className={`badge ${getBadgeColor('escalate', selectedTicket.escalate)}`}>
                      {selectedTicket.escalate ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>

                {/* SLA Display - NEW */}
                {selectedTicket.sla_status && (
                  <div className="p-3 bg-gray-50 dark:bg-slate-700 rounded-lg border border-gray-200 dark:border-slate-600">
                    <p className="text-sm text-gray-500 dark:text-slate-400">SLA Status</p>
                    <div className="flex items-center gap-2 flex-wrap mt-1">
                      <span className={`badge ${getBadgeColor('sla', selectedTicket.sla_status)}`}>
                        {selectedTicket.sla_status === 'on_track' ? '✅ On Track' : 
                         selectedTicket.sla_status === 'approaching' ? '⚠️ Approaching Deadline' : 
                         '🚨 Breached'}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-slate-400">
                        Response by: {selectedTicket.sla_response_deadline ? new Date(selectedTicket.sla_response_deadline).toLocaleString() : 'N/A'}
                      </span>
                    </div>
                    {selectedTicket.sla_resolution_deadline && (
                      <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
                        Resolution by: {new Date(selectedTicket.sla_resolution_deadline).toLocaleString()}
                      </p>
                    )}
                  </div>
                )}

                {ticketLanguage && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Language</p>
                    <span className="badge badge-blue">
                      {ticketLanguage.language} ({ticketLanguage.confidence}% confidence)
                    </span>
                  </div>
                )}

                {resolutionTime && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Estimated Resolution Time</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="badge badge-blue">
                        {resolutionTime.estimated_hours} hours
                      </span>
                      <span className="text-xs text-gray-500 dark:text-slate-400">
                        ({resolutionTime.minimum_hours} - {resolutionTime.maximum_hours} hours)
                      </span>
                      <span className="text-xs text-gray-500 dark:text-slate-400">
                        Confidence: {resolutionTime.confidence}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">{resolutionTime.reasoning}</p>
                  </div>
                )}

                {churnRisk && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Churn Risk</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`badge ${
                        churnRisk.risk_level === 'critical' ? 'badge-red' :
                        churnRisk.risk_level === 'high' ? 'badge-orange' :
                        churnRisk.risk_level === 'medium' ? 'badge-yellow' :
                        'badge-green'
                      }`}>
                        {churnRisk.risk_level.toUpperCase()} ({churnRisk.churn_risk}%)
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">{churnRisk.recommendation}</p>
                    {churnRisk.factors && churnRisk.factors.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {churnRisk.factors.map((factor, idx) => (
                          <span key={idx} className="badge badge-gray text-xs">{factor}</span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {followupInfo && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">Follow-up Required</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`badge ${followupInfo.needs_followup ? 'badge-yellow' : 'badge-green'}`}>
                        {followupInfo.needs_followup ? 'Yes' : 'No'}
                      </span>
                      {followupInfo.needs_followup && (
                        <>
                          <span className="text-xs text-gray-500 dark:text-slate-400">
                            Timeline: {followupInfo.suggested_timeline}
                          </span>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">{followupInfo.reasoning}</p>
                    {followupInfo.needs_followup && followupInfo.followup_question && (
                      <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                        Suggested follow-up: "{followupInfo.followup_question}"
                      </p>
                    )}
                  </div>
                )}

                {qualityScore && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-slate-400">AI Response Quality</p>
                    <div className="flex items-center gap-4 flex-wrap">
                      <span className="text-lg font-bold text-primary-600 dark:text-primary-400">
                        {qualityScore.overall_score}/10
                      </span>
                      <div className="flex flex-wrap gap-2">
                        <span className="badge badge-green">Clarity: {qualityScore.clarity}/10</span>
                        <span className="badge badge-blue">Empathy: {qualityScore.empathy}/10</span>
                        <span className="badge badge-purple">Completeness: {qualityScore.completeness}/10</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">{qualityScore.recommendation}</p>
                    {qualityScore.strengths && qualityScore.strengths.length > 0 && (
                      <div className="mt-1">
                        <span className="text-xs text-green-600 dark:text-green-400">Strengths: {qualityScore.strengths.join(', ')}</span>
                      </div>
                    )}
                    {qualityScore.improvements && qualityScore.improvements.length > 0 && (
                      <div className="mt-1">
                        <span className="text-xs text-orange-600 dark:text-orange-400">Improvements: {qualityScore.improvements.join(', ')}</span>
                      </div>
                    )}
                  </div>
                )}

                <div>
                  <p className="text-sm text-gray-500 dark:text-slate-400">AI Response</p>
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                    <p className="text-gray-700 dark:text-slate-200">{selectedTicket.response || 'No response generated'}</p>
                  </div>
                </div>

                {replyOptions.length > 0 && (
                  <div className="pt-2">
                    <p className="text-sm font-medium text-gray-700 dark:text-slate-200 mb-2">Reply Options (Click to use)</p>
                    <div className="space-y-2">
                      {replyOptions.map((option, index) => (
                        <div
                          key={index}
                          className="p-3 bg-gray-50 dark:bg-slate-700 rounded-lg border border-gray-200 dark:border-slate-600 hover:border-primary-300 dark:hover:border-primary-500 cursor-pointer transition-colors"
                          onClick={() => {
                            setReplyMessage(option.reply);
                          }}
                        >
                          <div className="flex items-center justify-between flex-wrap">
                            <span className={`badge ${
                              option.tone === 'empathetic' ? 'badge-green' :
                              option.tone === 'direct_professional' ? 'badge-blue' :
                              'badge-purple'
                            }`}>
                              {option.tone}
                            </span>
                            <span className="text-xs text-gray-500 dark:text-slate-400">{option.reasoning}</span>
                          </div>
                          <p className="text-sm text-gray-700 dark:text-slate-200 mt-1">{option.reply}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {kbArticles.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-slate-200 mb-2">Knowledge Base Articles</p>
                    <div className="space-y-1">
                      {kbArticles.map((article, index) => (
                        <div key={index} className="p-2 bg-gray-50 dark:bg-slate-700 rounded-lg text-sm">
                          <span className="font-medium text-gray-900 dark:text-slate-100">{article.title}</span>
                          <p className="text-gray-600 dark:text-slate-300 text-xs">{article.content?.substring(0, 100)}...</p>
                          <span className="badge badge-gray text-xs">{article.category}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <p className="text-sm text-gray-500 dark:text-slate-400 mb-1">Assign to Agent</p>
                  <select
                    className="input max-w-[200px]"
                    value={selectedTicket.assigned_to || ''}
                    onChange={(e) => {
                      const newAgent = e.target.value;
                      handleAssignTicket(selectedTicket.id, newAgent);
                      setSelectedTicket({...selectedTicket, assigned_to: newAgent});
                    }}
                  >
                    <option value="">Unassigned</option>
                    {agentOptions.map((agent) => (
                      <option key={agent} value={agent}>{agent}</option>
                    ))}
                  </select>
                </div>

                {selectedTicket.customer_email && (
                  <div className="pt-2 flex flex-wrap gap-2">
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => fetchCustomerHistory(selectedTicket.customer_email)}
                    >
                      View Customer History
                    </button>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => loadAllAIFeatures(selectedTicket.id)}
                      disabled={loadingFeatures}
                    >
                      {loadingFeatures ? 'Loading AI Features...' : 'Analyze with AI'}
                    </button>
                  </div>
                )}

                {/* Error message for AI features */}
                {featureError && (
                  <div className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg text-sm text-yellow-700 dark:text-yellow-300">
                    ⚠️ {featureError}
                  </div>
                )}

                {showHistory && customerHistory.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 dark:text-slate-200 mb-2">Previous Tickets</h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {customerHistory.map((ticket) => (
                        <div key={ticket.id} className="p-2 bg-gray-50 dark:bg-slate-700 rounded-lg text-sm">
                          <div className="flex justify-between">
                            <span className="font-medium text-gray-900 dark:text-slate-100">#{ticket.id}</span>
                            <span className={`badge ${getBadgeColor('status', ticket.status)}`}>
                              {ticket.status}
                            </span>
                          </div>
                          <p className="text-gray-600 dark:text-slate-300 truncate">{ticket.customer_message}</p>
                          <span className="text-xs text-gray-400 dark:text-slate-500">
                            {new Date(ticket.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200 dark:border-slate-700">
                  <label className="block text-sm font-medium text-gray-700 dark:text-slate-200 mb-2">Reply</label>
                  <textarea
                    className="input min-h-[80px]"
                    placeholder="Type your reply..."
                    value={replyMessage}
                    onChange={(e) => setReplyMessage(e.target.value)}
                  />
                  <div className="flex gap-2 mt-2">
                    <button
                      className="btn btn-primary flex-1"
                      onClick={() => handleSendReply(selectedTicket.id)}
                      disabled={!replyMessage.trim() || sendingReply}
                    >
                      {sendingReply ? 'Sending...' : 'Send Reply'}
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={() => setReplyMessage('')}
                    >
                      Clear
                    </button>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200 dark:border-slate-700">
                  <label className="block text-sm font-medium text-gray-700 dark:text-slate-200 mb-2">Update Status</label>
                  <div className="flex flex-wrap gap-2">
                    {['new', 'in_progress', 'resolved', 'closed'].map((status) => (
                      <button
                        key={status}
                        className={`btn btn-sm ${selectedTicket.status === status ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => {
                          handleUpdateStatus(selectedTicket.id, status);
                          setSelectedTicket({...selectedTicket, status});
                        }}
                      >
                        {status}
                      </button>
                    ))}
                  </div>
                </div>

                {selectedTicket.status === 'resolved' && !feedbackAnalysis && (
                  <div className="pt-4 border-t border-gray-200 dark:border-slate-700">
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setShowFeedbackForm(!showFeedbackForm)}
                    >
                      Add Customer Feedback
                    </button>
                    
                    {showFeedbackForm && (
                      <div className="mt-2">
                        <textarea
                          className="input min-h-[60px]"
                          placeholder="Enter customer feedback..."
                          value={feedbackText}
                          onChange={(e) => setFeedbackText(e.target.value)}
                        />
                        <button
                          className="btn btn-primary btn-sm mt-2"
                          onClick={() => submitFeedback(selectedTicket.id)}
                          disabled={analyzing || !feedbackText.trim()}
                        >
                          {analyzing ? 'Analyzing...' : 'Analyze Feedback'}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {feedbackAnalysis && (
                  <div className="pt-4 border-t border-gray-200 dark:border-slate-700">
                    <p className="text-sm font-medium text-gray-700 dark:text-slate-200 mb-2">Feedback Analysis</p>
                    <div className="p-3 bg-gray-50 dark:bg-slate-700 rounded-lg space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-gray-700 dark:text-slate-200">Sentiment:</span>
                        <span className={`badge ${feedbackAnalysis.sentiment === 'positive' ? 'badge-green' : feedbackAnalysis.sentiment === 'negative' ? 'badge-red' : 'badge-yellow'}`}>
                          {feedbackAnalysis.sentiment}
                        </span>
                        <span className="text-sm font-medium text-gray-700 dark:text-slate-200 ml-4">Satisfaction:</span>
                        <span className="badge badge-blue">{feedbackAnalysis.satisfaction_score}/10</span>
                      </div>
                      {feedbackAnalysis.key_themes && feedbackAnalysis.key_themes.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 dark:text-slate-200">Key Themes:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {feedbackAnalysis.key_themes.map((theme, idx) => (
                              <span key={idx} className="badge badge-gray">{theme}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {feedbackAnalysis.suggestions && feedbackAnalysis.suggestions.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 dark:text-slate-200">Suggestions:</p>
                          <ul className="text-sm text-gray-600 dark:text-slate-300 list-disc pl-4">
                            {feedbackAnalysis.suggestions.map((suggestion, idx) => (
                              <li key={idx}>{suggestion}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}