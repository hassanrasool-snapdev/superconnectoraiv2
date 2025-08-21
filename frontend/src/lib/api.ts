import {
  WarmIntroStatus,
  WarmIntroRequest,
  PaginatedWarmIntroRequests,
  GeneratedEmail,
  SearchResult,
  SavedSearch,
  FavoriteConnection,
  Connection,
  SearchHistory
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function createWarmIntroRequest(
  requesterName: string,
  connectionName: string,
  status: WarmIntroStatus = WarmIntroStatus.pending,
  token: string
): Promise<WarmIntroRequest> {
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
): Promise<WarmIntroRequest> {
    try {
        const body: { status: WarmIntroStatus; connected_date?: string; declined_date?: string } = { status };
        
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
): Promise<PaginatedWarmIntroRequests> {
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
): Promise<WarmIntroRequest> {
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

async function uploadConnectionsCSV(file: File): Promise<{ message: string; uploaded_count: number }> {
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

async function deleteConnections(token: string): Promise<{ message: string; deleted_count: number }> {
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

async function clearPineconeData(token: string): Promise<{ message: string }> {
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
export async function loginUser(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
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
): Promise<{ id: string; email: string; name: string; created_at: string }> {
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
  token: string
): Promise<GeneratedEmail[]> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(token); // Prevent unused parameter error
  return Promise.resolve([]);
}

export async function getUserProfile(token: string): Promise<{ id: string; email: string; name: string; created_at: string }> {
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
  searchRequest: { query: string; filters?: Record<string, unknown> },
  token: string,
  onProgress?: (progress: number) => void
): Promise<SearchResult[]> {
  try {
    if (onProgress) {
      onProgress(10);
    }

    // Production fallback: Try regular search endpoint if SSE fails
    const useSSE = true;
    let response: Response;

    if (useSSE) {
      response = await fetch(`${API_BASE_URL}/search/progress`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
          "Accept": "text/event-stream",
          "Cache-Control": "no-cache",
        },
        body: JSON.stringify(searchRequest),
      });
    } else {
      response = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(searchRequest),
      });
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // For non-SSE response, parse JSON directly
    if (!useSSE || !response.headers.get('content-type')?.includes('text/event-stream')) {
      const results = await response.json();
      if (onProgress) onProgress(100);
      return results;
    }

    // Handle Server-Sent Events for progress updates
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let results: SearchResult[] = [];
    let buffer = '';

    // Set a timeout for SSE response
    const SSE_TIMEOUT = 600000; // 10 minutes (600 seconds) to accommodate long AI processing
    let timeoutId: NodeJS.Timeout | null = null;
    const timeoutPromise = new Promise<never>((_, reject) => {
      timeoutId = setTimeout(() => {
        reject(new Error('SSE stream timeout'));
      }, SSE_TIMEOUT);
    });

    try {
      if (reader) {
        await Promise.race([
          (async () => {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              buffer += decoder.decode(value, { stream: true });
              
              // Process complete lines
              let newlineIndex;
              while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
                const line = buffer.slice(0, newlineIndex).trim();
                buffer = buffer.slice(newlineIndex + 1);

                if (line.startsWith('data: ')) {
                  try {
                    const jsonData = line.slice(6).trim();
                    
                    if (jsonData && jsonData !== '') {
                      const data = JSON.parse(jsonData) as {
                        progress?: number;
                        results?: SearchResult[];
                        error?: string;
                        message?: string;
                      };
                      
                      if (typeof data.progress === 'number' && onProgress) {
                        onProgress(Math.min(data.progress, 100));
                      }
                      
                      if (data.results && Array.isArray(data.results) && data.results.length > 0) {
                        results = data.results;
                        // If we have results and progress is 100, we're done
                        if (data.progress === 100) {
                          if (timeoutId) clearTimeout(timeoutId);
                          return;
                        }
                      }
                      
                      if (data.error) {
                        throw new Error(data.error);
                      }
                    }
                  } catch (parseError) {
                    console.warn('Failed to parse SSE data:', parseError, 'Line:', line);
                    // Continue processing other lines instead of breaking
                  }
                }
              }
            }
          })(),
          timeoutPromise
        ]);
      }
    } catch (error) {
      if (timeoutId) clearTimeout(timeoutId);
      if (error instanceof Error && error.message === 'SSE stream timeout') {
        console.warn('SSE timeout, falling back to regular search');
        // Fallback to regular search endpoint
        try {
          const fallbackResponse = await fetch(`${API_BASE_URL}/search`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify(searchRequest),
          });
          
          if (fallbackResponse.ok) {
            const fallbackResults = await fallbackResponse.json();
            if (onProgress) onProgress(100);
            return fallbackResults;
          }
        } catch (fallbackError) {
          console.error('Fallback search also failed:', fallbackError);
        }
      }
      throw error;
    }

    if (timeoutId) clearTimeout(timeoutId);
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
  filters: Record<string, unknown> | undefined,
  token: string
): Promise<SavedSearch> {
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
): Promise<FavoriteConnection> {
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
): Promise<{ subject: string; body: string; generated_at: string }> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(connectionId, prompt, token); // Prevent unused parameter errors
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
): Promise<{ items: Connection[]; total: number; page: number; limit: number; total_pages: number }> {
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
  token: string
): Promise<SavedSearch[]> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(token); // Prevent unused parameter error
  return Promise.resolve([]);
}

export async function deleteSavedSearch(
  searchId: string,
  token: string
): Promise<{ success: boolean }> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(searchId, token); // Prevent unused parameter errors
  return Promise.resolve({ success: true });
}

export async function getSearchHistory(
  token: string
): Promise<SearchHistory[]> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(token); // Prevent unused parameter error
  return Promise.resolve([]);
}

export async function clearSearchHistory(token: string): Promise<{ success: boolean }> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(token); // Prevent unused parameter error
  return Promise.resolve({ success: true });
}

export async function deleteSearchHistoryEntry(
  entryId: string,
  token: string
): Promise<{ success: boolean }> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(entryId, token); // Prevent unused parameter errors
  return Promise.resolve({ success: true });
}

export async function getFavoriteConnections(
  token: string
): Promise<FavoriteConnection[]> {
  // Mock implementation - replace with actual API call when backend is ready
  console.log(token); // Prevent unused parameter error
  return Promise.resolve([]);
}

export async function removeFavoriteConnection(
  connectionId: string,
): Promise<{ id: string; favorited: boolean }> {
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
): Promise<{ items: unknown[]; total: number; page: number; limit: number; total_pages: number }> {
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