import { useState, useEffect } from 'react';
import MutualMatches from './components/MutualMatches';
import NewLikes from './components/NewLikes';
import FilterPanel from './components/FilterPanel';
import Dashboard from './components/Dashboard';
import { Heart, Zap, Settings, RefreshCw } from 'lucide-react';
import { apiService, Stats, FilterConfig } from './services/api';
import './App.css';

interface Stats {
  total_profiles: number;
  mutual_matches: number;
  incoming_likes: number;
  outgoing_likes: number;
  by_app: Record<string, number>;
}

type TabType = 'mutual' | 'likes' | 'filters' | 'dashboard';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [initialized, setInitialized] = useState(false);

  // Check backend health and initialize
  useEffect(() => {
    checkHealthAndInit();
  }, []);

  const checkHealthAndInit = async () => {
    try {
      setLoading(true);
      const healthy = await apiService.checkHealth();
      
      if (healthy) {
        // Initialize with default filter config
        const defaultConfig: FilterConfig = {
          min_age: 18,
          max_age: 100,
          max_distance_km: 50,
          must_not_smoke: false,
          must_not_use_drugs: false,
          use_clip: true,
        };
        
        await apiService.initialize(defaultConfig);
        setInitialized(true);
        await getStats();
      }
    } catch (error) {
      console.error('Failed to initialize:', error);
      setInitialized(false);
    } finally {
      setLoading(false);
    }
  };

  const getStats = async () => {
    try {
      const statsData = await apiService.getStats();
      setStats(statsData);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      // Sync from all authenticated platforms
      await apiService.refresh();
      await getStats();
      alert('Sync complete! Check the dashboard for updates.');
    } catch (error) {
      console.error('Sync failed:', error);
      alert('Sync failed: ' + (error as any).message);
    } finally {
      setSyncing(false);
    }
  };

  const handleInit = async (filterConfig: FilterConfig) => {
    try {
      await apiService.initialize(filterConfig);
      setInitialized(true);
      await getStats();
      setActiveTab('dashboard');
    } catch (error) {
      console.error('Initialization failed:', error);
      alert('Initialization failed: ' + (error as any).message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-pink-500 to-purple-600">
        <div className="text-white text-center">
          <div className="animate-spin mb-4">
            <Heart size={48} />
          </div>
          <h1 className="text-3xl font-bold">Loading...</h1>
        </div>
      </div>
    );
  }

  if (!initialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-500 to-purple-600 p-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-8 text-center">
            Dating Apps Orchestrator
          </h1>
          <FilterPanel onInit={handleInit} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <header className="bg-black bg-opacity-50 border-b border-pink-500">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">
              Dating Orchestrator
            </h1>
            <p className="text-gray-400 text-sm">Unify Tinder, Hinge & Match</p>
          </div>
          <button
            onClick={handleSync}
            disabled={syncing}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold transition ${
              syncing
                ? 'bg-gray-600 text-gray-400'
                : 'bg-gradient-to-r from-pink-500 to-purple-500 text-white hover:from-pink-600 hover:to-purple-600'
            }`}
          >
            <Zap size={20} />
            {syncing ? 'Syncing...' : 'Sync Apps'}
          </button>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-gradient-to-r from-pink-900 to-purple-900 border-b border-pink-500">
          <div className="max-w-7xl mx-auto px-4 py-3 grid grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-pink-200 text-sm">Mutual Matches</p>
              <p className="text-white text-2xl font-bold">{stats.mutual_matches}</p>
            </div>
            <div>
              <p className="text-pink-200 text-sm">Incoming Likes</p>
              <p className="text-white text-2xl font-bold">{stats.incoming_likes}</p>
            </div>
            <div>
              <p className="text-pink-200 text-sm">Total Profiles</p>
              <p className="text-white text-2xl font-bold">{stats.total_profiles}</p>
            </div>
            <div>
              <p className="text-pink-200 text-sm">Apps Connected</p>
              <p className="text-white text-2xl font-bold">{Object.keys(stats.by_app).length}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <nav className="border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 flex gap-8">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`py-4 px-2 font-semibold transition border-b-2 ${
              activeTab === 'dashboard'
                ? 'border-pink-500 text-pink-400'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('mutual')}
            className={`py-4 px-2 font-semibold transition border-b-2 flex items-center gap-2 ${
              activeTab === 'mutual'
                ? 'border-pink-500 text-pink-400'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            <Heart size={18} /> Mutual Matches
          </button>
          <button
            onClick={() => setActiveTab('likes')}
            className={`py-4 px-2 font-semibold transition border-b-2 ${
              activeTab === 'likes'
                ? 'border-pink-500 text-pink-400'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            Incoming Likes
          </button>
          <button
            onClick={() => setActiveTab('filters')}
            className={`py-4 px-2 font-semibold transition border-b-2 flex items-center gap-2 ${
              activeTab === 'filters'
                ? 'border-pink-500 text-pink-400'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            <Settings size={18} /> Filters
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'dashboard' && <Dashboard apiBase={API_BASE} />}
        {activeTab === 'mutual' && <MutualMatches apiBase={API_BASE} />}
        {activeTab === 'likes' && <NewLikes apiBase={API_BASE} />}
        {activeTab === 'filters' && <FilterPanel onInit={handleInit} isUpdate={true} />}
      </main>
    </div>
  );
}

export default App;
