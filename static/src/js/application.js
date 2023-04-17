(async () => {
    let docs = {}
    let currentStep = 0
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
        if (event.target.matches('#nextStepButton')) {
            event.preventDefault()
            let steps = document.querySelectorAll('ol li')
            let currentStepButtons = steps[currentStep].querySelectorAll('a')
            document.querySelectorAll('.step')[currentStep].classList.add('hidden')
            console.log(currentStepButtons)
            currentStepButtons[0].classList.add('hidden')
            currentStepButtons[1].classList.remove('hidden')
            currentStep++
            console.log(currentStep)
            if(currentStep > 0){
                event.target.previousElementSibling.classList.remove('hidden')
            }
            if(currentStep == 3){
                event.target.classList.add('hidden')
                event.target.nextElementSibling.classList.remove('hidden')
            }
            currentStepButtons = steps[currentStep].querySelectorAll('a')
            document.querySelectorAll('.step')[currentStep].classList.remove('hidden')
            console.log(currentStepButtons)
            currentStepButtons[0].classList.remove('hidden')
            currentStepButtons[1].classList.add('hidden')
        }
        if (event.target.matches('#previousStepButton')) {
            event.preventDefault()
            let steps = document.querySelectorAll('ol li')
            let currentStepButtons = steps[currentStep].querySelectorAll('a')
            document.querySelectorAll('.step')[currentStep].classList.add('hidden')
            currentStepButtons[0].classList.add('hidden')
            currentStepButtons[1].classList.remove('hidden')
            currentStep--
            console.log(currentStep)
            if(currentStep == 0){
                event.target.classList.add('hidden')
            }
            if(currentStep < 3){
                let nextButton = event.target.nextElementSibling
                nextButton.classList.remove('hidden')
                nextButton.nextElementSibling.classList.add('hidden')
            }
            currentStepButtons = steps[currentStep].querySelectorAll('a')
            document.querySelectorAll('.step')[currentStep].classList.remove('hidden')
            console.log(currentStepButtons)
            currentStepButtons[0].classList.remove('hidden')
            currentStepButtons[1].classList.add('hidden')
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
                let nationality = nationalityElement.options[nationalityElement.selectedIndex].dataset.id
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
                    state = stateElement.options[stateElement.selectedIndex].dataset.id
                } catch(e){
                    state = ''
                }
                // let zipcode = document.querySelector('#zipcode').value
                let countryElement = document.querySelector('#country')
                let country = countryElement.options[countryElement.selectedIndex].dataset.id
                let universityElement = document.querySelector('#university')
                let university = universityElement.options[universityElement.selectedIndex].dataset.id
                let programElement = document.querySelector('#program')
                let program = programElement.options[programElement.selectedIndex].dataset.id
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
                    nationality: parseInt(nationality),
                    passport_number: passport_number,
                    passport_issue_date: passport_issue_date,
                    passport_expiry_date: passport_expiry_date,
                    // contact_number: contact_number,
                    address_line_1: address_line_1,
                    address_line_2: address_line_2,
                    city: city,
                    state: state,
                    // zipcode: zipcode,
                    country: parseInt(country),
                    university: parseInt(university),
                    program: parseInt(program)
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
        // event.preventDefault() 
        // event.stopPropagation()
        if(event.target.matches('#country')){
            let statesDropdown = document.querySelector('#state')
            let statesOptions = statesDropdown.querySelectorAll('option')
            Array.from(statesOptions).forEach(option=>{
                if(option.dataset.countryId == event.target.options[event.target.selectedIndex].dataset.id){
                    option.classList.remove('hidden')
                } else {
                    option.classList.add('hidden')
                }
            })

            Array.from(statesOptions).filter(option => option.dataset.countryId == event.target.options[event.target.selectedIndex].id).forEach(option=>{
                option.classList.remove('hidden')
            })
            Array.from(statesOptions).filter(option => option.dataset.countryId != event.target.options[event.target.selectedIndex].id).forEach(option=>{
                option.classList.add('hidden')
            })
            const countryStateOptions = Array.from(statesOptions).filter(option => !option.classList.contains('hidden'))
            statesDropdown.selectedIndex = countryStateOptions.length ? countryStateOptions[0].index : -1

        }
        if(event.target.matches('#university')){
            console.log('university changed')
            let programsDropdown = document.querySelector('#program')
            let programsOptions = programsDropdown.querySelectorAll('option')
            Array.from(programsOptions).forEach(option=>{
                if(option.dataset.universityId == event.target.options[event.target.selectedIndex].dataset.id){
                    option.classList.remove('hidden')
                } else {
                    option.classList.add('hidden')
                }
            })
            // Array.from(programsOptions).filter(option => option.dataset.universityId == event.target.options[event.target.selectedIndex].id).forEach(option=>{
            //     option.classList.remove('hidden')
            // })
            // Array.from(programsOptions).filter(option => option.dataset.universityId != event.target.options[event.target.selectedIndex].id).forEach(option=>{
            //     option.classList.add('hidden')
            // })
            const universityProgramOptions = Array.from(programsOptions).filter(option => !option.classList.contains('hidden'))
            programsDropdown.selectedIndex = universityProgramOptions.length ? universityProgramOptions[0].index : -1
        }
        if(event.target.matches('#program')){
            let programsDropdown = event.target
            let programDocuments = document.querySelectorAll('.uploadFieldWrapper')
            Array.from(programDocuments).forEach(inputWrapper =>{
                if(inputWrapper.dataset.program != programsDropdown[programsDropdown.selectedIndex].id){
                    inputWrapper.classList.add('hidden')
                } else {
                    inputWrapper.classList.remove('hidden')
                }
            })
        }
        if(event.target.matches('input[type="file"]')){
            if(event.target.files.length > 0 ){
                let exceedsLimit = false
                let allowedSize = event.target.dataset.allowedSize
                let allowedTypes = event.target.dataset.allowedTypes
                if(event.target.files[0].size > allowedSize * 1024 * 1024){
                    exceedsLimit = true
                }
                let typeFound = false
                for(const type of allowedTypes.split(',')){
                    if(event.target.files[0].type.includes(type.trim())) typeFound = true
                }
                if(!typeFound || exceedsLimit){
                    event.target.value = ''
                    alert(`Only files not exceeding ${allowedSize} MB and of type ${allowedTypes} are allowed`)
                }
            }
        }

    })

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