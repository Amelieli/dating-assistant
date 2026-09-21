import { useState, useEffect } from 'react';
import axios from 'axios';
import ProfileCard from './ProfileCard';
import { Loader } from 'lucide-react';

interface Props {
  apiBase: string;
}

export default function MutualMatches({ apiBase }: Props) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'score' | 'recent' | 'distance'>('score');

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${apiBase}/matches/mutual`);
      setMatches(response.data.matches);
    } catch (error) {
      console.error('Failed to load matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSortedMatches = () => {
    const sorted = [...matches];
    switch (sortBy) {
      case 'score':
        return sorted.sort((a, b) => (b.match_percentage || 0) - (a.match_percentage || 0));
      case 'distance':
        return sorted.sort((a, b) => (a.distance_km || 999) - (b.distance_km || 999));
      case 'recent':
      default:
        return sorted.sort((a, b) => new Date(b.last_seen).getTime() - new Date(a.last_seen).getTime());
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader className="animate-spin text-pink-400" size={32} />
      </div>
    );
  }

  const sorted = getSortedMatches();

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">
          Mutual Matches ({matches.length})
        </h2>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600"
        >
          <option value="score">Best Match</option>
          <option value="distance">Closest</option>
          <option value="recent">Most Recent</option>
        </select>
      </div>

      {sorted.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No mutual matches yet. Keep swiping!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sorted.map((profile) => (
            <ProfileCard key={`${profile.app_source}-${profile.app_id}`} profile={profile} />
          ))}
        </div>
      )}
    </div>
  );
}
