// /**
//  * LANCAM Frontend - Main Entry Point
//  */

// import { LancamApp } from './js/app.js';

// // declare the global route .
// // const route={
// //     "/":"home",
// //     "/home":"home",
// //     "/scan":"scan",
// //     "/result":"./components/result.html",
// //     "/compare":"compare",
// //     "/certificates":"certificates",
// //     "/history":"history",
// //     "/settings":"settings"
// // }

// // //  based on the route it will navigate the functionality

// // async function navigateToPage(route) {
// //     const mainContent = document.querySelector('.sidebar').parentElement;

// //     // Hide all core sections initially
// //     const sections = ['.sidebar', '.camera-area', '.controls-panel', '.wake-area'];
// //     sections.forEach(sel => {
// //         const el = document.querySelector(sel);
// //         if (el) el.style.display = 'none';
// //     });

// //     // Hide all dynamic containers (result, scan, etc.)
// //     document.querySelectorAll('.page-container').forEach(container => {
// //         container.style.display = 'none';
// //     });

// //     // Handle routes
// //     if (route === 'home') {
// //         // Show main layout again
// //         sections.forEach(sel => {
// //             const el = document.querySelector(sel);
// //             if (el) el.style.display = 'block';
// //         });
// //         return;
// //     }

// //     // For result, scan, compare, etc.
// //     try {
// //         const response = await fetch(`./components/${route}.html`);
// //         const resultHTML = await response.text();

// //         // Create or update container
// //         let container = document.getElementById(route);
// //         if (!container) {
// //             container = document.createElement('div');
// //             container.id = route;
// //             container.classList.add('page-container'); // pick up CSS styles
// //             mainContent.appendChild(container);
// //         }

// //         // Parse HTML and extract matching section
// //         const parser = new DOMParser();
// //         const doc = parser.parseFromString(resultHTML, 'text/html');
// //         const bodyContent = doc.querySelector(`#${route}`);

// //         container.innerHTML = bodyContent ? bodyContent.outerHTML : resultHTML;
// //         container.style.display = 'flex';

// //     } catch (error) {
// //         console.error(`Error loading ${route} page:`, error);
// //     }
// // }
// // Initialize application when DOM is ready
// function initializeApp() {
//     const app = new LancamApp();
//     app.initialize();
    
//     // Store globally for external access
//     window.lancamApp = app;
    
//     // Cleanup on page unload
//     window.addEventListener('beforeunload', () => {
//         app.cleanup();
//     });
// }

// // Start initialization
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', initializeApp);
// } else {
//     initializeApp();
// }



// const container = document.querySelector('.container');
// const LoginLink = document.querySelector('.SignInLink');
// const RegisterLink = document.querySelector('.SignUpLink');

// RegisterLink.addEventListener('click', () =>{
//     container.classList.add('active');
// })

// LoginLink.addEventListener('click', () => {
//     container.classList.remove('active');
// })


// import { LancamApp } from './js/app.js';


// // code to show the login/regitration page.

// function isUserAuthenticated() {
//     return localStorage.getItem('userToken') || 
//            sessionStorage.getItem('isAuthenticated');
// }

// async function showAuthPage() {
//     try {
//         const response = await fetch('./components/login-registration.html');
//         let authHTML = await response.text();
        
//         // Add inline event handlers to avoid timing issues
//         authHTML = authHTML.replace(
//             'class="SignUpLink"', 
//             'class="SignUpLink" onclick="switchToRegister()"'
//         );
//         authHTML = authHTML.replace(
//             'class="SignInLink"', 
//             'class="SignInLink" onclick="switchToLogin()"'
//         );
//         authHTML = authHTML.replace(
//             'id="login-form"', 
//             'id="login-form" onsubmit="return handleLogin(event)"'
//         );
//         authHTML = authHTML.replace(
//             'id="register-form"', 
//             'id="register-form" onsubmit="return handleRegister(event)"'
//         );
        
//         document.body.innerHTML = authHTML;
        
//     } catch (error) {
//         console.error('Error:', error);
//     }
// }

// // Global functions for inline handlers
// window.switchToRegister = function() {
//     document.querySelector('.container').classList.add('active');
// };

// window.switchToLogin = function() {
//     document.querySelector('.container').classList.remove('active');
// };

// // window.handleLogin = function(event) {
// //     event.preventDefault();
// //     const formData = new FormData(event.target);
// //     const username = formData.get('username');
// //     const password = formData.get('password');
    
// //     if (username && password) {
// //         sessionStorage.setItem('isAuthenticated', 'true');
// //         sessionStorage.setItem('username', username);
// //         initializeMainApp();
// //     }
// //     return false;
// // };

// window.handleLogin = function(event) {
//     event.preventDefault();
    
//     // Set dummy session values
//     sessionStorage.setItem('isAuthenticated', 'true');
//     sessionStorage.setItem('username', 'DummyUser');
    
//     // Directly initialize app
//     initializeMainApp();
    
//     return false;
// };

// window.handleRegister = function(event) {
//     event.preventDefault();
//     const formData = new FormData(event.target);
//     const username = formData.get('username');
//     const email = formData.get('email');
//     const password = formData.get('password');
    
//     if (username && email && password) {
//         alert('Registration successful! Please login.');
//         switchToLogin();
//     }
//     return false;
// };

// function initializeMainApp() {
//     document.body.innerHTML = '<div>Loading main app...</div>';
//     const app = new LancamApp();
//     app.initialize();
//     window.lancamApp = app;
// }

// function initializeApp() {
//     if (isUserAuthenticated()) {
//         initializeMainApp();
//     } else {
//         showAuthPage();
//     }
// }

// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', initializeApp);
// } else {
//     initializeApp();
// }

// function initializeApp() {
//     const app = new LancamApp();
//     app.initialize();
    
//     // Store globally for external access
//     window.lancamApp = app;
    
//     // Cleanup on page unload
//     window.addEventListener('beforeunload', () => {
//         app.cleanup();
//     });
// }

// // Start initialization
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', initializeApp);
// } else {
//     initializeApp();
// }

// import { LancamApp } from './js/app.js';

// // check if user is authenticated
// function isUserAuthenticated() {
//     return localStorage.getItem('userToken') || 
//            sessionStorage.getItem('isAuthenticated');
// }

// // show login / register page
// async function showAuthPage() {
//     try {
//         const response = await fetch('./components/login-registration.html');
//         let authHTML = await response.text();
        
//         // Attach inline handlers
//         authHTML = authHTML.replace(
//             'class="SignUpLink"', 
//             'class="SignUpLink" onclick="switchToRegister()"'
//         );
//         authHTML = authHTML.replace(
//             'class="SignInLink"', 
//             'class="SignInLink" onclick="switchToLogin()"'
//         );
//         authHTML = authHTML.replace(
//             'id="login-form"', 
//             'id="login-form" onsubmit="return handleLogin(event)"'
//         );
//         authHTML = authHTML.replace(
//             'id="register-form"', 
//             'id="register-form" onsubmit="return handleRegister(event)"'
//         );
        
//         document.body.innerHTML = authHTML;
        
//     } catch (error) {
//         console.error('Error:', error);
//     }
// }

// // switch to register form
// window.switchToRegister = function() {
//     document.querySelector('.container').classList.add('active');
// };

// // switch to login form
// window.switchToLogin = function() {
//     document.querySelector('.container').classList.remove('active');
// };

// // ✅ Dummy Login (username + password required)
// window.handleLogin = function(event) {
//     event.preventDefault();

//     const formData = new FormData(event.target);
//     const username = formData.get('username');
//     const password = formData.get('password');

//     if (username && password) {
//         // store session
//         sessionStorage.setItem('isAuthenticated', 'true');
//         sessionStorage.setItem('username', username);

//         // load main app
//         // initializeMainApp();
//          initializeApp();
//     } else {
//         alert("⚠️ Please enter username and password!");
//     }

//     return false;
// };

// // ✅ Dummy Register
// window.handleRegister = function(event) {
//     event.preventDefault();
//     const formData = new FormData(event.target);
//     const username = formData.get('username');
//     const email = formData.get('email');
//     const password = formData.get('password');
    
//     if (username && email && password) {
//         alert('✅ Registration successful! Please login.');
//         switchToLogin();
//     } else {
//         alert("⚠️ Please fill all fields!");
//     }
//     return false;
// };

// // initialize main app
// // function initializeMainApp() {
// //     document.body.innerHTML = '<div>Loading main app...</div>';
// //     const app = new LancamApp();
// //     app.initialize();
// //     window.lancamApp = app;
// // }

// // first check authentication
// function initializeApp() {
//     if (isUserAuthenticated()) {
//         const app=new LancamApp();
//         app.initialize();
//         window.lancamApp= app;
//         //clean up on page unload..
//         window.addEventListener('beforeunload', () => {
//             app.cleanup();
//         });
//     } else {
//         showAuthPage();
//     }
// }

// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', initializeApp);
// } else {
//     initializeApp();
// }


// import { LancamApp } from './js/app.js';

// // ✅ Always set authentication on load
// function forceLogin() {
//     sessionStorage.setItem('isAuthenticated', 'true');
//     sessionStorage.setItem('username', 'DummyUser'); // default user
// }

// // ✅ Main app loader
// function initializeMainApp() {
//     const app = new LancamApp();
//     app.initialize();
//     window.lancamApp = app;

//     // cleanup on unload
//     window.addEventListener('beforeunload', () => {
//         app.cleanup();
//     });
// }

// // ✅ Entry point
// function initializeApp() {
//     forceLogin();           // <-- Direct login force kar diya
//     initializeMainApp();    // <-- Direct app load ho jayega
// }

// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', initializeApp);
// } else {
//     initializeApp();
// }


import { LancamApp } from './js/app.js';

// check if user is authenticated
function isUserAuthenticated() {
    return localStorage.getItem('userToken') || 
           sessionStorage.getItem('isAuthenticated');
}

// show login / register page
async function showAuthPage() {
    try {
        const response = await fetch('./components/login-registration.html');
        let authHTML = await response.text();
        
        // Attach inline handlers
        authHTML = authHTML.replace(
            'class="SignUpLink"', 
            'class="SignUpLink" onclick="switchToRegister()"'
        );
        authHTML = authHTML.replace(
            'class="SignInLink"', 
            'class="SignInLink" onclick="switchToLogin()"'
        );
        authHTML = authHTML.replace(
            'id="login-form"', 
            'id="login-form" onsubmit="return handleLogin(event)"'
        );
        authHTML = authHTML.replace(
            'id="register-form"', 
            'id="register-form" onsubmit="return handleRegister(event)"'
        );
        
        document.body.innerHTML = authHTML;
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// switch to register form
window.switchToRegister = function() {
    document.querySelector('.container').classList.add('active');
};

// switch to login form
window.switchToLogin = function() {
    document.querySelector('.container').classList.remove('active');
};

// ✅ Login handler (username + password required)
window.handleLogin = function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const username = formData.get('username');
    const password = formData.get('password');

    if (1==1) {
        // store session
        sessionStorage.setItem('isAuthenticated', 'true');
        sessionStorage.setItem('username', username);

        // 🔥 Ab sirf main app load hoga, login page skip ho jayega
        // window.location.reaload();
        // initializeMainApp();
        // window.location.href = './index.html';
        window.location.reload();
    } else {
        alert("⚠️ Please enter username and password!");
    }

    return false;
};

// ✅ Register handler
window.handleRegister = function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const username = formData.get('username');
    const email = formData.get('email');
    const password = formData.get('password');
    
    if (username && email && password) {
        alert('✅ Registration successful! Please login.');
        switchToLogin();
    } else {
        alert("⚠️ Please fill all fields!");
    }
    return false;
};

// ✅ Main app
function initializeMainApp() {
    const app = new LancamApp();
    app.initialize();
    window.lancamApp = app;

    // cleanup on page unload
    window.addEventListener('beforeunload', () => {
        app.cleanup();
    });
}

// ✅ Entry point
function initializeApp() {
    if (isUserAuthenticated()) {
        // window.location.reload();
        initializeMainApp();
    } else {
        showAuthPage();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

//  function setActive(el){
//         document.querySelectorAll('.settings-light-btn').forEach(e=>e.classList.remove('active'));
//         el.classList.add('active');
//       }