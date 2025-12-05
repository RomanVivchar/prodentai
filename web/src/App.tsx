import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Home from './pages/Home';
import RiskAssessment from './pages/RiskAssessment';
import Nutrition from './pages/Nutrition';
import Psychology from './pages/Psychology';
import Reminders from './pages/Reminders';
import Facts from './pages/Facts';
import Braces from './pages/Braces';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50 overflow-x-hidden max-w-full">
          <Navbar />
          <main className="container mx-auto px-4 py-8 max-w-full overflow-x-hidden">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/risks" element={<RiskAssessment />} />
              <Route path="/nutrition" element={<Nutrition />} />
              <Route path="/psychology" element={<Psychology />} />
              <Route path="/reminders" element={<Reminders />} />
              <Route path="/facts" element={<Facts />} />
              <Route path="/braces" element={<Braces />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </main>
          <Toaster position="top-right" />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
