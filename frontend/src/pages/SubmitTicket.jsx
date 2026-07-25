import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

export default function SubmitTicket() {
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.customer_message.trim()) {
      alert('Please enter your message');
      return;
    }

    setSubmitting(true);
    try {
      const response = await apiClient.post('/support/tickets', formData);
      setTicketId(response.data.id);
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting ticket:', error);
      alert('Failed to submit ticket. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <div className="card text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Ticket Submitted!</h2>
          <p className="text-gray-600 mb-4">
            Your support ticket has been received. Our team will review it and get back to you shortly.
          </p>
          <p className="text-sm text-gray-500">
            Ticket #{ticketId}
          </p>
          <button
            className="btn btn-primary mt-4"
            onClick={() => navigate('/')}
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Submit a Support Ticket</h1>
        <p className="text-gray-600 mb-6">
          Fill out the form below and our team will assist you as soon as possible.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Your Email</label>
            <input
              type="email"
              name="customer_email"
              className="input"
              placeholder="john@example.com"
              value={formData.customer_email}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Message *</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Product ID (optional)</label>
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
      </div>
    </div>
  );
}