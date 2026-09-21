import { useState } from 'react';
import { Settings } from 'lucide-react';

interface Props {
  onInit: (config: any) => void;
  isUpdate?: boolean;
}

export default function FilterPanel({ onInit, isUpdate = false }: Props) {
  const [config, setConfig] = useState({
    min_age: 25,
    max_age: 40,
    max_distance_km: 50,
    must_not_smoke: true,
    must_not_use_drugs: true,
    min_interest_overlap: 1,
    required_interests: '',
    use_clip: true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const finalConfig = {
      ...config,
      required_interests: config.required_interests
        .split(',')
        .map((i) => i.trim())
        .filter((i) => i),
    };
    onInit(finalConfig);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-6"
    >
      <h2 className="text-2xl font-bold text-white flex items-center gap-2">
        <Settings /> Filter Preferences
      </h2>

      {/* Age Range */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-gray-300 font-semibold mb-2">Minimum Age</label>
          <input
            type="number"
            value={config.min_age}
            onChange={(e) => setConfig({ ...config, min_age: parseInt(e.target.value) })}
            className="w-full bg-gray-700 border border-gray-600 text-white rounded px-3 py-2"
            min="18"
            max="100"
          />
        </div>
        <div>
          <label className="block text-gray-300 font-semibold mb-2">Maximum Age</label>
          <input
            type="number"
            value={config.max_age}
            onChange={(e) => setConfig({ ...config, max_age: parseInt(e.target.value) })}
            className="w-full bg-gray-700 border border-gray-600 text-white rounded px-3 py-2"
            min="18"
            max="100"
          />
        </div>
      </div>

      {/* Distance */}
      <div>
        <label className="block text-gray-300 font-semibold mb-2">
          Maximum Distance (km): {config.max_distance_km}
        </label>
        <input
          type="range"
          min="5"
          max="200"
          value={config.max_distance_km}
          onChange={(e) =>
            setConfig({ ...config, max_distance_km: parseInt(e.target.value) })
          }
          className="w-full"
        />
      </div>

      {/* Lifestyle Filters */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-white">Lifestyle</h3>
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={config.must_not_smoke}
            onChange={(e) =>
              setConfig({ ...config, must_not_smoke: e.target.checked })
            }
            className="w-4 h-4 rounded"
          />
          <span className="text-gray-300">No Smoking</span>
        </label>
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={config.must_not_use_drugs}
            onChange={(e) =>
              setConfig({ ...config, must_not_use_drugs: e.target.checked })
            }
            className="w-4 h-4 rounded"
          />
          <span className="text-gray-300">No Drug Use</span>
        </label>
      </div>

      {/* Interests */}
      <div>
        <label className="block text-gray-300 font-semibold mb-2">
          Required Interests (comma-separated)
        </label>
        <textarea
          value={config.required_interests}
          onChange={(e) =>
            setConfig({ ...config, required_interests: e.target.value })
          }
          placeholder="hiking, travel, photography"
          className="w-full bg-gray-700 border border-gray-600 text-white rounded px-3 py-2 h-20 resize-none"
        />
      </div>

      {/* CLIP Matching */}
      <label className="flex items-center gap-3 cursor-pointer">
        <input
          type="checkbox"
          checked={config.use_clip}
          onChange={(e) => setConfig({ ...config, use_clip: e.target.checked })}
          className="w-4 h-4 rounded"
        />
        <span className="text-gray-300">
          Use AI Photo Matching (CLIP)
          <p className="text-xs text-gray-400">Slower but finds visually similar profiles</p>
        </span>
      </label>

      {/* Submit */}
      <button
        type="submit"
        className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-bold py-3 rounded-lg transition"
      >
        {isUpdate ? 'Update Filters' : 'Initialize Orchestrator'}
      </button>
    </form>
  );
}
