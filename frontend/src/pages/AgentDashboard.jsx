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

  useEffect(() => {
    fetchAgentInfo();
  }, []);

  const fetchAgentInfo = async () => {
    try {
      // Get current agent info
      const agentResponse = await apiClient.get('/support/agent/me');
      setAgent(agentResponse.data);
      
      // Then fetch tickets
      await fetchAgentData(agentResponse.data.name);
    } catch (error) {
      console.error('Error fetching agent info:', error);
      // Fallback to default
      setAgent({ name: 'Sarah Johnson', role: 'agent' });
      await fetchAgentData('Sarah Johnson');
    }
  };

  const fetchAgentData = async (agentName) => {
    setLoading(true);
    try {
      // Get all tickets
      const response = await apiClient.get('/support/tickets', {
        params: { limit: 100, offset: 0 }
      });
      const allTickets = response.data || [];

      // Filter: My tickets
      const my = allTickets.filter(t => t.assigned_to === agentName);
      setMyTickets(my);

      // Filter: Unassigned tickets (new or in_progress without assignment)
      const unassigned = allTickets.filter(t => 
        !t.assigned_to && (t.status === 'new' || t.status === 'in_progress')
      );
      setUnassignedTickets(unassigned);

      // Calculate stats
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

  const getBadgeColor = (type, value) => {
    if (type === 'status') {
      switch(value) {
        case 'new': return 'badge-yellow';
        case 'in_progress': return 'badge-blue';
        case 'resolved': return 'badge-green';
        case 'closed': return 'badge-gray';
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
    if (type === 'sentiment') {
      switch(value) {
        case 'positive': return 'badge-green';
        case 'neutral': return 'badge-yellow';
        case 'negative': return 'badge-red';
        default: return 'badge-gray';
      }
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
        <div className="text-gray-500">Loading your dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">👋 Welcome back, {agent.name}</h1>
            <p className="text-gray-600 mt-1">Here's what you need to work on today</p>
          </div>
          <Link to="/tickets" className="text-sm text-primary-600 hover:text-primary-700">
            View All Tickets →
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500">My Open Tickets</p>
          <p className="text-2xl font-bold text-primary-600">{stats.myOpen}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Resolved Today</p>
          <p className="text-2xl font-bold text-green-600">{stats.resolvedToday}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Pending Replies</p>
          <p className="text-2xl font-bold text-yellow-600">{stats.pendingReplies}</p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* My Tickets */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">📋 My Tickets ({myTickets.length})</h2>
          
          {myTickets.length === 0 ? (
            <p className="text-gray-500 text-sm">No tickets assigned to you yet.</p>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {myTickets.slice(0, 10).map((ticket) => (
                <div 
                  key={ticket.id} 
                  className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  onClick={() => {
                    setSelectedTicket(ticket);
                    setShowDetail(true);
                    setReplyMessage(ticket.response || '');
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        #{ticket.id} - {ticket.customer_name || 'Anonymous'}
                      </p>
                      <p className="text-sm text-gray-600 truncate">
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
                    <span className="text-xs text-gray-500 ml-2 whitespace-nowrap">
                      {getTimeAgo(ticket.created_at)}
                    </span>
                  </div>
                  <div className="flex gap-2 mt-2">
                    <select
                      className="text-xs border rounded px-2 py-1"
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
                <p className="text-xs text-gray-500 text-center">
                  Showing 10 of {myTickets.length} tickets
                </p>
              )}
            </div>
          )}
        </div>

        {/* Unassigned Queue */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">📥 Available Queue ({unassignedTickets.length})</h2>
          
          {unassignedTickets.length === 0 ? (
            <p className="text-gray-500 text-sm">No unassigned tickets in the queue.</p>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {unassignedTickets.slice(0, 10).map((ticket) => (
                <div 
                  key={ticket.id} 
                  className="p-3 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors cursor-pointer border border-yellow-200"
                  onClick={() => {
                    setSelectedTicket(ticket);
                    setShowDetail(true);
                    setReplyMessage(ticket.response || '');
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        #{ticket.id} - {ticket.customer_name || 'Anonymous'}
                      </p>
                      <p className="text-sm text-gray-600 truncate">
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
                    <span className="text-xs text-gray-500 ml-2 whitespace-nowrap">
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
                    📌 Assign to Me
                  </button>
                </div>
              ))}
              {unassignedTickets.length > 10 && (
                <p className="text-xs text-gray-500 text-center">
                  Showing 10 of {unassignedTickets.length} tickets
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Ticket Detail Modal */}
      {showDetail && selectedTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    Ticket #{selectedTicket.id}
                  </h2>
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <span className="text-sm text-gray-600">{selectedTicket.customer_name || 'Anonymous'}</span>
                    <span className="text-sm text-gray-400">•</span>
                    <span className="text-sm text-gray-600">{selectedTicket.customer_email || 'No email'}</span>
                    <span className="text-xs text-gray-400 ml-2">
                      ({getTimeAgo(selectedTicket.created_at)})
                    </span>
                  </div>
                </div>
                <button
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                  onClick={() => setShowDetail(false)}
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">Message</p>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {selectedTicket.customer_message || 'No message'}
                  </p>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Intent</p>
                    <p className="text-sm font-medium">{selectedTicket.intent || 'unknown'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Sentiment</p>
                    <span className={`badge ${getBadgeColor('sentiment', selectedTicket.sentiment)}`}>
                      {selectedTicket.sentiment || 'neutral'}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Priority</p>
                    <span className={`badge ${getBadgeColor('priority', selectedTicket.priority)}`}>
                      {selectedTicket.priority || 'low'}
                    </span>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">AI Response</p>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-gray-700">{selectedTicket.response || 'No response generated'}</p>
                  </div>
                </div>

                {/* Reply Section */}
                <div className="pt-4 border-t border-gray-200">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Reply</label>
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

                <div className="pt-4 border-t border-gray-200">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Update Status</label>
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