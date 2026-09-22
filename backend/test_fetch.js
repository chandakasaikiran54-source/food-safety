const fs = require('fs');
const path = require('path');

async function test() {
  try {
    const loginRes = await fetch('http://localhost:5000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'test@example.com', password: 'password123' })
    });
    let token;
    const loginData = await loginRes.json();
    if (!loginRes.ok) {
       const regRes = await fetch('http://localhost:5000/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: 'Test', email: 'test@example.com', password: 'password123' })
        });
        const regData = await regRes.json();
        token = regData.data.token;
    } else {
        token = loginData.data.token;
    }

    const formData = new FormData();
    const blob = new Blob([fs.readFileSync('../ai-service/test_food.jpg')], { type: 'image/jpeg' });
    formData.append('image', blob, 'test.jpg');

    const uploadRes = await fetch('http://localhost:5000/api/scans/analyze', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const text = await uploadRes.text();
    console.log('Status:', uploadRes.status);
    console.log('Response:', text);
  } catch(e) {
    console.error(e);
  }
}
test();
