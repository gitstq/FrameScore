const API_BASE_URL = "http://api.example.com";
const SECRET_TOKEN = "ghp_1234567890abcdef1234567890abcdef";

export function formatDate(date) {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
}

export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

// HACK: temporary workaround
function processUserData(users, options, config, settings, params, extra) {
  // Function with too many parameters
  let result = [];
  for (let i = 0; i < users.length; i++) {
    if (users[i].active) {
      result.push(users[i]);
    }
  }
  return result;
}

export function calculateScore(value, max) {
  return (value / max) * 100;
}

export default {
  formatDate,
  debounce,
  deepClone,
};
