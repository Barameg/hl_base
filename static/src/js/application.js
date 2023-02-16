(async () => {
    let docs = {}
    let session = getCookie('session')
    let partner_id = getCookie('partner')
    if (session && partner_id) {
        let sessionValidation = await postData('/api/validateSession')
        if (sessionValidation.result && sessionValidation.result.success && sessionValidation.result.data.accountVerified) {
            document.body.classList.remove('hidden')

            const urlParams = new URLSearchParams(window.location.search);
            const applicationId = urlParams.get("id");
            let nationalityDropdown = document.querySelector('#nationality')
            let countriesDropdown = document.querySelector('#country')
            let statesDropdown = document.querySelector('#state')
            let universitiesDropdown = document.querySelector('#university')
            let programsDropdown = document.querySelector('#program')
            let programDocumentsWrapper = document.querySelector('#programDocuments')

            let countriesRequest = await postData('/api/countries')
            for (const country of countriesRequest.result.data.countries) {
                const nationalityOption = document.createElement('option')
                nationalityOption.id = country.id
                nationalityOption.value = country.id
                nationalityOption.innerText = country.name
                nationalityDropdown.append(nationalityOption)
                const countryOption = document.createElement('option')
                countryOption.id = country.id
                countryOption.value = country.id
                countryOption.innerText = country.name
                countriesDropdown.append(countryOption)
            }

            let statesRequest = await postData('/api/states', {
                country: countriesDropdown.options[countriesDropdown.selectedIndex].id
            })
            if(statesRequest.result.data.states.length > 0){
                for (const state of statesRequest.result.data.states) {
                    const option = document.createElement('option')
                    option.id = state.id
                    option.value = state.id
                    option.innerText = state.name
                    statesDropdown.append(option)
                }
                stateWrapper.style.display = 'grid'
            } else {
                stateWrapper.style.display = 'none'
            }

            let universitiesRequest = await postData('/api/universities')
            for (const university of universitiesRequest.result.data.universities) {
                const option = document.createElement('option')
                option.id = university.id
                option.value = university.id
                option.innerText = university.name
                universitiesDropdown.append(option)
            }

            let programsRequest = await postData('/api/programs', {
                university: universitiesDropdown.options[universitiesDropdown.selectedIndex].id
            })
            programsDropdown.innerHTML = ''
            for (const program of programsRequest.result.data.programs) {
                const option = document.createElement('option')
                option.id = program.id
                option.value = program.id
                option.innerText = program.name
                programsDropdown.append(option)
            }
            let programDocumentsRequest = await postData('/api/documents', {
                program: programsDropdown.options[programsDropdown.selectedIndex].id
            })
            for (const doc of programDocumentsRequest.result.data.documents) {                
                docs[toCamelCase(doc.name)] = {
                    allowed_size: doc.allowed_size,
                    allowed_types: doc.allowed_types
                }
                console.log(docs)
                const documentElementHTML = `
                <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:border-t sm:border-gray-200 sm:pt-5">
                    <label for="${toCamelCase(doc.name)}" class="block text-sm font-medium text-gray-700 sm:mt-px sm:pt-2">${doc.name}</label>
                    <input ${doc.required ? 'required' : ''} type="file" name="${toCamelCase(doc.name)}" id="${toCamelCase(doc.name)}" class="block w-full appearance-none rounded-md border border-gray-300 px-3 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm" placeholder="www.example.com">
                </div>`
                programDocumentsWrapper.insertAdjacentHTML('beforeend', documentElementHTML)
            }

            if(applicationId){
                let applicationRequest = await postData('/api/applications',{
                    id: applicationId
                })
                if(applicationRequest.result.data.applications.length > 0){
                    let application = applicationRequest.result.data.applications[0]
                    document.querySelector('#firstName').value = application.first_name
                    document.querySelector('#middleName').value = application.middle_name
                    document.querySelector('#lastName').value = application.last_name
                    document.querySelector('#dob').value = application.dob
                    document.querySelector('#passport_number').value = application.passport_number
                    document.querySelector('#passport_issue').value = application.passport_issue_date
                    document.querySelector('#passport_expiry').value = application.passport_expiry_date
                    document.querySelector('#address_line_1').value = application.address_line_1
                    document.querySelector('#address_line_2').value = application.address_line_2
                    document.querySelector('#city').value = application.city
                    document.querySelector('#state').value = application.state ? application.state[0] : ''
                    document.querySelector('#country').value = application.country ? application.country[0] : ''
                    document.querySelector('#university').value = application.university ? application.university[0] : ''
                    document.querySelector('#program').value = application.program ? application.program[0] : ''
                } else {

                }
            } else {
                console.log('wooooooo')
            }


        } else if (sessionValidation.result && sessionValidation.result.success && !sessionValidation.result.data.accountVerified) {
            window.location.href = '/emailVerification'
        } else if (sessionValidation.result && !sessionValidation.result.success) {
            alert(sessionValidation.result.message)
        } else {
            window.location.href = '/login'
        }
    } else {
        window.location.href = '/login'
    }

    document.addEventListener('submit', function(event){
        console.log(event.target)
    })
    document.addEventListener('click', async function (event) {
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
        if (event.target.matches('.logoutButton')) {
            event.preventDefault()
            document.cookie.split(";").forEach(function (c) {
                document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
            });
            window.location.href = '/login'
        }
        if (event.target.matches('#cancelApplication')) {
            event.preventDefault()
            window.location.href = '/dashboard'

        }
        if (event.target.matches('#saveApplication')) {
            event.preventDefault()
            event.target.classList.add('disabled')
            let form = event.target.closest('form')
            if(form.checkValidity()){
                let first_name = document.querySelector('#firstName').value
                let middle_name = document.querySelector('#middleName').value
                let last_name = document.querySelector('#lastName').value
                let gender = document.querySelector('input[name="gender"]:checked').value
                let dob = document.querySelector('#dob').value
                // father_first_name = fields.Char()
                // father_last_name = fields.Char()
                // mother_first_name = fields.Char()
                // mother_last_name = fields.Char()
                let marital_status = document.querySelector('input[name="marital_status"]:checked').value
                let nationalityElement = document.querySelector('#nationality')
                let nationality = nationalityElement.options[nationalityElement.selectedIndex].id
                let passport_number = document.querySelector('#passport_number').value
                let passport_issue_date = document.querySelector('#passport_issue').value
                let passport_expiry_date = document.querySelector('#passport_expiry').value
                let contact_number = document.querySelector('#nationality').value
                let address_line_1 = document.querySelector('#address_line_1').value
                let address_line_2 = document.querySelector('#address_line_2').value
                let city = document.querySelector('#city').value
                let stateElement = document.querySelector('#state')
                let state;
                try {
                    state = stateElement.options[stateElement.selectedIndex].id
                } catch(e){
                    state = ''
                }
                // let zipcode = document.querySelector('#zipcode').value
                let countryElement = document.querySelector('#country')
                let country = countryElement.options[countryElement.selectedIndex].id
                let universityElement = document.querySelector('#university')
                let university = universityElement.options[universityElement.selectedIndex].id
                let programElement = document.querySelector('#program')
                let program = programElement.options[programElement.selectedIndex].id
                const urlParams = new URLSearchParams(window.location.search);
                const applicationId = urlParams.get("id");
                let jsonData = {
                    id: applicationId ? applicationId : '',
                    first_name: first_name,
                    middle_name: middle_name,
                    last_name: last_name,
                    gender: gender,
                    dob:dob,
                    // father_first_name: fields.Char()
                    // father_last_name: fields.Char()
                    // mother_first_name: fields.Char()
                    // mother_last_name: fields.Char()
                    marital_status: marital_status,
                    nationality: nationality,
                    passport_number: passport_number,
                    passport_issue_date: passport_issue_date,
                    passport_expiry_date: passport_expiry_date,
                    // contact_number: contact_number,
                    address_line_1: address_line_1,
                    address_line_2: address_line_2,
                    city: city,
                    state: state,
                    // zipcode: zipcode,
                    country: country,
                    university: university,
                    program: program
                }
                const formData = new FormData();
                formData.append('jsonData', JSON.stringify(jsonData));
    
                let docs = document.querySelectorAll('input[type="file"]')
                for(const doc of docs){
                    formData.append(camelToSpace(doc.id), doc.files[0]);
                }
    
                let applicationRequest = await postForm('/api/saveApplication', formData)
                if(applicationRequest.success ){
                    window.location.href = '/dashboard'
                } else {
                    alert(applicationRequest.message)
                    event.target.classList.remove('disabled')
                }
            } else {
                form.reportValidity()
                event.target.classList.remove('disabled')
            }
        }
        

    }, false)
    document.addEventListener('change', async function (event) {
        event.preventDefault() 
        event.stopPropagation()
        if(event.target.matches('#country')){
            let countriesDropdown = event.target
            let statesDropdown = document.querySelector('#state')
            let stateWrapper = document.querySelector('#stateWrapper')
            statesDropdown.innerHTML = ''
            let statesRequest = await postData('/api/states', {
                country: countriesDropdown.options[countriesDropdown.selectedIndex].id
            })
            if(statesRequest.result.data.states.length > 0){
                for (const state of statesRequest.result.data.states) {
                    const option = document.createElement('option')
                    option.id = state.id
                    option.innerText = state.name
                    statesDropdown.append(option)
                }
                stateWrapper.style.display = 'grid'
            } else {
                stateWrapper.style.display = 'none'
            }

        }
        if(event.target.matches('#university')){
            let universitiesDropdown = event.target
            let programsRequest = await postData('/api/programs', {
                university: universitiesDropdown.options[universitiesDropdown.selectedIndex].id
            })
            let programsDropdown = document.querySelector('#program')
            programsDropdown.innerHTML = ''
            for (const program of programsRequest.result.data.programs) {
                const option = document.createElement('option')
                option.id = program.id
                option.innerText = program.name
                programsDropdown.append(option)
            }
            let programDocumentsRequest = await postData('/api/documents', {
                program: programsDropdown.options[programsDropdown.selectedIndex].id
            })
            let programDocumentsWrapper = document.querySelector('#programDocuments')
            programDocumentsWrapper.innerHTML = ''
            for (const doc of programDocumentsRequest.result.data.documents) {
                const documentElementHTML = `
                <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:border-t sm:border-gray-200 sm:pt-5">
                    <label for="${toCamelCase(doc.name)}" class="block text-sm font-medium text-gray-700 sm:mt-px sm:pt-2">${doc.name}</label>
                    <input required="true" type="file" name="${toCamelCase(doc.name)}" id="${toCamelCase(doc.name)}" class="block w-full appearance-none rounded-md border border-gray-300 px-3 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm" placeholder="www.example.com">
                </div>`
                programDocumentsWrapper.insertAdjacentHTML('beforeend',documentElementHTML)
            }
        }
        if(event.target.matches('#program')){
            let programsDropdown = event.target
            let programDocumentsRequest = await postData('/api/documents', {
                program: programsDropdown.options[programsDropdown.selectedIndex].id
            })
            let programDocumentsWrapper = document.querySelector('#programDocuments')
            programDocumentsWrapper.innerHTML = ''
            for (const doc of programDocumentsRequest.result.data.documents) {
                const documentElementHTML = `
                <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:border-t sm:border-gray-200 sm:pt-5">
                    <label for="${toCamelCase(doc.name)}" class="block text-sm font-medium text-gray-700 sm:mt-px sm:pt-2">${doc.name}</label>
                    <input required="true" type="file" name="${toCamelCase(doc.name)}" id="${toCamelCase(doc.name)}" class="block w-full appearance-none rounded-md border border-gray-300 px-3 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm" placeholder="www.example.com">
                </div>`
                programDocumentsWrapper.insertAdjacentHTML('beforeend',documentElementHTML)
            }
        }
        if(event.target.matches('input[type="file"]')){
            console.log(event.target.files)
            if(event.target.files.length > 0 ){
                let exceedsLimit = false
                if(event.target.files[0].size > docs[event.target.name].allowed_size * 1024 * 1024){
                    exceedsLimit = true
                    alert(`file exceeds limit of ${docs[event.target.name].allowed_size} MB`)
                }
                let typeFound = false
                for(const type of docs[event.target.name].allowed_types.split(',')){
                    if(event.target.files[0].type.includes(type.trim())) typeFound = true
                }
                if(!typeFound || exceedsLimit){
                    event.target.value = ''
                    alert(`Only files not exceeding ${docs[event.target.name].allowed_types} MB and of type ${docs[event.target.name].allowed_types} are allowed`)
                }
            }
        }

    })

    function getCookie(cookieName) {
        var name = cookieName + "=";
        var decodedCookie = decodeURIComponent(document.cookie);
        var ca = decodedCookie.split(';');
        for (var i = 0; i < ca.length; i++) {
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
    function toCamelCase(str) {
        let words = str.split(' ');
        for (let i = 1; i < words.length; i++) {
            words[i] = words[i][0].toUpperCase() + words[i].slice(1).toLowerCase();
        }
        return words.join('');
    }
    function camelToSpace(str) {
        return str.replace(/([A-Z])/g, ' $1').trim();
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
    async function postForm(url = '', formData = new FormData()) {
        // Default options are marked with *
        const response = await fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            body: formData // body data type must match "Content-Type" header
        });
        return response.json(); // parses JSON response into native JavaScript objects
    }
})()