(async ()=>{
    let session = getCookie('session')
    let partner_id = getCookie('partner')
    if(session && partner_id){
        let sessionValidation = await postData('/api/validateSession', { 
            partner_id: parseInt(partner_id), 
            session: session 
        })
        if(sessionValidation.result && sessionValidation.result.success && sessionValidation.result.data.accountVerified){
            let loader = document.querySelector('#loader')                
            loader.classList.add('hidden')
        } else if (sessionValidation.result && sessionValidation.result.success && !sessionValidation.result.data.accountVerified){
            let loader = document.querySelector('#loader')                
            loader.classList.add('hidden')
            window.location.href = '/emailVerification'
        } else if( sessionValidation.result && !sessionValidation.result.success) {
            alert(sessionValidation.result.message)
        } else {
            window.location.href = '/login'
        }
    } else {
        window.location.href = '/login'
    }

    document.addEventListener('click', async function(event){
        if(event.target.matches('.logoutButton')){
            event.preventDefault()
            document.cookie.split(";").forEach(function(c) {
                document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
            });
            window.location.href = '/login'
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