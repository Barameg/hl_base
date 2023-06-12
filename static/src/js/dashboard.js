
(async ()=>{
    document.addEventListener('click', async function(event){
        if (event.target.matches('#closeSidebar')) {
            let offCanvasMenuBackdrop = document.querySelector('#offCanvasMenuBackdrop')
            let offCanvasMenu = document.querySelector('#offCanvasMenu')
            offCanvasMenuBackdrop.classList.add('hidden')
            offCanvasMenu.classList.add('hidden')
        }
        if (event.target.matches('#openSidebar')) {
            let offCanvasMenuBackdrop = document.querySelector('#offCanvasMenuBackdrop')
            let offCanvasMenu = document.querySelector('#offCanvasMenu')
            offCanvasMenuBackdrop.classList.remove('hidden')
            offCanvasMenu.classList.remove('hidden')
        }
        if(event.target.matches('.logoutButton')){
            event.preventDefault()
            document.cookie.split(";").forEach(function(c) {
                document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
            });
            window.location.href = '/login'
        }
    }, false)

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