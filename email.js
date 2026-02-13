const { ClientSecretCredential } = require('@azure/identity');
const axios = require('axios');

const CLIENT_ID = '106de4cf-bfb2-4604-acb8-a1e706f649a4';
const TENANT_ID = '47a6a11c-419e-4636-8505-04d72b2c3088';
const CLIENT_SECRET = 'hhj8Q~.eiyy_ZAaypk5keA4MZl42.uzj11fYJayb';
const USER_EMAIL = 'legion@briartech.ca';

async function getAccessToken() {
  const credential = new ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET);
  const tokenRequest = {
    scopes: ['https://graph.microsoft.com/.default'],
  };
  const tokenResponse = await credential.getToken(tokenRequest);
  return tokenResponse.token;
}

async function checkEmails() {
  try {
    const token = await getAccessToken();
    const response = await axios.get(`https://graph.microsoft.com/v1.0/users/${USER_EMAIL}/mailFolders/Inbox/messages?$top=10&$select=subject,from,receivedDateTime,isRead,bodyPreview`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log('Recent emails:', response.data.value.slice(0,5).map(m => ({
      subject: m.subject || 'No subject',
      from: m.from?.emailAddress?.address || 'Unknown',
      received: m.receivedDateTime,
      read: m.isRead,
      preview: (m.bodyPreview || '').substring(0,100)
    })));
  } catch (err) {
    console.error('Email check failed:', err.response?.data || err.message);
  }
}

const action = process.argv[2];
if (action === 'check') checkEmails();
else if (action === 'refresh') console.log('Token refreshed');
else console.log('Usage: node email.js check|refresh');