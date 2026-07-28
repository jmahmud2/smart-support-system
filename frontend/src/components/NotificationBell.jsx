import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function NotificationBell() {
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      checkNotifications();
    }, 30000);

    checkNotifications();

    return () => clearInterval(interval);
  }, []);

  const checkNotifications = async () => {
    try {
      const response = await apiClient.get('/support/tickets?limit=10');
      let tickets = [];
      if (response.data.data) {
        tickets = response.data.data;
      } else if (response.data.value) {
        tickets = response.data.value;
      }

      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      const newTickets = tickets.filter(t => 
        t.status === 'new' && t.assigned_to === currentUser.name
      );

      setNotifications(newTickets);
      setUnreadCount(newTickets.length);
    } catch (error) {
      console.error('Error checking notifications:', error);
    }
  };

  const markAsRead = () => {
    setUnreadCount(0);
    setShowDropdown(false);
  };

  const getTimeAgo = (createdAt) => {
    const hours = Math.floor((Date.now() - new Date(createdAt)) / (1000 * 60 * 60));
    if (hours < 1) return 'Just now';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    return new Date(createdAt).toLocaleDateString();
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-700 relative transition-colors"
        aria-label="Notifications"
      >
        🔔
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-200 dark:border-slate-700 z-50 max-h-96 overflow-y-auto">
          <div className="p-3 border-b border-gray-200 dark:border-slate-700 flex justify-between items-center">
            <span className="font-semibold text-gray-900 dark:text-slate-100">Notifications</span>
            <button
              onClick={markAsRead}
              className="text-sm text-primary-600 dark:text-primary-400 hover:underline"
            >
              Mark all read
            </button>
          </div>
          {notifications.length === 0 ? (
            <div className="p-4 text-center text-gray-500 dark:text-slate-400">
              No new notifications
            </div>
          ) : (
            notifications.map((ticket) => (
              <div key={ticket.id} className="p-3 border-b border-gray-100 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors">
                <div className="flex items-start gap-2">
                  <span className="text-xl">🎫</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-slate-100">
                      Ticket #{ticket.id}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-slate-400">
                      {ticket.customer_name || 'Anonymous'} • {getTimeAgo(ticket.created_at)}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-slate-300 truncate mt-1">
                      {ticket.customer_message?.substring(0, 60)}...
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}