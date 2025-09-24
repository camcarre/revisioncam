/**
 * Système d'authentification simple pour RevisionCam
 * Vérifie la connexion sur toutes les pages protégées
 */

// Configuration des identifiants
const VALID_CREDENTIALS = {
  username: 'camcam',
  password: '202122'
};

// Durée de session (24 heures)
const SESSION_DURATION = 24 * 60 * 60 * 1000;

/**
 * Vérifie si l'utilisateur est connecté
 */
function isLoggedIn() {
  const loginStatus = localStorage.getItem('isLoggedIn');
  const loginTime = localStorage.getItem('loginTime');
  
  if (!loginStatus || loginStatus !== 'true' || !loginTime) {
    return false;
  }
  
  // Vérifier si la session a expiré
  const now = new Date().getTime();
  const loginTimestamp = new Date(loginTime).getTime();
  
  if (now - loginTimestamp > SESSION_DURATION) {
    // Session expirée
    clearAuth();
    return false;
  }
  
  return true;
}

/**
 * Efface les données d'authentification
 */
function clearAuth() {
  localStorage.removeItem('isLoggedIn');
  localStorage.removeItem('username');
  localStorage.removeItem('loginTime');
}

/**
 * Déconnecte l'utilisateur
 */
function logout() {
  clearAuth();
  redirectToLogin();
}

/**
 * Redirige vers la page de connexion
 */
function redirectToLogin() {
  // Éviter les redirections en boucle
  if (!window.location.pathname.includes('login.html')) {
    window.location.href = '/login.html';
  }
}

/**
 * Initialise la protection d'authentification
 * À appeler sur chaque page protégée
 */
function initAuth() {
  // Vérifier la connexion
  if (!isLoggedIn()) {
    redirectToLogin();
    return false;
  }
  
  // Ajouter un bouton de déconnexion si nécessaire
  addLogoutButton();
  
  return true;
}

/**
 * Ajoute un bouton de déconnexion dans la navbar
 */
function addLogoutButton() {
  // Attendre que le DOM soit chargé
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addLogoutButton);
    return;
  }
  
  const navbar = document.querySelector('.navbar-nav');
  if (!navbar) return;
  
  // Vérifier si le bouton existe déjà
  if (document.getElementById('logoutBtn')) return;
  
  const username = localStorage.getItem('username') || 'Utilisateur';
  
  const logoutLi = document.createElement('li');
  logoutLi.className = 'nav-item';
  logoutLi.innerHTML = `
    <a href="#" class="nav-link" id="logoutBtn" onclick="logout(); return false;">
      <i class="fas fa-sign-out-alt me-2"></i>Déconnexion (${username})
    </a>
  `;
  
  navbar.appendChild(logoutLi);
}

/**
 * Vérifie la connexion et redirige si nécessaire
 * Version simplifiée pour les pages qui n'ont pas de navbar
 */
function checkAuth() {
  if (!isLoggedIn()) {
    redirectToLogin();
    return false;
  }
  return true;
}

/**
 * Extend session - prolonge la session de l'utilisateur
 */
function extendSession() {
  if (isLoggedIn()) {
    localStorage.setItem('loginTime', new Date().toISOString());
  }
}

// Prolonger la session à chaque interaction utilisateur
document.addEventListener('click', extendSession);
document.addEventListener('keypress', extendSession);

// Vérifier la session toutes les 5 minutes
setInterval(() => {
  if (!isLoggedIn()) {
    redirectToLogin();
  }
}, 5 * 60 * 1000);

// Export pour utilisation dans d'autres scripts
window.auth = {
  isLoggedIn,
  logout,
  clearAuth,
  checkAuth,
  extendSession,
  VALID_CREDENTIALS
};
