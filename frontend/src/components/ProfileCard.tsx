import { MapPin, Briefcase, Heart } from 'lucide-react';

interface Profile {
  app_id: string;
  app_source: string;
  name: string;
  age: number;
  location: string;
  distance_km?: number;
  bio: string;
  interests: string[];
  occupation: string;
  match_percentage?: number;
  photo_urls: string[];
  verified: boolean;
}

interface Props {
  profile: Profile;
  isNew?: boolean;
}

export default function ProfileCard({ profile, isNew }: Props) {
  const mainPhoto = profile.photo_urls[0];

  return (
    <div className="relative bg-gray-800 rounded-lg overflow-hidden hover:shadow-xl transition border border-gray-700 hover:border-pink-500">
      {/* Photo */}
      <div className="relative h-48 bg-gray-700 overflow-hidden">
        {mainPhoto ? (
          <img
            src={mainPhoto}
            alt={profile.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as any).src = 'https://via.placeholder.com/300x200?text=No+Image';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-500">
            No photos
          </div>
        )}

        {/* New Badge */}
        {isNew && (
          <div className="absolute top-2 right-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white px-3 py-1 rounded-full text-xs font-bold">
            NEW
          </div>
        )}

        {/* Verified Badge */}
        {profile.verified && (
          <div className="absolute top-2 left-2 bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
            <span></span> Verified
          </div>
        )}

        {/* Match Score */}
        {profile.match_percentage !== undefined && (
          <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-pink-400 px-3 py-1 rounded-full text-sm font-bold">
            {Math.round(profile.match_percentage)}% Match
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Name & Age */}
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-bold text-white">
            {profile.name}, {profile.age}
          </h3>
          <span className="text-xs font-semibold text-pink-400 uppercase">
            {profile.app_source}
          </span>
        </div>

        {/* Location */}
        <div className="flex items-center gap-1 text-gray-400 text-sm mb-3">
          <MapPin size={14} />
          {profile.location}
          {profile.distance_km !== undefined && <span> • {profile.distance_km}km away</span>}
        </div>

        {/* Occupation */}
        {profile.occupation && (
          <div className="flex items-center gap-1 text-gray-400 text-sm mb-3">
            <Briefcase size={14} />
            {profile.occupation}
          </div>
        )}

        {/* Bio */}
        {profile.bio && (
          <p className="text-gray-300 text-sm mb-3 line-clamp-2">
            {profile.bio}
          </p>
        )}

        {/* Interests */}
        {profile.interests && profile.interests.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-2">
              {profile.interests.slice(0, 4).map((interest, idx) => (
                <span
                  key={idx}
                  className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded-full"
                >
                  {interest}
                </span>
              ))}
              {profile.interests.length > 4 && (
                <span className="text-xs bg-gray-700 text-gray-400 px-2 py-1 rounded-full">
                  +{profile.interests.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* CTA */}
        <button className="w-full mt-4 bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-semibold py-2 rounded-lg transition flex items-center justify-center gap-2">
          <Heart size={16} />
          View Profile
        </button>
      </div>
    </div>
  );
}
