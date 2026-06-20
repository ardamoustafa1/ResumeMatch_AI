const buttonHtml = `
  <button id="resumematch-btn" class="resumematch-btn">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
    Match with AI
  </button>
`;

function findTargetContainer() {
  const selectors = [
    '.job-details-jobs-unified-top-card__container--two-pane',
    '.jobs-unified-top-card__content--two-pane',
    '.job-view-layout-jobs-details',
    '.jobs-details-top-card__actions'
  ];
  for (const s of selectors) {
    const el = document.querySelector(s);
    if (el) return el;
  }
  // Ultimate fallback: Try to attach near the job title
  const title = document.querySelector('h1.t-24');
  if (title) return title.parentElement;
  return null;
}

function injectButton() {
  if (document.getElementById('resumematch-btn')) return;
  const targetContainer = findTargetContainer();
  if (targetContainer) {
    targetContainer.insertAdjacentHTML('beforeend', buttonHtml);
    document.getElementById('resumematch-btn').addEventListener('click', handleMatchClick);
  }
}

async function handleMatchClick() {
  const btn = document.getElementById('resumematch-btn');
  btn.innerText = 'Analyzing...';
  btn.disabled = true;

  try {
    let jdText = '';
    const jdSelectors = [
      '.job-details-jobs-unified-top-card__job-insight', // add more robust ones
      '.jobs-description__container',
      '.jobs-box__html-content',
      'article.jobs-description__container',
      '#job-details'
    ];
    for (const s of jdSelectors) {
      const el = document.querySelector(s);
      if (el && el.innerText.trim()) {
        jdText = el.innerText.trim();
        break;
      }
    }
    
    if (!jdText) {
      // Fallback
      const fallbackEl = document.querySelector('.job-view-layout-jobs-details');
      if (fallbackEl) jdText = fallbackEl.innerText.trim();
    }
    
    if (!jdText) {
      console.warn('Telemetry: Job description DOM selector failed. LinkedIn layout changed.');
      throw new Error('Job description not found. LinkedIn layout might have changed.');
    }

    const { apiToken, cvText } = await chrome.storage.local.get([
      'apiToken',
      'cvText'
    ]);
    if (!apiToken || !cvText) {
      alert('Please configure API Token and CV Text in the ResumeMatch extension popup.');
      return;
    }

    const response = await chrome.runtime.sendMessage({
      type: 'START_ANALYSIS',
      payload: {
        cv_text: cvText,
        jd_text: jdText,
        company: 'LinkedIn Job'
      }
    });
    if (!response?.ok) throw new Error(response?.error || 'Failed to start analysis');
    btn.innerText = 'Analysis Started!';
    btn.style.backgroundColor = '#16a34a'; // green
  } catch (err) {
    console.error(err);
    alert('Error: ' + err.message);
    btn.innerText = 'Failed';
    btn.style.backgroundColor = '#dc2626'; // red
  } finally {
    setTimeout(() => {
      btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> Match with AI`;
      btn.disabled = false;
      btn.style.backgroundColor = '#2563eb';
    }, 3000);
  }
}

// Observe DOM mutations to inject button when navigating LinkedIn SPA
const observer = new MutationObserver(() => injectButton());
observer.observe(document.body, { childList: true, subtree: true });
injectButton();
