//let regex = /(^[^\\w]{1,20})$/ Detecta si hay algún caracter especial
/*
let regex = /[^\w]{1,20}/  //Ubica cualquier caracter especial
var user = '__@@s__""_ss_#'
console.log(user)
let res = user.replace(regex, "")
console.log(res)
while(res !== user) {
    user = res
    res = user.replace(regex, "")
    console.log(res)
}

*/
let filter = filter_spec_chars('__admin__')
console.log(filter)

function filter_spec_chars(str) { 
    let regex = /[^\w]{1,20}/
    let res = str.replace(regex, "")
    while(res !== str) {
        str = res
        res = str.replace(regex, "")
    }
    return res
 }
/*
 const username = document.getElementById('username')
 if (username) {
    username.addEventListener('input', evt => {
        let filteredVal = filter_spec_chars(username.value)
        let change = username.value !== filteredVal
        if (change) {
            username.value = filteredVal
            evt.preventDefault()
            evt.stopPropagation()
        }
    })
}
*/


// Buscar todos los formularios para validar
const forms = document.querySelectorAll('.needs-validation')
Array.from(forms).forEach(form => {
    console.log(form)
    // Checar si todo se carga vacío o si hay alguna cosa qué validar
    if (!form.checkValidity()) {
        form.classList.add('was-validated')
        
        allInputs = $(`#${form.id} :input`)
        console.log(allInputs)
        allInputs.each(function() {
            // Funcionalidad individual
            console.log(`Eventos para: ${this.name}`)
            this.addEventListener('input', _ => {
                if (this.value === '') {
                    console.log(`Input vacío: ${this.name}`)
                    //this.classList.remove('is-valid')
                    this.classList.remove('is-invalid')
                    return
                } 
                if (this.id === 'username'){
                    this.value = filter_spec_chars(this.value)
                }
                if (!this.checkValidity() || this.value.length < 5) {
                    console.log(`Input no válido: ${this.name}`)
                    //this.classList.remove('is-valid')
                    this.classList.add('is-invalid')
                } else {
                    console.log(`Input válido: ${this.name}`)
                    //this.classList.add('is-valid')
                    this.classList.remove('is-invalid')
                }
            }, true)

            // Cuando se desenfoca el input, quitar la validación por espacio
            this.addEventListener('blur', _ => {
                //this.classList.remove('is-valid')
                this.classList.remove('is-invalid')
            }, true)

            this.addEventListener('focus', _ => {
                if (!this.checkValidity()) {
                    console.log(`Input no válido: ${this.name}`)
                    ///this.classList.remove('is-valid')
                    this.classList.add('is-invalid')
                } else {
                    console.log(`Input válido: ${this.name}`)
                    //this.classList.add('is-valid')
                    this.classList.remove('is-invalid')
                }
            }, true)
        })

        const checkAllEmpty = () => {
            var allEmpty = true;
            $('#register-form :input').each(function() {
                if (this.id === 'csrf_token') {
                    console.log('TOKEN -> next')
                    return true
                }
                if (this.id === 'next') {
                    console.log('NEXT -> next')
                    return true
                }
                if (this.id === 'submit') {
                    console.log('SUBMIT -> next')
                    return true
                }

                if ($(this).val() !== '' ) {
                    console.log($`${this.id} has value and not token false`)
                    allEmpty = false;
                } else {
                    console.log($`${this.id} is empty, next`)
                }
            })
            return allEmpty
        }

        const clean = checkAllEmpty()
        if (clean){
            form.classList.remove('was-validated')
            console.log('Formulario cargado sin valores iniciales.')
        } else {
            form.classList.add('was-validated')
            console.log('Formulario cargado con algún valor inicial - Iniciando validación')
        }
    }

    // Submit
    form.addEventListener('submit', event => {
        console.log('Submit')
        if (!form.checkValidity()) {
            console.log('No validado')
            event.preventDefault()
            event.stopPropagation()
            $(`#${form.id} :input`).each(function() {
                if (!this.checkValidity()) {
                    console.log(`Input no válido: ${this.name}`)
                    /*
                    this.classList.remove('is-valid')
                    */
                    this.classList.add('is-invalid')
                } else {
                    console.log(`Input válido: ${this.name}`)
                    /*
                    this.classList.add('is-valid')
                    */
                    this.classList.remove('is-invalid')
                }
            })
        } else console.log('Formulario validado')

        //form.classList.add('was-validated')
    }, true)
})