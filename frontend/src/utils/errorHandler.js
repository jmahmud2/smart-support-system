export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  if (error.response) {
    const { status, data } = error.response;
    
    if (status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return 'Session expired. Please log in again.';
    }
    
    if (status === 403) {
      return 'You do not have permission to perform this action.';
    }
    
    if (status === 429) {
      return 'Too many requests. Please wait a moment.';
    }
    
    return data?.detail || data?.message || defaultMessage;
  }
  
  if (error.request) {
    return 'Network error. Please check your connection.';
  }
  
  return defaultMessage;
};

export const showToast = (message, type = 'info') => {
  const toastEvent = new CustomEvent('showToast', { detail: { message, type } });
  window.dispatchEvent(toastEvent);
};