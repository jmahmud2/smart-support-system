import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

export default function CustomerSubmit() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_email: '',
    customer_message: '',
    product_id: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [ticketId, setTicketId] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.customer_message.trim()) {
      setError('Please enter your message');
      return;
    }
    if (!formData.customer_email.trim()) {
      setError('Please enter your email');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const response = await apiClient.post('/support/tickets', formData);
      setTicketId(response.data.id);
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting ticket:', error);
      setError('Failed to submit ticket. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <div className="card text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2">Ticket Submitted!</h2>
          <p className="text-gray-600 dark:text-slate-300 mb-4">
            Your support ticket has been received. Our team will review it and get back to you shortly.
          </p>
          <p className="text-sm text-gray-500 dark:text-slate-400">
            Ticket #{ticketId}
          </p>
          <div className="mt-4 space-y-2">
            <button
              className="btn btn-primary w-full"
              onClick={() => navigate('/customer/track')}
            >
              Track Your Ticket
            </button>
            <button
              className="btn btn-secondary w-full"
              onClick={() => navigate('/')}
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2">Submit a Support Ticket</h1>
        <p className="text-gray-600 dark:text-slate-300 mb-6">
          Fill out the form below and our team will assist you as soon as possible.
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-300 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
              Your Name <span className="text-gray-400">(optional)</span>
            </label>
            <input
              type="text"
              name="customer_name"
              className="input"
              placeholder="John Doe"
              value={formData.customer_name}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
              Your Email *
            </label>
            <input
              type="email"
              name="customer_email"
              className="input"
              placeholder="john@example.com"
              value={formData.customer_email}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
              Message *
            </label>
            <textarea
              name="customer_message"
              className="input min-h-[150px]"
              placeholder="Describe your issue..."
              value={formData.customer_message}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
              Product ID <span className="text-gray-400">(optional)</span>
            </label>
            <input
              type="number"
              name="product_id"
              className="input"
              placeholder="Enter product ID"
              value={formData.product_id}
              onChange={handleChange}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Ticket'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500 dark:text-slate-400">
            Already have a ticket?{' '}
            <button
              onClick={() => navigate('/customer/track')}
              className="text-primary-600 dark:text-primary-400 hover:underline"
            >
              Track it here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}