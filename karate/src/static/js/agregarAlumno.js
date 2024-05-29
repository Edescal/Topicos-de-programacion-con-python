$( () => {
    const forms = document.querySelectorAll('.needs-validation')
    Array.from(forms).forEach(form => {
        // este if se tuvo que poner para que no interfiera con el 
        // formulario de agregar asistencias, por eso esquiva su id
        if (form.id === 'formulario') {
            return
        }

        console.log(`Formulario: ${form.getAttribute('id')}`)
        $(`#${form.getAttribute('id')} :input`).each(function() {
            console.log(`Configurando input: ${this.name}`)
            this.addEventListener('input', evt => { 
                console.log(this.name)
                if (this.value === '') {
                    this.classList.remove('is-valid')
                    this.classList.remove('is-invalid')
                    return
                } 
                // Algunos inputs tienen un mínimo de caracteres
                let minlength = this.getAttribute('minlength')
                let muycorto = minlength !== null &&  this.value.length < minlength
                if (!this.checkValidity() || muycorto) {
                    this.classList.remove('is-valid')
                    this.classList.add('is-invalid')
                } else {
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
                this.value = $.trim(this.value)
                this.classList.remove('is-valid')
                this.classList.remove('is-invalid')
            }, true)

            // Validar cuando se enfoca el input
            this.addEventListener('focus', evt => {
                if (!this.checkValidity()) {
                    this.classList.remove('is-valid')
                    this.classList.add('is-invalid')
                } else {
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
    
                $(`#${form.getAttribute('id')} :input`).each(function() {
                    if (!this.checkValidity()) {
                        console.log(`Input no válido: ${this.name}`)
                        this.classList.remove('is-valid')
                        this.classList.add('is-invalid')
                    } else {
                        this.classList.add('is-valid')
                        this.classList.remove('is-invalid')
                    }
                })
                return false;
            } 
        }, true)
    })

    // settear modal de editar
    $('#editar-modal').on('show.bs.modal', evt => {
        let button = evt.relatedTarget
        let estatusData = $(button).data('estatus')
        let estatusValue = estatusData === 'ACTIVO' ? 1 : estatusData === 'PENDIENTE' ? 2 : 3
        $('#edit-estatus').attr('value', estatusValue).val(estatusValue)
        $('#id_alumno').attr('value', $(button).data('id')).val($(button).data('id'))
        $('#edit-nombres').attr('value', $(button).data('nombres')).val($(button).data('nombres'))
        $('#edit-apellido-paterno').attr('value', $(button).data('app')).val($(button).data('app'))
        $('#edit-apellido-materno').attr('value', $(button).data('apm')).val($(button).data('apm'))
        $('#edit-fecha-nacimiento').attr('value', $(button).data('fecha')).val($(button).data('fecha'))
        $('#edit-cinturon').attr('value', $(button).data('cinturon')).val($(button).data('cinturon'))
        $('#edit-telefono').attr('value', $(button).data('telefono')).val($(button).data('telefono'))
        id_state = $(button).data('id')
    });
});

// función para validar teléfonos
function onkeydowndate(evt) {
    if (`${evt.key}`.match(/[0-9]/)){
        if (!evt.target.checkValidity()) {
            evt.target.classList.remove('is-valid')
            evt.target.classList.add('is-invalid')
        } else {
            evt.target.classList.add('is-valid')
            evt.target.classList.remove('is-invalid')
        }
        return true;
    }
    return false;
}

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
    return result.replace(' De ', ' de ').replace(' La ', ' la ')
}