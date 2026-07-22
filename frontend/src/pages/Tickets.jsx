import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState('');
  const [intentFilter, setIntentFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Pagination
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [totalTickets, setTotalTickets] = useState(0);
  
  // New ticket form
  const [showNewTicket, setShowNewTicket] = useState(false);
  const [newTicket, setNewTicket] = useState({
    customer_name: '',
    customer_email: '',
    customer_message: '',
    product_id: ''
  });
  const [submitting, setSubmitting] = useState(false);

  // Fetch tickets on load and filter changes
  useEffect(() => {
    fetchTickets();
  }, [statusFilter, intentFilter, offset, limit]);

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
      setTickets(response.data || []);
      // Note: API doesn't return total count, so we'll estimate
      setTotalTickets(tickets.length + (response.data.length === limit ? limit : 0));
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

  const getStatusOptions = () => {
    return ['new', 'in_progress', 'resolved', 'closed'];
  };

  const getIntentOptions = () => {
    return ['refund', 'shipping', 'product_inquiry', 'complaint', 'general'];
  };

  // Filter tickets by search term
  const filteredTickets = tickets.filter(ticket => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      (ticket.customer_message || '').toLowerCase().includes(search) ||
      (ticket.customer_name || '').toLowerCase().includes(search) ||
      (ticket.intent || '').toLowerCase().includes(search)
    );
  });

  return (
    <div>
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support Tickets</h1>
          <p className="text-gray-600 mt-1">Manage and track customer support tickets</p>
        </div>
        <button
          className="btn btn-primary mt-4 sm:mt-0"
          onClick={() => setShowNewTicket(true)}
        >
          + New Ticket
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="flex gap-2">
              <input
                type="text"
                className="input flex-1"
                placeholder="Search messages..."
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

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
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

          {/* Intent Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Intent</label>
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

          {/* Show per page */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Show</label>
            <select
              className="input"
              value={limit}
              onChange={(e) => {
                setLimit(parseInt(e.target.value));
                setOffset(0);
              }}
            >
              <option value="10">10 per page</option>
              <option value="20">20 per page</option>
              <option value="50">50 per page</option>
            </select>
          </div>
        </div>

        {/* Clear filters */}
        {(statusFilter || intentFilter || searchTerm) && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              className="text-sm text-primary-600 hover:text-primary-700"
              onClick={() => {
                setStatusFilter('');
                setIntentFilter('');
                setSearchTerm('');
                setOffset(0);
              }}
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>

      {/* Tickets Table */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading tickets...</div>
        </div>
      ) : filteredTickets.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No tickets found</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Intent</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Escalate</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredTickets.map((ticket) => (
                <tr
                  key={ticket.id}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedTicket(ticket);
                    setShowDetail(true);
                  }}
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">#{ticket.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                    {ticket.customer_message?.substring(0, 60) || 'No message'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${getBadgeColor('sentiment', ticket.intent)}`}>
                      {ticket.intent || 'unknown'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${getBadgeColor('status', ticket.status)}`}>
                      {ticket.status || 'new'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${getBadgeColor('priority', ticket.priority)}`}>
                      {ticket.priority || 'low'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${getBadgeColor('escalate', ticket.escalate)}`}>
                      {ticket.escalate ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      <select
                        className="text-xs border rounded px-2 py-1"
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

      {/* Pagination */}
      {totalTickets > limit && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-600">
            Showing {offset + 1} to {Math.min(offset + limit, totalTickets)} of {totalTickets}
          </p>
          <div className="flex gap-2">
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
            >
              Previous
            </button>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setOffset(offset + limit)}
              disabled={offset + limit >= totalTickets}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* New Ticket Modal */}
      {showNewTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">New Support Ticket</h2>
                <button
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                  onClick={() => setShowNewTicket(false)}
                >
                  ×
                </button>
              </div>
              
              <form onSubmit={handleCreateTicket}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Customer Name</label>
                    <input
                      type="text"
                      className="input"
                      placeholder="John Doe"
                      value={newTicket.customer_name}
                      onChange={(e) => setNewTicket({...newTicket, customer_name: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Customer Email</label>
                    <input
                      type="email"
                      className="input"
                      placeholder="john@example.com"
                      value={newTicket.customer_email}
                      onChange={(e) => setNewTicket({...newTicket, customer_email: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Message *</label>
                    <textarea
                      className="input min-h-[100px]"
                      placeholder="Describe the issue..."
                      value={newTicket.customer_message}
                      onChange={(e) => setNewTicket({...newTicket, customer_message: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Product ID (optional)</label>
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
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Ticket #{selectedTicket.id}
                </h2>
                <button
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                  onClick={() => setShowDetail(false)}
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">Customer</p>
                  <p className="font-medium">{selectedTicket.customer_name || 'Anonymous'}</p>
                  <p className="text-sm text-gray-600">{selectedTicket.customer_email || 'No email'}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Message</p>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {selectedTicket.customer_message || 'No message'}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Intent</p>
                    <span className={`badge ${getBadgeColor('sentiment', selectedTicket.intent)}`}>
                      {selectedTicket.intent || 'unknown'}
                    </span>
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
                  <div>
                    <p className="text-sm text-gray-500">Escalate</p>
                    <span className={`badge ${getBadgeColor('escalate', selectedTicket.escalate)}`}>
                      {selectedTicket.escalate ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">AI Response</p>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-gray-700">{selectedTicket.response || 'No response generated'}</p>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Reasoning</p>
                  <p className="text-gray-600 text-sm">{selectedTicket.reasoning || 'No reasoning provided'}</p>
                </div>
                
                <div className="pt-4 border-t border-gray-200">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Update Status</label>
                  <div className="flex gap-2">
                    {getStatusOptions().map((status) => (
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