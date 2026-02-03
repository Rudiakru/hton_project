import axios from 'axios';

const api = {
  healthCheck: async () => {
    const response = await axios.get('/api/health');
    return response.data;
  },

  // Demo-mode endpoints (frozen demo pack; zero compute)
  demoHealth: async () => {
    const response = await axios.get('/api/demo/health');
    return response.data;
  },

  demoMatches: async () => {
    const response = await axios.get('/api/demo/matches');
    return response.data;
  },

  demoTeams: async () => {
    const response = await axios.get('/api/demo/teams');
    return response.data;
  },

  demoShowMoments: async (matchId) => {
    const response = await axios.get('/api/demo/show-moments', {
      params: { match_id: matchId }
    });
    return response.data;
  },

  demoAnalyzeMoment: async (evidenceId) => {
    const response = await axios.get('/api/demo/analyze-moment', {
      params: { evidence_id: evidenceId }
    });
    return response.data;
  },

  demoScoutTeam: async (teamId) => {
    const response = await axios.get('/api/demo/scout-team', {
      params: { team_id: teamId }
    });
    return response.data;
  },

  demoIntegrity: async () => {
    const response = await axios.get('/api/demo/integrity');
    return response.data;
  },

  demoObservationMasking: async () => {
    const response = await axios.get('/api/demo/observation-masking');
    return response.data;
  },

  demoBenchmarks: async () => {
    const response = await axios.get('/api/demo/benchmarks');
    return response.data;
  },

  demoValidation: async () => {
    const response = await axios.get('/api/demo/validation');
    return response.data;
  },

  parseMatch: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post('/api/parse-match', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  analyzeBatch: async (files) => {
    const maxSize = 20 * 1024 * 1024; // 20MB
    for (let i = 0; i < files.length; i++) {
      if (files[i].size > maxSize) {
        throw new Error(`File ${files[i].name} is too large. Max 20MB.`);
      }
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    
    try {
      const response = await axios.post('/api/analyze-batch', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000 // 60s for batch
      });
      return response.data;
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Analysis timed out. Try fewer files.');
      }
      throw error;
    }
  }
};

export default api;
