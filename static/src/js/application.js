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

            let statesDropdown = document.querySelector('#state')
            let statesOptions = statesDropdown.querySelectorAll('option')
            Array.from(statesOptions).forEach(option => {
                if (option.dataset.countryId == event.target.options[event.target.selectedIndex].value) {
                    option.classList.remove('hidden')
                } else {
                    option.classList.add('hidden')
                }
            })

            console.log(statesOptions)
            const countryStateOptions = Array.from(statesOptions).filter(option => !option.classList.contains('hidden'))
            if (countryStateOptions.length > 0) {
                statesDropdown.required = true
            } else {
                statesDropdown.required = false
            }
            statesDropdown.selectedIndex = countryStateOptions.length ? countryStateOptions[0].index : -1

        }
        if (event.target.matches('#university')) {
            console.log('university changed')
            let programsDropdown = document.querySelector('#program')
            let programsOptions = programsDropdown.querySelectorAll('option')
            Array.from(programsOptions).forEach(option => {
                if (option.dataset.universityId == event.target.options[event.target.selectedIndex].dataset.id) {
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

            let programDocuments = document.querySelectorAll('.uploadFieldWrapper')

            Array.from(programDocuments).forEach(inputWrapper => {
                if (inputWrapper.dataset.program != programsDropdown[programsDropdown.selectedIndex].dataset.id) {
                    inputWrapper.classList.add('hidden')
                } else {
                    inputWrapper.classList.remove('hidden')
                }
            })

        }
        if (event.target.matches('#program')) {
            let programsDropdown = event.target
            let programDocuments = document.querySelectorAll('.uploadFieldWrapper')
            Array.from(programDocuments).forEach(inputWrapper => {
                if (inputWrapper.dataset.program != programsDropdown[programsDropdown.selectedIndex].dataset.id) {
                    inputWrapper.classList.add('hidden')
                } else {
                    inputWrapper.classList.remove('hidden')
                }
            })
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