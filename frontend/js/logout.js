// Shared frontend utilities
(function(){
  // Prefer page-defined API if available; fallback to default
  const API_BASE = (typeof window !== 'undefined' && window.API) ? window.API : 'http://localhost:5001';

  async function logout() {
    try {
      await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' });
    } catch (e) {
      // swallow network errors; proceed to clear session
    } finally {
      try { sessionStorage.clear(); } catch (_) {}
      location.href = 'login.html';
    }
  }

  // Expose globally
  window.logout = logout;
})();


