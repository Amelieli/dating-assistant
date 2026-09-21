import { useState, useEffect } from 'react';
import axios from 'axios';
import ProfileCard from './ProfileCard';
import { Loader, Star } from 'lucide-react';

interface Props {
  apiBase: string;
}

export default function NewLikes({ apiBase }: Props) {
  const [likes, setLikes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterApp, setFilterApp] = useState<string>('all');

  useEffect(() => {
    loadLikes();
  }, []);

  const loadLikes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${apiBase}/matches/incoming`);
      setLikes(response.data.likes);
    } catch (error) {
      console.error('Failed to load likes:', error);
    } finally {
      setLoading(false);
    }
  };

  const getFilteredLikes = () => {
    if (filterApp === 'all') return likes;
    return likes.filter((like) => like.app_source === filterApp);
  };

  const appCounts = likes.reduce(
    (acc, like) => {
      acc[like.app_source] = (acc[like.app_source] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader className="animate-spin text-pink-400" size={32} />
      </div>
    );
  }

  const filtered = getFilteredLikes();

  return (
    <div>
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Star className="text-yellow-400" /> Incoming Likes ({likes.length})
          </h2>
        </div>

        {/* App Filter */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterApp('all')}
            className={`px-4 py-2 rounded-lg font-semibold transition ${
              filterApp === 'all'
                ? 'bg-pink-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All ({likes.length})
          </button>
          {Object.entries(appCounts).map(([app, count]) => (
            <button
              key={app}
              onClick={() => setFilterApp(app)}
              className={`px-4 py-2 rounded-lg font-semibold transition capitalize ${
                filterApp === app
                  ? 'bg-pink-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {app} ({count})
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No incoming likes. Check back soon!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((profile) => (
            <ProfileCard key={`${profile.app_source}-${profile.app_id}`} profile={profile} isNew />
          ))}
        </div>
      )}
    </div>
  );
}
