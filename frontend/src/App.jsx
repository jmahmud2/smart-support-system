import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Tickets from './pages/Tickets';
import SubmitTicket from './pages/SubmitTicket';
import AgentDashboard from './pages/AgentDashboard';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/tickets" element={<Tickets />} />
          <Route path="/submit" element={<SubmitTicket />} />
          <Route path="/agent" element={<AgentDashboard />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;