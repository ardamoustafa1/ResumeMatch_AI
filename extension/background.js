chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== 'START_ANALYSIS') return false;

  (async () => {
    try {
      const { apiToken, apiBaseUrl } = await chrome.storage.local.get([
        'apiToken',
        'apiBaseUrl'
      ]);
      if (!apiToken) throw new Error('API token is not configured');
      const baseUrl = (apiBaseUrl || 'http://localhost:8000').replace(/\/$/, '');
      const response = await fetch(`${baseUrl}/api/v1/analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiToken}`
        },
        body: JSON.stringify(message.payload)
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(body.detail?.error || body.detail || 'Analysis could not start');
      }
      sendResponse({ ok: true, data: body });
    } catch (error) {
      sendResponse({ ok: false, error: error.message });
    }
  })();

  return true;
});
