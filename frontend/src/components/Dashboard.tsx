import { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, Users, Search } from 'lucide-react';

interface Props {
  apiBase: string;
}

export default function Dashboard({ apiBase }: Props) {
  const [stats, setStats] = useState<any>(null);
  const [filterApplied, setFilterApplied] = useState(false);
  const [yourInterests, setYourInterests] = useState('');
  const [clipSearchText, setClipSearchText] = useState('');
  const [clipResults, setClipResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${apiBase}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleFilterAndRank = async () => {
    if (!yourInterests.trim()) {
      alert('Please enter your interests');
      return;
    }

    setLoading(true);
    try {
      const interests = yourInterests
        .split(',')
        .map((i) => i.trim())
        .filter((i) => i);

      await axios.post(`${apiBase}/filter-and-rank`, {
        your_interests: interests,
        embed_photos: false,
      });

      setFilterApplied(true);
      await loadStats();
      alert('Filters applied! Check the tabs for results.');
    } catch (error) {
      alert('Failed to apply filters: ' + (error as any).message);
    } finally {
      setLoading(false);
    }
  };

  const handleCLIPSearch = async () => {
    if (!clipSearchText.trim()) {
      alert('Please describe what youre looking for');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${apiBase}/search/by-description`, {
        description: clipSearchText,
        top_k: 10,
      });
      setClipResults(response.data.matches || []);
    } catch (error) {
      alert('CLIP search failed: ' + (error as any).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Quick Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-pink-900 to-pink-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-pink-200 text-sm font-semibold">Mutual Matches</p>
                <p className="text-4xl font-bold text-white mt-2">{stats.mutual_matches}</p>
              </div>
              <TrendingUp className="text-pink-300" size={32} />
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-900 to-purple-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-200 text-sm font-semibold">Incoming Likes</p>
                <p className="text-4xl font-bold text-white mt-2">{stats.incoming_likes}</p>
              </div>
              <Users className="text-purple-300" size={32} />
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-900 to-blue-800 rounded-lg p-6">
            <div>
              <p className="text-blue-200 text-sm font-semibold">Total Profiles</p>
              <p className="text-4xl font-bold text-white mt-2">{stats.total_profiles}</p>
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-900 to-indigo-800 rounded-lg p-6">
            <div>
              <p className="text-indigo-200 text-sm font-semibold">Apps Synced</p>
              <p className="text-4xl font-bold text-white mt-2">
                {Object.keys(stats.by_app).length}
              </p>
              <p className="text-indigo-300 text-xs mt-2">
                {Object.entries(stats.by_app)
                  .map(([app, count]) => `${app}: ${count}`)
                  .join(', ')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filter & Rank Section */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4">Apply Smart Filters</h3>
        <p className="text-gray-400 mb-4">
          Define your interests and well rank all profiles for compatibility
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-gray-300 font-semibold mb-2">
              Your Interests (comma-separated)
            </label>
            <textarea
              value={yourInterests}
              onChange={(e) => setYourInterests(e.target.value)}
              placeholder="hiking, travel, photography, cooking"
              className="w-full bg-gray-700 border border-gray-600 text-white rounded px-3 py-2 h-20 resize-none"
            />
          </div>
          <button
            onClick={handleFilterAndRank}
            disabled={loading}
            className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 disabled:opacity-50 text-white font-bold py-3 rounded-lg transition"
          >
            {loading ? 'Processing...' : 'Filter & Rank Profiles'}
          </button>
          {filterApplied && (
            <p className="text-green-400 text-sm">
              Filters applied! Check the Mutual Matches and Incoming Likes tabs.
            </p>
          )}
        </div>
      </div>

      {/* CLIP Image Search */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Search size={24} /> AI Photo Search (CLIP)
        </h3>
        <p className="text-gray-400 mb-4">
          Describe your ideal match and find visually similar profiles
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-gray-300 font-semibold mb-2">
              Describe What Youre Looking For
            </label>
            <textarea
              value={clipSearchText}
              onChange={(e) => setClipSearchText(e.target.value)}
              placeholder="e.g. athletic blonde woman with outdoorsy vibe"
              className="w-full bg-gray-700 border border-gray-600 text-white rounded px-3 py-2 h-20 resize-none"
            />
          </div>
          <button
            onClick={handleCLIPSearch}
            disabled={loading}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 disabled:opacity-50 text-white font-bold py-3 rounded-lg transition"
          >
            {loading ? 'Searching...' : 'Search with AI'}
          </button>

          {clipResults.length > 0 && (
            <div className="mt-6 space-y-4">
              <h4 className="text-white font-semibold">Top Matches:</h4>
              {clipResults.map((result, idx) => (
                <div key={idx} className="bg-gray-700 rounded p-4 flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-semibold text-white">
                      {result.profile.name}, {result.profile.age}
                    </p>
                    <p className="text-gray-400 text-sm">{result.profile.location}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-cyan-400 font-bold">
                      {(result.similarity_score * 100).toFixed(0)}% Similar
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4">How It Works</h3>
        <div className="space-y-3 text-gray-300">
          <p>1. Configure your filters and authenticate with your dating apps</p>
          <p>2. Sync data to fetch all your likes and matches</p>
          <p>3. Apply smart filters to find compatible matches</p>
          <p>4. Use CLIP to find profiles similar to your description</p>
          <p>5. View all results unified in one dashboard</p>
        </div>
      </div>
    </div>
  );
}
