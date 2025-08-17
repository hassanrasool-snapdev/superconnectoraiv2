import { WarmIntroStatus } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function createWarmIntroRequest(
  requesterName: string,
  connectionName: string,
  status: WarmIntroStatus = WarmIntroStatus.pending,
  token: string
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/warm-intro-requests/`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        requester_name: requesterName,
        connection_name: connectionName,
        status: status,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to create warm intro request:", error);
    throw error;
  }
}

export async function updateWarmIntroRequestStatus(
    requestId: string,
    status: WarmIntroStatus,
    token: string,
    connectedDate?: string,
    declinedDate?: string
): Promise<any> {
    try {
        const body: any = { status };
        
        if (connectedDate) {
            body.connected_date = connectedDate;
        }
        
        if (declinedDate) {
            body.declined_date = declinedDate;
        }

        const response = await fetch(`${API_BASE_URL}/warm-intro-requests/${requestId}/status`, {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Failed to update warm intro request status:", error);
        throw error;
    }
}

export async function getWarmIntroRequests(
  token: string,
  page: number = 1,
  limit: number = 10,
  status?: WarmIntroStatus
): Promise<any> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    
    if (status) {
      params.append('status', status);
    }

    const response = await fetch(`${API_BASE_URL}/warm-intro-requests/?${params}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to fetch warm intro requests:", error);
    throw error;
  }
}

export async function getWarmIntroRequestById(
  requestId: string,
  token: string
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/warm-intro-requests/${requestId}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to fetch warm intro request:", error);
    throw error;
  }
}

async function uploadConnectionsCSV(file: File): Promise<any> {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to upload connections CSV:", error);
    throw error;
  }
}

async function deleteConnections(token: string): Promise<any> {
  try {
    const response = await fetch(`/api/delete`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ connectionIds: [] }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to delete connections:", error);
    throw error;
  }
}

async function clearPineconeData(token: string): Promise<any> {
  try {
    const response = await fetch(`/api/clear-pinecone`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to clear Pinecone data:", error);
    throw error;
  }
}

// Real authentication implementations
export async function loginUser(email: string, password: string): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to login:", error);
    throw error;
  }
}

export async function registerUser(
  email: string,
  password: string,
  name: string
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
        name
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to register:", error);
    throw error;
  }
}

export async function getGeneratedEmails(
  token: string,
  page: number = 1,
  limit: number = 10
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    items: [],
    total: 0,
    page,
    limit,
    total_pages: 0
  });
}

export async function getUserProfile(token: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to get user profile:", error);
    throw error;
  }
}

export async function searchConnectionsWithProgress(
  searchRequest: { query: string; filters?: any },
  token: string,
  onProgress?: (progress: number) => void
): Promise<any[]> {
  try {
    if (onProgress) {
      onProgress(10);
    }

    const response = await fetch(`${API_BASE_URL}/search/progress`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(searchRequest),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Handle Server-Sent Events for progress updates
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let results: any[] = [];

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.progress && onProgress) {
                onProgress(data.progress);
              }
              
              if (data.results) {
                results = data.results;
              }
              
              if (data.error) {
                throw new Error(data.error);
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', parseError);
            }
          }
        }
      }
    }

    return results;
  } catch (error) {
    console.error("Failed to search connections:", error);
    throw error;
  }
}

export async function getConnectionsCount(token: string): Promise<{ count: number }> {
  try {
    const response = await fetch(`${API_BASE_URL}/connections/count`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to get connections count:", error);
    throw error;
  }
}

export async function createSavedSearch(
  name: string,
  query: string,
  filters: any,
  token: string
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/saved-searches/`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
        query,
        filters
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to create saved search:", error);
    throw error;
  }
}

export async function addFavoriteConnection(
  connectionId: string,
  token: string
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/favorites/`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        connection_id: connectionId
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to add favorite connection:", error);
    throw error;
  }
}

export async function generateEmail(
  connectionId: string,
  prompt: string,
  token: string
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    subject: "Introduction Request",
    body: "This is a generated email body based on your prompt.",
    generated_at: new Date().toISOString()
  });
}

// Additional missing API functions
export async function getConnections(
  token: string,
  page: number = 1,
  limit: number = 10
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    items: [],
    total: 0,
    page,
    limit,
    total_pages: 0
  });
}

export async function getSavedSearches(
  token: string,
  page: number = 1,
  limit: number = 10
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    items: [],
    total: 0,
    page,
    limit,
    total_pages: 0
  });
}

export async function deleteSavedSearch(
  searchId: string,
  token: string
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({ success: true });
}

export async function getSearchHistory(
  token: string,
  page: number = 1,
  limit: number = 10
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    items: [],
    total: 0,
    page,
    limit,
    total_pages: 0
  });
}

export async function clearSearchHistory(token: string): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({ success: true });
}

export async function deleteSearchHistoryEntry(
  entryId: string,
  token: string
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({ success: true });
}

export async function getFavoriteConnections(
  token: string,
  page: number = 1,
  limit: number = 10
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    items: [],
    total: 0,
    page,
    limit,
    total_pages: 0
  });
}

export async function removeFavoriteConnection(
  connectionId: string,
  token: string
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    id: connectionId,
    favorited: false
  });
}

export async function getTippingHistory(
  token: string,
  page: number = 1,
  limit: number = 10
): Promise<any> {
  // Mock implementation - replace with actual API call when backend is ready
  return Promise.resolve({
    items: [],
    total: 0,
    page,
    limit,
    total_pages: 0
  });
}

export async function exportConnectedRequestsCSV(token: string): Promise<Blob> {
  try {
    const response = await fetch(`${API_BASE_URL}/warm-intro-requests/export/csv`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.blob();
  } catch (error) {
    console.error("Failed to export connected requests CSV:", error);
    throw error;
  }
}

export { uploadConnectionsCSV, deleteConnections, clearPineconeData };