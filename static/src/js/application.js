(async () => {
    let docs = {}
    let currentStep = 0
    document.addEventListener('click', async function (event) {
        let form = document.querySelector('form')
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
            let currentStepInputs = document.querySelectorAll('.step')[currentStep].querySelectorAll('input[required="true"]')
            let currentStepSelections = document.querySelectorAll('.step')[currentStep].querySelectorAll('select[required="true"]')
            console.log(currentStepInputs)
            let stepValid = true
            for (const input of currentStepInputs) {
                console.log(input)
                if (input.value == '') {
                    stepValid = false
                    break
                }
            }
            for (const select of currentStepSelections) {
                if (select.value == '') {
                    stepValid = false
                    break
                }
            }
            if (!stepValid) {
                form.reportValidity()
            } else {
                let steps = document.querySelectorAll('ol li')
                let currentStepButtons = steps[currentStep].querySelectorAll('a')
                document.querySelectorAll('.step')[currentStep].classList.add('hidden')
                console.log(currentStepButtons)
                currentStepButtons[0].classList.add('hidden')
                currentStepButtons[1].classList.remove('hidden')
                currentStep++
                console.log(currentStep)
                if (currentStep > 0) {
                    event.target.previousElementSibling.classList.remove('hidden')
                }
                if (currentStep == 3) {
                    event.target.classList.add('hidden')
                    event.target.nextElementSibling.classList.remove('hidden')
                }
                currentStepButtons = steps[currentStep].querySelectorAll('a')
                document.querySelectorAll('.step')[currentStep].classList.remove('hidden')
                console.log(currentStepButtons)
                currentStepButtons[0].classList.remove('hidden')
                currentStepButtons[1].classList.add('hidden')
            }
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
            if (currentStep == 0) {
                event.target.classList.add('hidden')
            }
            if (currentStep < 3) {
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

    }, false)
    document.addEventListener('change', async function (event) {
        // event.preventDefault() 
        // event.stopPropagation()
        if (event.target.matches('#country')) {
            let statesResponse = await fetch(`/api/listStates?country=${event.target.value}`)
            let statesContent = await statesResponse.text()

            let states = JSON.parse(statesContent)

            let statesDropdown = document.querySelector('#state')
            statesDropdown.innerHTML = ''

            for(const state of states){
                let stateOption = document.createElement('option')
                stateOption.setAttribute('data-id', state.id)
                stateOption.setAttribute('value', state.id)
                stateOption.innerText = state.name
                statesDropdown.append(stateOption)
            }

        }
        if (event.target.matches('#university')) {
            console.log('university changed')

            let programsDropdown = document.querySelector('#program')
            programsDropdown.innerHTML = ''

            let programsResponse = await fetch(`/api/listPrograms?university=${event.target.value}`)
            let programsContent = await programsResponse.text()
            let programs = JSON.parse(programsContent)


            for await (const [key, program] of Object.entries(programs)){
                if(key == programs.length){
                    let programOption = document.createElement('option')
                    programOption.setAttribute('data-id', program.id)
                    programOption.setAttribute('value', program.id)
                    programOption.innerText = program.name
                    programsDropdown.append(programOption)
                }
                let programOption = document.createElement('option')
                programOption.setAttribute('data-id', program.id)
                programOption.setAttribute('value', program.id)
                programOption.innerText = program.name
                programsDropdown.append(programOption)
            }
            let program = programsDropdown[0].dataset.id
            let documentsResponse = await fetch(`/api/listDocuments?program=${program}`)
            let documentsContent = await documentsResponse.text()
            let documents = JSON.parse(documentsContent)
            let documentsWrapper = document.querySelector('#programDocuments')
            documentsWrapper.innerHTML = ''

            for(const document of documents){
                let htmlContent = `
                    <div class="uploadFieldWrapper" data-program="${program.id}">
                        <label class="block mb-2 text-sm font-medium text-gray-900" for="${document.uuid}">
                            ${document.name} ${document.template ? 'You can download template <a class="text-sm font-medium text-current group-hover:text-current" href="/template/' + document.uuid + '">from here</a>' : ''}
                        </label>
                        <input name="${document.uuid}" required="${document.required}" data-allowed-size="${document.allowed_size}" data-allowed-types="${document.allowed_types}" class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none" id="${document.uuid}" type="file"/>
                    </div>`
                documentsWrapper.insertAdjacentHTML('afterbegin', htmlContent)
            }

        }
        if (event.target.matches('#program')) {
            console.log('program changed')
            console.log(event.target)
            let programsDropdown = event.target
            let programDocuments = document.querySelectorAll('.uploadFieldWrapper')

            let documentsResponse = await fetch(`/api/listDocuments?program=${event.target.value}`)
            let documentsContent = await documentsResponse.text()

            let documents = JSON.parse(documentsContent)
            console.log(documents)
            let documentsWrapper = document.querySelector('#programDocuments')
            documentsWrapper.innerHTML = ''

            for(const document of documents){
                let htmlContent = `
                    <div class="uploadFieldWrapper" data-program="${program}">
                        <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="${document.uuid}">
                            ${document.name} ${document.template ? 'You can download template <a class="text-sm font-medium text-current group-hover:text-current" href="/template/' + document.uuid + '">from here</a>' : ''}
                        </label>
                        <input name="${document.uuid}" required="${document.required}" data-allowed-size="${document.allowed_size}" data-allowed-types="${document.allowed_types}" class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" id="${document.uuid}" type="file"/>
                    </div>`
                documentsWrapper.insertAdjacentHTML('afterbegin', htmlContent)
            }
        }
        
        if (event.target.matches('input[type="file"]')) {
            if (event.target.files.length > 0) {
                let exceedsLimit = false
                let allowedSize = event.target.dataset.allowedSize
                let allowedTypes = event.target.dataset.allowedTypes
                if (event.target.files[0].size > allowedSize * 1024 * 1024) {
                    exceedsLimit = true
                }
                let typeFound = false
                let types = allowedTypes.split(',')
                console.log(types)
                for (const type of types) {
                    if (event.target.files[0].type.includes(type.trim())) typeFound = true
                }
                console.log(typeFound)
                console.log(exceedsLimit)
                if (!typeFound || exceedsLimit) {
                    event.target.value = ''
                    alert(`Only files not exceeding ${allowedSize} MB and of type ${allowedTypes} are allowed`)
                }
            }
        }

        if(event.target.matches('#passport_issue_date')){
            var passport_issue_date = new Date(event.target.value);
            var passport_expiry_date = new Date(passport_issue_date.getFullYear() + 10, passport_issue_date.getMonth(), passport_issue_date.getDate());
            var formattedDate = passport_expiry_date.toISOString().split('T')[0];
            var passport_expiry_date_input = document.querySelector('#passport_expiry_date')
            passport_expiry_date_input.value = formattedDate
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

    let programsDropdown = document.querySelector('#program')
    if(program.value != ''){
        let programDocuments = document.querySelectorAll('.uploadFieldWrapper')
        let documentsResponse = await fetch(`/api/listDocuments?program=${event.target.value}`)
        let documentsContent = await documentsResponse.text()

        let documents = JSON.parse(documentsContent)
        console.log(documents)
        let documentsWrapper = document.querySelector('#programDocuments')
        documentsWrapper.innerHTML = ''

        for(const document of documents){
            let htmlContent = `
                <div class="uploadFieldWrapper" data-program="${program}">
                    <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="${document.uuid}">
                        ${document.name} ${document.template ? 'You can download template <a class="text-sm font-medium text-current group-hover:text-current" href="/template/' + document.uuid + '">from here</a>' : ''}
                    </label>
                    <input name="${document.uuid}" required="${document.required}" data-allowed-size="${document.allowed_size}" data-allowed-types="${document.allowed_types}" class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" id="${document.uuid}" type="file"/>
                </div>`
            documentsWrapper.insertAdjacentHTML('afterbegin', htmlContent)
        }
    }
})()