/**
 * API Service for Dating Agent
 * Handles all communication with the Flask backend
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

export interface Profile {
  id: string;
  app: string;
  name: string;
  age: number;
  bio: string;
  photos: string[];
  interests: string[];
  location: string;
  distance_km?: number;
  match_status: string;
}

export interface Stats {
  total_profiles: number;
  mutual_matches: number;
  incoming_likes: number;
  outgoing_likes: number;
  by_app: Record<string, number>;
}

export interface FilterConfig {
  min_age?: number;
  max_age?: number;
  max_distance_km?: number;
  must_not_smoke?: boolean;
  must_not_use_drugs?: boolean;
  required_interests?: string[];
  use_clip?: boolean;
}

export interface SyncRequest {
  hinge_user_id?: string;
  tinder_user_id?: string;
  limit?: number;
  find_duplicates?: boolean;
}

export interface SyncResponse {
  status: string;
  platforms: Record<string, any>;
  duration_seconds: number;
}

class APIService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }

  // Initialize orchestrator with filter config
  async initialize(config: FilterConfig): Promise<any> {
    const response = await this.api.post('/init', config);
    return response.data;
  }

  // Authenticate with dating apps
  async authenticate(credentials: Record<string, any>): Promise<any> {
    const response = await this.api.post('/authenticate', credentials);
    return response.data;
  }

  // Sync profiles from dating apps
  async sync(request: SyncRequest): Promise<SyncResponse> {
    const response = await this.api.post('/sync', request);
    return response.data;
  }

  // Get statistics
  async getStats(): Promise<Stats> {
    const response = await this.api.get('/stats');
    return response.data;
  }

  // Get mutual matches
  async getMutualMatches(): Promise<Profile[]> {
    const response = await this.api.get('/matches/mutual');
    return response.data.profiles || [];
  }

  // Get incoming likes
  async getIncomingLikes(): Promise<Profile[]> {
    const response = await this.api.get('/matches/incoming');
    return response.data.profiles || [];
  }

  // Filter and rank profiles
  async filterAndRank(filters: FilterConfig, searchQuery?: string): Promise<Profile[]> {
    const response = await this.api.post('/filter-and-rank', {
      ...filters,
      search_query: searchQuery,
    });
    return response.data.profiles || [];
  }

  // Search by description
  async searchByDescription(query: string): Promise<Profile[]> {
    const response = await this.api.post('/search/by-description', {
      query,
    });
    return response.data.profiles || [];
  }

  // Get profile details
  async getProfile(app: string, profileId: string): Promise<Profile> {
    const response = await this.api.get(`/profile/${app}/${profileId}`);
    return response.data.profile;
  }

  // Export mutual matches
  async exportMutualMatches(): Promise<Blob> {
    const response = await this.api.get('/export/mutual-matches', {
      responseType: 'blob',
    });
    return response.data;
  }

  // Refresh data
  async refresh(): Promise<any> {
    const response = await this.api.post('/refresh');
    return response.data;
  }
}

export const apiService = new APIService();
export default apiService;
