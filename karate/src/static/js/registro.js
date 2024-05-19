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

         // Cuando se desenfoca el input, quitar la validación por espacio
         this.addEventListener('blur', evt => {
            if (this.id !== 'password') {
                this.value = $.trim(this.value)
            }
            this.classList.remove('is-valid')
            this.classList.remove('is-invalid')
        }, true)

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
    })
}