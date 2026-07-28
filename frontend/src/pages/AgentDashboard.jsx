import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Link } from 'react-router-dom';

export default function AgentDashboard() {
  const [myTickets, setMyTickets] = useState([]);
  const [unassignedTickets, setUnassignedTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState(null);
  const [stats, setStats] = useState({
    myOpen: 0,
    resolvedToday: 0,
    pendingReplies: 0
  });
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [replyMessage, setReplyMessage] = useState('');
  const [sendingReply, setSendingReply] = useState(false);
  const [customerHistory, setCustomerHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  
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
  
  const [agentOptions, setAgentOptions] = useState([]);

  useEffect(() => {
    fetchAgents();
    fetchAgentInfo();
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

  const fetchAgentInfo = async () => {
    try {
      const agentResponse = await apiClient.get('/support/agent/me');
      setAgent(agentResponse.data);
      await fetchAgentData(agentResponse.data.name);
    } catch (error) {
      console.error('Error fetching agent info:', error);
      setAgent({ name: 'Sarah Johnson', role: 'agent' });
      await fetchAgentData('Sarah Johnson');
    }
  };

  const fetchAgentData = async (agentName) => {
    setLoading(true);
    try {
      const response = await apiClient.get('/support/tickets', {
        params: { limit: 100, offset: 0 }
      });
      const allTickets = response.data.data || [];

      const my = allTickets.filter(t => t.assigned_to === agentName);
      setMyTickets(my);

      const unassigned = allTickets.filter(t => 
        !t.assigned_to && (t.status === 'new' || t.status === 'in_progress')
      );
      setUnassignedTickets(unassigned);

      const myOpen = my.filter(t => t.status === 'new' || t.status === 'in_progress').length;
      const resolvedToday = my.filter(t => {
        if (!t.resolved_at) return false;
        const today = new Date().toDateString();
        const resolvedDate = new Date(t.resolved_at).toDateString();
        return resolvedDate === today;
      }).length;
      const pendingReplies = my.filter(t => t.status === 'in_progress').length;

      setStats({ myOpen, resolvedToday, pendingReplies });

    } catch (error) {
      console.error('Error fetching agent data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignToSelf = async (ticketId) => {
    if (!agent) return;
    try {
      await apiClient.patch(`/support/tickets/${ticketId}/assign`, null, {
        params: { agent_name: agent.name }
      });
      fetchAgentData(agent.name);
    } catch (error) {
      console.error('Error assigning ticket:', error);
      alert('Failed to assign ticket');
    }
  };

  const handleAssignTicket = async (ticketId, agentName) => {
    try {
      await apiClient.patch(`/support/tickets/${ticketId}/assign`, null, {
        params: { agent_name: agentName }
      });
      if (agent) {
        fetchAgentData(agent.name);
      }
    } catch (error) {
      console.error('Error assigning ticket:', error);
      alert('Failed to assign ticket');
    }
  };

  const handleUpdateStatus = async (ticketId, newStatus) => {
    try {
      await apiClient.patch(`/support/tickets/${ticketId}/status`, null, {
        params: { status: newStatus }
      });
      if (agent) {
        fetchAgentData(agent.name);
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status');
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
      setShowDetail(false);
      if (agent) {
        fetchAgentData(agent.name);
      }
      alert('Reply sent successfully!');
    } catch (error) {
      console.error('Error sending reply:', error);
      alert('Failed to send reply');
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

  const fetchReplyOptions = async (ticketId) => {
    if (!ticketId) return;
    setLoadingFeatures(true);
    try {
      const response = await apiClient.post(`/support/tickets/${ticketId}/reply-options`);
      setReplyOptions(response.data.options || []);
    } catch (error) {
      console.error('Error fetching reply options:', error);
    } finally {
      setLoadingFeatures(false);
    }
  };

  const evaluateResponse = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.post(`/support/tickets/${ticketId}/evaluate-response`);
      setQualityScore(response.data.quality_score);
    } catch (error) {
      console.error('Error evaluating response:', error);
    }
  };

  const fetchKnowledgeBase = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/knowledge-base`);
      setKbArticles(response.data.articles || []);
    } catch (error) {
      console.error('Error fetching knowledge base:', error);
    }
  };

  const fetchChurnRisk = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/churn-risk`);
      setChurnRisk(response.data.churn_risk);
    } catch (error) {
      console.error('Error fetching churn risk:', error);
    }
  };

  const fetchFollowupInfo = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/followup`);
      setFollowupInfo(response.data.followup);
    } catch (error) {
      console.error('Error fetching followup info:', error);
    }
  };

  const fetchLanguage = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/language`);
      setTicketLanguage(response.data.language);
    } catch (error) {
      console.error('Error fetching language:', error);
    }
  };

  const fetchResolutionTime = async (ticketId) => {
    if (!ticketId) return;
    try {
      const response = await apiClient.get(`/support/tickets/${ticketId}/resolution-time`);
      setResolutionTime(response.data.resolution_time);
    } catch (error) {
      console.error('Error fetching resolution time:', error);
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
      console.error('Error loading AI features:', error);
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
    return 'badge-gray';
  };

  const getTimeAgo = (createdAt) => {
    const hours = Math.floor((Date.now() - new Date(createdAt)) / (1000 * 60 * 60));
    if (hours < 1) return 'Just now';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    return new Date(createdAt).toLocaleDateString();
  };

  if (loading || !agent) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 dark:text-slate-400">Loading your dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Welcome back, {agent.name}</h1>
            <p className="text-gray-600 dark:text-slate-400 mt-1">Here's what you need to work on today</p>
          </div>
          <Link to="/tickets" className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300">
            View All Tickets →
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-slate-400">My Open Tickets</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{stats.myOpen}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-slate-400">Resolved Today</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.resolvedToday}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 dark:text-slate-400">Pending Replies</p>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.pendingReplies}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">My Tickets ({myTickets.length})</h2>
          
          {myTickets.length === 0 ? (
            <p className="text-gray-500 dark:text-slate-400 text-sm">No tickets assigned to you yet.</p>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {myTickets.slice(0, 10).map((ticket) => (
                <div 
                  key={ticket.id} 
                  className="ticket-card p-3 rounded-lg cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedTicket(ticket);
                    setShowDetail(true);
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
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                        #{ticket.id} - {ticket.customer_name || 'Anonymous'}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-slate-300 truncate">
                        {ticket.customer_message?.substring(0, 60)}...
                      </p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        <span className={`badge ${getBadgeColor('status', ticket.status)}`}>
                          {ticket.status}
                        </span>
                        <span className={`badge ${getBadgeColor('priority', ticket.priority)}`}>
                          {ticket.priority}
                        </span>
                        <span className={`badge ${getBadgeColor('sentiment', ticket.sentiment)}`}>
                          {ticket.sentiment}
                        </span>
                        {ticket.escalate && (
                          <span className="badge badge-red">Escalated</span>
                        )}
                      </div>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-slate-400 ml-2 whitespace-nowrap">
                      {getTimeAgo(ticket.created_at)}
                    </span>
                  </div>
                  <div className="flex gap-2 mt-2">
                    <select
                      className="text-xs border rounded px-2 py-1 bg-white dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200"
                      value={ticket.status}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleUpdateStatus(ticket.id, e.target.value);
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <option value="new">New</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
                    </select>
                    <button
                      className="text-xs btn btn-primary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedTicket(ticket);
                        setShowDetail(true);
                        setReplyMessage(ticket.response || '');
                      }}
                    >
                      Reply
                    </button>
                  </div>
                </div>
              ))}
              {myTickets.length > 10 && (
                <p className="text-xs text-gray-500 dark:text-slate-400 text-center">
                  Showing 10 of {myTickets.length} tickets
                </p>
              )}
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Available Queue ({unassignedTickets.length})</h2>
          
          {unassignedTickets.length === 0 ? (
            <p className="text-gray-500 dark:text-slate-400 text-sm">No unassigned tickets in the queue.</p>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {unassignedTickets.slice(0, 10).map((ticket) => (
                <div 
                  key={ticket.id} 
                  className="queue-card p-3 rounded-lg cursor-pointer transition-colors border"
                  onClick={() => {
                    setSelectedTicket(ticket);
                    setShowDetail(true);
                    setReplyMessage(ticket.response || '');
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                        #{ticket.id} - {ticket.customer_name || 'Anonymous'}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-slate-300 truncate">
                        {ticket.customer_message?.substring(0, 60)}...
                      </p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        <span className={`badge ${getBadgeColor('priority', ticket.priority)}`}>
                          {ticket.priority}
                        </span>
                        <span className={`badge ${getBadgeColor('sentiment', ticket.sentiment)}`}>
                          {ticket.sentiment}
                        </span>
                        {ticket.escalate && (
                          <span className="badge badge-red">Escalated</span>
                        )}
                      </div>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-slate-400 ml-2 whitespace-nowrap">
                      {getTimeAgo(ticket.created_at)}
                    </span>
                  </div>
                  <button
                    className="btn btn-primary btn-sm w-full mt-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAssignToSelf(ticket.id);
                    }}
                  >
                    Assign to Me
                  </button>
                </div>
              ))}
              {unassignedTickets.length > 10 && (
                <p className="text-xs text-gray-500 dark:text-slate-400 text-center">
                  Showing 10 of {unassignedTickets.length} tickets
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Ticket Detail Modal - Fixed for dark mode */}
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

                {/* AI Response */}
                <div>
                  <p className="text-sm text-gray-500 dark:text-slate-400">AI Response</p>
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                    <p className="text-gray-700 dark:text-slate-200">{selectedTicket.response || 'No response generated'}</p>
                  </div>
                </div>

                {/* Assign in Modal */}
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
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}