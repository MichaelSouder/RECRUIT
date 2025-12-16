import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { CreditCard } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loginWithPIV, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      // Handle FastAPI validation errors (array format)
      const errorDetail = err.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        const errorMessages = errorDetail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        setError(errorMessages || 'Login failed');
      } else if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError('Login failed. Please check your credentials.');
      }
    }
  };

  const handlePIVLogin = async () => {
    setError('');
    
    try {
      // Request client certificate from browser
      // Note: This requires the server to be configured for client certificate authentication
      // For now, we'll use a prompt-based approach where the user enters their certificate ID
      // In a production environment with proper mTLS setup, the certificate would be extracted automatically
      
      const certificateId = prompt('Please enter your PIV certificate identifier (CN or SAN):');
      if (!certificateId) {
        return;
      }
      
      await loginWithPIV(certificateId);
      navigate('/');
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail;
      if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError('PIV login failed. Please check your certificate identifier.');
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            RECRUIT Study Platform
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="admin@recruit.com"
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="admin123"
            />
          </div>
          <div className="space-y-3">
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Sign in
            </Button>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">Or</span>
              </div>
            </div>
            <Button 
              type="button" 
              variant="secondary" 
              className="w-full flex items-center justify-center space-x-2"
              onClick={handlePIVLogin}
              isLoading={isLoading}
            >
              <CreditCard className="w-4 h-4" />
              <span>Login with PIV</span>
            </Button>
          </div>
          <div className="text-sm text-gray-600 text-center bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="font-semibold text-blue-900 mb-2">Test Credentials:</p>
            <div className="space-y-1 text-left">
              <p className="font-mono text-xs">
                <span className="font-semibold">Admin:</span> admin@recruit.com / admin123
              </p>
              <p className="font-mono text-xs">
                <span className="font-semibold">Researcher:</span> researcher1@recruit.com / password123
              </p>
              <p className="font-mono text-xs">
                <span className="font-semibold">Viewer:</span> viewer1@recruit.com / password123
              </p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};


