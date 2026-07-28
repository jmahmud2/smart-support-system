import { useState } from 'react';
import apiClient from '../api/client';

export default function CustomerTrack() {
  const [email, setEmail] = useState('');
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Please enter your email');
      return;
    }

    setLoading(true);
    setError('');
    setSearched(true);

    try {
      const response = await apiClient.get(`/support/tickets/customer/${email}`);
      setTickets(response.data);
      if (response.data.length === 0) {
        setError('No tickets found for this email');
      }
    } catch (error) {
      console.error('Error fetching tickets:', error);
      setError('Failed to fetch tickets. Please try again.');
      setTickets([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      'new': 'badge-yellow',
      'in_progress': 'badge-blue',
      'resolved': 'badge-green',
      'closed': 'badge-gray'
    };
    return colors[status] || 'badge-gray';
  };

  const getTimeAgo = (createdAt) => {
    const hours = Math.floor((Date.now() - new Date(createdAt)) / (1000 * 60 * 60));
    if (hours < 1) return 'Just now';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    return new Date(createdAt).toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto py-12">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2">Track Your Tickets</h1>
        <p className="text-gray-600 dark:text-slate-300 mb-6">
          Enter your email to view all your support tickets and their status.
        </p>

        <form onSubmit={handleSearch} className="flex gap-2 mb-6">
          <input
            type="email"
            className="input flex-1"
            placeholder="Enter your email..."
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && (
          <div className={`p-3 rounded-lg text-sm ${searched && tickets.length === 0 ? 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-600 dark:text-yellow-300' : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-300'}`}>
            {error}
          </div>
        )}

        {tickets.length > 0 && (
          <div className="mt-6 space-y-4">
            <p className="text-sm text-gray-500 dark:text-slate-400">
              Found {tickets.length} ticket{tickets.length > 1 ? 's' : ''}
            </p>
            {tickets.map((ticket) => (
              <div key={ticket.id} className="p-4 bg-gray-50 dark:bg-slate-700 rounded-lg border border-gray-200 dark:border-slate-600">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="font-medium text-gray-900 dark:text-slate-100">
                        Ticket #{ticket.id}
                      </span>
                      <span className={`badge ${getStatusBadge(ticket.status)}`}>
                        {ticket.status}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-slate-400">
                        {getTimeAgo(ticket.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-slate-300 mt-2">
                      {ticket.customer_message?.substring(0, 150)}
                      {ticket.customer_message?.length > 150 && '...'}
                    </p>
                    {ticket.response && (
                      <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                          <span className="font-medium">Response:</span> {ticket.response}
                        </p>
                      </div>
                    )}
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className={`badge ${getStatusBadge(ticket.status)}`}>
                        {ticket.intent || 'general'}
                      </span>
                      <span className={`badge ${ticket.escalate ? 'badge-red' : 'badge-green'}`}>
                        {ticket.escalate ? 'Escalated' : 'Auto'}
                      </span>
                    </div>
                  </div>
                  <div className="text-right text-xs text-gray-400 dark:text-slate-500">
                    {ticket.resolved_at ? 'Resolved' : 'Active'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}