const API_URL = "http://127.0.0.1:8001";

export async function apiFetch(
  endpoint,
  options = {}
) {
  const token = localStorage.getItem(
    "forensics_token"
  );

  const headers = {
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,
      headers
    }
  );

  if (response.status === 401) {
    localStorage.removeItem(
      "forensics_token"
    );
    localStorage.removeItem(
      "forensics_user"
    );

    window.location.href = "/login";

    throw new Error(
      "Authentication expired. Please login again."
    );
  }

  return response;
}

export async function apiJson(
  endpoint,
  options = {}
) {
  const response = await apiFetch(
    endpoint,
    options
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Request failed"
    );
  }

  return data;
}

export { API_URL };