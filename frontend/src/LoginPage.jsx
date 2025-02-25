import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
const path="http://127.0.0.1:8000";


const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('patient');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [metaMaskId, setMetaMaskId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusCode, setStatusCode] = useState(null);
  
  const navigate = useNavigate();

  const connectMetaMask = async () => {
    setError('');
    
    if (typeof window.ethereum === 'undefined') {
      setError('MetaMask is not installed. Please install MetaMask to continue.');
      return;
    }
    
    try {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      setMetaMaskId(accounts[0]);
      return accounts[0];
    } catch (error) {
      setError('Failed to connect to MetaMask. Please try again.');
      console.error(error);
      return null;
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    let endpoint = '';
    let requestBody = {};
    
    switch (activeTab) {
      case 'hospital':
        endpoint = `${path}/hospital-login/`;
        
        // Verify MetaMask for hospital login
        const hospitalMetaMaskAccount = metaMaskId || await connectMetaMask();
        if (!hospitalMetaMaskAccount) {
          setIsLoading(false);
          return;
        }
        
        requestBody = {
          username,
          password,
          metamask_id: hospitalMetaMaskAccount
        };
        break;
        
      case 'doctor':
        endpoint = `${path}/doctor-login/`;
        
        // Verify MetaMask for doctor login
        const doctorMetaMaskAccount = metaMaskId || await connectMetaMask();
        if (!doctorMetaMaskAccount) {
          setIsLoading(false);
          return;
        }
        
        requestBody = {
          username,
          password,
          metamask_id: doctorMetaMaskAccount
        };
        break;
        
      case 'patient':
        endpoint = `${path}/patient-login/`;
        requestBody = {
          username,
          password
        };
        break;
        
      default:
        setError('Invalid login type');
        setIsLoading(false);
        return;
    }
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      setStatusCode(response.status);
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        localStorage.setItem('userType', activeTab);
        
        // Redirect based on user type
        navigate(`/${activeTab}-dashboard`);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      setError('Network error. Please try again later.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center text-blue-600 mb-6">Healthcare Login</h1>
        
        {/* Status Code Display */}
        {statusCode && (
          <div className={`mb-4 text-center p-2 rounded ${
            statusCode >= 200 && statusCode < 300 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            Status Code: {statusCode}
          </div>
        )}
        
        {/* Login Type Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            className={`flex-1 py-2 font-medium ${
              activeTab === 'patient' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-blue-500'
            }`}
            onClick={() => setActiveTab('patient')}
          >
            Patient
          </button>
          <button
            className={`flex-1 py-2 font-medium ${
              activeTab === 'doctor' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-blue-500'
            }`}
            onClick={() => setActiveTab('doctor')}
          >
            Doctor
          </button>
          <button
            className={`flex-1 py-2 font-medium ${
              activeTab === 'hospital' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-blue-500'
            }`}
            onClick={() => setActiveTab('hospital')}
          >
            Hospital
          </button>
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label htmlFor="username" className="block text-gray-700 font-medium mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-700 font-medium mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          {/* MetaMask Integration for Doctor and Hospital */}
          {(activeTab === 'doctor' || activeTab === 'hospital') && (
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <label className="block text-gray-700 font-medium mb-2">
                  MetaMask Verification
                </label>
                <button
                  type="button"
                  onClick={connectMetaMask}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Connect Wallet
                </button>
              </div>
              {metaMaskId ? (
                <div className="p-3 bg-green-100 text-green-700 rounded-md truncate">
                  Connected: {metaMaskId}
                </div>
              ) : (
                <div className="p-3 bg-gray-100 text-gray-700 rounded-md">
                  Please connect your MetaMask wallet
                </div>
              )}
            </div>
          )}
          
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150"
            disabled={isLoading || ((activeTab === 'doctor' || activeTab === 'hospital') && !metaMaskId)}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="mt-4 text-center">
          <a href="#" className="text-sm text-blue-600 hover:text-blue-800">
            Forgot password?
          </a>
        </div>
        
        <div className="mt-6 border-t border-gray-200 pt-4 text-center">
          <p className="text-sm text-gray-600">
            Need an account?{' '}
            <a href="#" className="font-medium text-blue-600 hover:text-blue-800">
              Register here
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
