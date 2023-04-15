(async ()=>{
    let session = getCookie('session')
    let partner_id = getCookie('partner')

    console.log(session, partner_id)
    if(session && partner_id){
        let sessionValidation = await postData('/api/validateSession', { 
            partner_id: parseInt(partner_id), 
            session: session 
        })
        if(sessionValidation.result && sessionValidation.result.success && sessionValidation.result.data.accountVerified){
            window.location.href = '/dashboard'
        } else if (sessionValidation.result && sessionValidation.result.success && !sessionValidation.result.data.accountVerified){
            window.location.href = '/emailVerification'
        } else if( sessionValidation.result && !sessionValidation.result.success) {
            alert(sessionValidation.result.message)
        } else {

        }
    } else {
        document.body.classList.remove('hidden')
    }

    document.addEventListener('click', async function(event){
        if(event.target.id == 'loginButton'){
            event.preventDefault()
            event.target.classList.add('disabled')
            const email = document.querySelector('#email').value
            const password = document.querySelector('#password').value
            const stayLoggedIn = document.querySelector('#remember-me').checked
            let login = await postData('/api/login', { email: email, password: password })
            if(login.result && login.result.success){
                if(stayLoggedIn){
                    sessionStorage.stayLoggedIn = true
                    const expiryDate = new Date();
                    expiryDate.setTime(expiryDate.getTime() + (365 * 24 * 60 * 60 * 1000));
                    var expires = "expires="+expiryDate.toUTCString();
                    document.cookie = `session=${login.result.data.session};${expires};path=/`
                    document.cookie = `partner=${login.result.data.partner};${expires};path=/`
                } else {
                    document.cookie = `session=${login.result.data.session};path=/`
                    document.cookie = `partner=${login.result.data.partner};path=/`
                }
                window.location.href = '/dashboard'
            } else if(login.result && !login.result.success){
                event.target.classList.remove('disabled')
                alert(login.result.message)
            }
        }
    }, false)

    function getCookie(cookieName) {
        var name = cookieName + "=";
        var decodedCookie = decodeURIComponent(document.cookie);
        var ca = decodedCookie.split(';');
        for(var i = 0; i <ca.length; i++) {
          var c = ca[i];
          while (c.charAt(0) == ' ') {
            c = c.substring(1);
          }
          if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
          }
        }
        return "";
    }

    async function postData(url = '', data = {}) {
        // Default options are marked with *
        const response = await fetch(url, {
          method: 'POST', // *GET, POST, PUT, DELETE, etc.
          mode: 'cors', // no-cors, *cors, same-origin
          cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
          credentials: 'same-origin', // include, *same-origin, omit
          headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
          },
          redirect: 'follow', // manual, *follow, error
          referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
          body: JSON.stringify(data) // body data type must match "Content-Type" header
        });
        return response.json(); // parses JSON response into native JavaScript objects
    }
    
})()
