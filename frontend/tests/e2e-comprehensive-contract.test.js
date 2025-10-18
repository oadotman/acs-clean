const axios = require('axios');

async function run() {
  const baseURL = process.env.API_BASE_URL || 'http://localhost:8000/api';
  const client = axios.create({ baseURL, timeout: 120000, headers: { 'Content-Type': 'application/json' } });

  const ad_copy = 'Boost your sales with our AI-powered ad optimizer. Learn More';
  const platform = 'facebook';

  const res = await client.post('/ads/comprehensive-analyze', { ad_copy, platform, user_id: 'e2e-test' });
  const data = res.data || res;

  const abTests = data.abTests;
  if (!abTests || !Array.isArray(abTests.abc_variants)) {
    throw new Error('abTests.abc_variants missing');
  }
  if (abTests.abc_variants.length !== 3) {
    throw new Error(`Expected 3 abc_variants, got ${abTests.abc_variants.length}`);
  }
  const ids = abTests.abc_variants.map(v => v.id);
  const expected = ['variant_a', 'variant_b', 'variant_c'];
  expected.forEach(id => {
    if (!ids.includes(id)) throw new Error(`Missing id ${id}`);
  });

  console.log('OK: contract valid. IDs:', ids.join(', '));
}

run().catch((e) => {
  console.error('E2E FAILED:', e.message);
  process.exit(1);
});


