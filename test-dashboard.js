const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  const consoleMessages = [];
  const errors = [];
  
  page.on('console', msg => {
    consoleMessages.push({ type: msg.type(), text: msg.text() });
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  page.on('pageerror', error => {
    errors.push(error.message);
  });

  try {
    await page.goto('http://localhost:8080', { waitUntil: 'networkidle', timeout: 10000 });
    
    // Wait a bit for any async errors
    await page.waitForTimeout(2000);
    
    // Check page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check if root element has content
    const rootContent = await page.$eval('#root', el => el.innerHTML.length);
    console.log('Root content length:', rootContent);
    
    // Check for any visible error elements
    const errorElements = await page.$$('.error, [class*="error"]');
    console.log('Error elements found:', errorElements.length);
    
    // Print all console errors
    console.log('\n=== Console Errors ===');
    errors.forEach(e => console.log('ERROR:', e));
    
    // Print network failures
    console.log('\n=== Network Info ===');
    console.log('Final URL:', page.url());
    
  } catch (e) {
    console.log('Page load error:', e.message);
  }
  
  await browser.close();
})();
