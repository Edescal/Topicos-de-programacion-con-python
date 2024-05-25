const form = document.getElementById('form-registro')
if (form) {
    $(`#${form.id} :input`).each(function() {
        console.log(this)
        this.addEventListener('input', evt => { 
            if (this.value === '') {
                console.log(`Input vacío: ${this.name}`)
                this.classList.remove('is-valid')
                this.classList.remove('is-invalid')
                return
            } 
            // Algunos inputs tienen un mínimo de caracteres
            let minlength = this.getAttribute('minlength')
            let muycorto = minlength !== null &&  this.value.length < minlength
            if (!this.checkValidity() || muycorto) {
                console.log(`Input no válido: ${this.name}`)
                this.classList.remove('is-valid')
                this.classList.add('is-invalid')
            } else {
                console.log(`Input válido: ${this.name}`)
                this.classList.add('is-valid')
                this.classList.remove('is-invalid')
            }
        })     

        // Cuando se desenfoca el input, quitar la validación y espacios
        this.addEventListener('blur', evt => {
            // si es nombre o apellido capitalizar
            if (this.name == 'nombres' || this.name.match('apellido')){
                this.value = capitalize(this.value)
            }

            // quitar los espacios con trim()
            if (this.id !== 'password') {
                this.value = $.trim(this.value)
            }
            this.classList.remove('is-valid')
            this.classList.remove('is-invalid')
        }, true)

        // Validar cuando se enfoca el input
        this.addEventListener('focus', evt => {
            if (!this.checkValidity()) {
                console.log(`Input no válido: ${this.name}`)
                this.classList.remove('is-valid')
                this.classList.add('is-invalid')
            } else {
                console.log(`Input válido: ${this.name}`)
                this.classList.add('is-valid')
                this.classList.remove('is-invalid')
            }
        }, true)
    })

    // evento para validar antes de enviar el formulario
    form.addEventListener('submit', evt => {
        if (!form.checkValidity()) {
            console.log('Formulario no validado - no enviado')
            evt.preventDefault()
            evt.stopPropagation()

            $(`#${form.id} :input`).each(function() {
                if (!this.checkValidity()) {
                    console.log(`Input no válido: ${this.name}`)
                    this.classList.remove('is-valid')
                    this.classList.add('is-invalid')
                } else {
                    this.classList.add('is-valid')
                    this.classList.remove('is-invalid')
                }
            })
        }
    }, true)
}

/*
    FUNCIÓN PARA CAPITALIZAR LOS NOMBRES
*/
function capitalize(input){
    let split = input.split(' ')
    let result = ''
    for (var i = 0; i < split.length; i++) {
        let palabra = split[i].toLowerCase()
        if (palabra == null || palabra.length == 0) {
            continue
        }
        palabra = palabra[0].toUpperCase() + palabra.slice(1)
        result = result.concat(` ${palabra}`)
    }
    return result
        .replace(' De ', ' de ').replace(' La ', ' la ')
        .replace(/\-[a-z]/g, char => char.toUpperCase())
}

console.log( capitalize('astrid de la lastra lópez-gatell') )

function replaceregex(input) { 

    let res = input.replace(/\-[a-z]/g, char => char.toUpperCase())
    console.log(res)
 }
