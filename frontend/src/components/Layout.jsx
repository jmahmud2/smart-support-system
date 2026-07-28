import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useDarkMode } from '../context/DarkModeContext';
import NotificationBell from './NotificationBell';

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Agent Dashboard', href: '/agent' },
  { name: 'Products', href: '/products' },
  { name: 'Tickets', href: '/tickets' },
];

const publicNavigation = [
  { name: 'Submit Ticket', href: '/customer/submit' },
  { name: 'Track Tickets', href: '/customer/track' },
];

export default function Layout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState(null);
  const { darkMode, toggleDarkMode } = useDarkMode();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  // Check if current path is a public customer page
  const isPublicPage = location.pathname.startsWith('/customer/');

  if (location.pathname === '/login') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex flex-col transition-colors duration-200">
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <nav className="bg-white dark:bg-slate-800 shadow-sm sticky top-0 z-50 border-b border-gray-200 dark:border-slate-700 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center gap-2">
                <span className="text-2xl font-bold text-primary-600 dark:text-primary-400 hidden sm:block">
                  SmartSupport
                </span>
                <span className="text-2xl font-bold text-primary-600 dark:text-primary-400 sm:hidden">
                  SS
                </span>
              </Link>
            </div>

            <div className="hidden lg:flex lg:items-center lg:gap-4">
              {/* Show different navigation based on user role */}
              {user ? (
                <>
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`nav-link ${isActive(item.href) ? 'nav-link-active' : 'nav-link-inactive'}`}
                    >
                      {item.name}
                    </Link>
                  ))}
                </>
              ) : (
                <>
                  {publicNavigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`nav-link ${isActive(item.href) ? 'nav-link-active' : 'nav-link-inactive'}`}
                    >
                      {item.name}
                    </Link>
                  ))}
                </>
              )}
              
              <NotificationBell />
              
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-700 transition-colors"
                aria-label="Toggle dark mode"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
              
              {user ? (
                <div className="flex items-center gap-4 ml-4 pl-4 border-l border-gray-200 dark:border-slate-700">
                  <span className="text-sm text-gray-600 dark:text-slate-300">
                    {user.name} ({user.role})
                  </span>
                  <button
                    onClick={handleLogout}
                    className="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 font-medium"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-lg text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                >
                  Sign In
                </Link>
              )}
            </div>

            <div className="flex items-center lg:hidden gap-2">
              <NotificationBell />
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-700"
                aria-label="Toggle dark mode"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
              {user && (
                <span className="text-xs text-gray-500 dark:text-slate-400">{user.name}</span>
              )}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-700"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? '✕' : '☰'}
              </button>
            </div>
          </div>
        </div>

        <div
          className={`lg:hidden fixed top-16 left-0 right-0 bg-white dark:bg-slate-800 shadow-lg z-50 transition-transform duration-300 border-b border-gray-200 dark:border-slate-700 ${
            mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className="px-4 py-4 space-y-2">
            {user ? (
              <>
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-4 py-3 rounded-lg text-base font-medium ${
                      isActive(item.href)
                        ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-700'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              </>
            ) : (
              <>
                {publicNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-4 py-3 rounded-lg text-base font-medium ${
                      isActive(item.href)
                        ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-700'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              </>
            )}
            {user ? (
              <>
                <div className="px-4 py-2 text-sm text-gray-500 dark:text-slate-400">
                  {user.name} ({user.role})
                </div>
                <button
                  onClick={() => {
                    handleLogout();
                    setMobileMenuOpen(false);
                  }}
                  className="block w-full text-left px-4 py-3 rounded-lg text-base font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/30"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-4 py-3 rounded-lg text-base font-medium text-white bg-primary-600 hover:bg-primary-700"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </nav>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {children}
      </main>

      <footer className="bg-white dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500 dark:text-slate-400">
            Smart Support System &copy; {new Date().getFullYear()} — AI-powered customer support
          </p>
        </div>
      </footer>
    </div>
  );
}