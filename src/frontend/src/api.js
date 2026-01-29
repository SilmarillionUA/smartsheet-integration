const API_BASE = "/api";

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }

  getMessages() {
    if (!this.data) return this.message;
    if (typeof this.data === "string") return this.data;
    if (this.data.detail) return this.data.detail;
    if (this.data.error) return this.data.error;
    // DRF validation errors: {field: [errors]}
    return Object.entries(this.data)
      .map(([field, errors]) => `${field}: ${[].concat(errors).join(", ")}`)
      .join("; ");
  }

  getUserFriendlyMessage() {
    switch (this.status) {
      case 429:
        return "Rate limit exceeded. Please wait a moment and try again.";
      case 503:
        return "Smartsheet is under maintenance. Try again later.";
      case 504:
        return "Request timed out. Please try again.";
      case 502:
        return this.getMessages();
      default:
        return this.getMessages();
    }
  }

  isRetryable() {
    return [429, 503, 504].includes(this.status);
  }
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && endpoint !== "/token/") {
    const refreshed = await refreshToken();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${localStorage.getItem(
        "access_token",
      )}`;
      const retryResponse = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });
      if (!retryResponse.ok) {
        const data = await retryResponse.json().catch(() => ({}));
        throw new ApiError("Request failed", retryResponse.status, data);
      }
      return retryResponse.status === 204 ? null : retryResponse.json();
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login/";
    return;
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError("Request failed", response.status, data);
  }

  return response.status === 204 ? null : response.json();
}

async function refreshToken() {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) return false;

  try {
    const response = await fetch(`${API_BASE}/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem("access_token", data.access);
      return true;
    }
  } catch (e) {
    console.error("Token refresh failed", e);
  }
  return false;
}

export const api = {
  register: (data) =>
    request("/register/", { method: "POST", body: JSON.stringify(data) }),
  login: (data) =>
    request("/token/", { method: "POST", body: JSON.stringify(data) }),
  logout: () =>
    request("/logout/", {
      method: "POST",
      body: JSON.stringify({ refresh: localStorage.getItem("refresh_token") }),
    }),
  getProfile: () => request("/profile/"),

  getSheets: () => request("/sheets/"),
  createSheet: (data) =>
    request("/sheets/", { method: "POST", body: JSON.stringify(data) }),
  deleteSheet: (sheetId) =>
    request(`/sheets/${sheetId}/`, { method: "DELETE" }),

  getItems: (sheetId) => request(`/sheets/${sheetId}/items/`),
  createItem: (sheetId, data) =>
    request(`/sheets/${sheetId}/items/create/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateItem: (sheetId, rowId, data) =>
    request(`/sheets/${sheetId}/items/${rowId}/`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteItem: (sheetId, rowId) =>
    request(`/sheets/${sheetId}/items/${rowId}/`, { method: "DELETE" }),
  indentItem: (sheetId, rowId) =>
    request(`/sheets/${sheetId}/items/${rowId}/indent/`, { method: "POST" }),
  outdentItem: (sheetId, rowId) =>
    request(`/sheets/${sheetId}/items/${rowId}/outdent/`, { method: "POST" }),
  moveItemUp: (sheetId, rowId) =>
    request(`/sheets/${sheetId}/items/${rowId}/move-up/`, { method: "POST" }),
  moveItemDown: (sheetId, rowId) =>
    request(`/sheets/${sheetId}/items/${rowId}/move-down/`, { method: "POST" }),
};
