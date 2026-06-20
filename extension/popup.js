document.addEventListener('DOMContentLoaded', () => {
  const apiTokenInput = document.getElementById('apiToken');
  const apiBaseUrlInput = document.getElementById('apiBaseUrl');
  const cvTextInput = document.getElementById('cvText');
  const saveBtn = document.getElementById('saveBtn');
  const statusDiv = document.getElementById('status');

  chrome.storage.local.get(['apiToken', 'apiBaseUrl', 'cvText'], (result) => {
    if (result.apiToken) apiTokenInput.value = result.apiToken;
    apiBaseUrlInput.value = result.apiBaseUrl || 'http://localhost:8000';
    if (result.cvText) cvTextInput.value = result.cvText;
  });

  saveBtn.addEventListener('click', async () => {
    const apiBaseUrl = apiBaseUrlInput.value.trim().replace(/\/$/, '');
    if (!apiBaseUrl.startsWith('http://localhost:') && !apiBaseUrl.startsWith('https://')) {
      statusDiv.textContent = 'Use HTTPS for remote APIs.';
      return;
    }
    if (apiBaseUrl.startsWith('https://')) {
      const origin = `${new URL(apiBaseUrl).origin}/*`;
      const granted = await chrome.permissions.request({ origins: [origin] });
      if (!granted) {
        statusDiv.textContent = 'API host permission was not granted.';
        return;
      }
    }
    chrome.storage.local.set({
      apiToken: apiTokenInput.value.trim(),
      apiBaseUrl,
      cvText: cvTextInput.value.trim()
    }, () => {
      statusDiv.textContent = 'Saved securely in local storage.';
      setTimeout(() => { statusDiv.textContent = ''; }, 2000);
    });
  });
});
