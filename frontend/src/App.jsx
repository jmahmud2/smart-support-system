import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { DarkModeProvider } from './context/DarkModeContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Tickets from './pages/Tickets';
import AgentDashboard from './pages/AgentDashboard';
import Login from './pages/Login';
import CustomerSubmit from './pages/CustomerSubmit';
import CustomerTrack from './pages/CustomerTrack';

function App() {
  return (
    <DarkModeProvider>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Layout>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            {/* Public Customer Routes */}
            <Route path="/customer/submit" element={<CustomerSubmit />} />
            <Route path="/customer/track" element={<CustomerTrack />} />
            
            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/products" element={
              <ProtectedRoute>
                <Products />
              </ProtectedRoute>
            } />
            <Route path="/tickets" element={
              <ProtectedRoute>
                <Tickets />
              </ProtectedRoute>
            } />
            <Route path="/agent" element={
              <ProtectedRoute>
                <AgentDashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </Layout>
      </Router>
    </DarkModeProvider>
  );
}

export default App;