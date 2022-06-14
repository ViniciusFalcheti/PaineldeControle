


document.getElementById('logout').onclick = function logout() {
    let token = localStorage.getItem('token')
    // use your favourite AJAX lib to send the token to the server as e.g. JSON
    // redirect user to e.g. landing page of app if logout successul, show error otherwise
}