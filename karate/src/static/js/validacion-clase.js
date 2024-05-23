/*
    ESTE JS ES PARA VALIDAR EL FORMULARIO DE AGREGAR NUEVAS ASISTENCIAS
    REQUIERE USAR LAS DEPENDENCIAS DE BOOTSTRAP-DATEPICKER PARA FUNCIONAR

    <!-- Bootstrap datepicker CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.9.0/css/bootstrap-datepicker.min.css"/>
    <!-- Bootstrap datepicker JS-->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.9.0/js/bootstrap-datepicker.min.js"></script>
*/

// esta variable almacena el estado de validación de la fecha
var fechaState = false
$(document).ready( () =>{
    // esto es para configurar la tabla en español
    $.fn.datepicker.dates['es'] = {
        days: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        daysShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
        daysMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
        months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthsShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
        today: 'Hoy',
        clear: 'Limpiar',
        format: 'dd/mm/yy',
        titleFormat: "MM yyyy", 
        weekStart: 1
    };
    // inicializar el datepicker
    $('#select-fecha').datepicker({
        autoclose: true,
        language: 'es-419',
        todayHighlight: true,   
        keepEmptyValues: true,
        todayBtn: true,
        changeMonth: true,
        changeYear: true,
        keyboardNavigation: false,  
        maxViewMode: 'years',
        daysOfWeekHighlighted: [selectDia.value],
        beforeShowDay : function(date) {
            return date.getDay() == selectDia.value
        },
        startDate: '2004-08-19',
        endDate: new Date(),
        format : 'yyyy-mm-dd'
    });
    // configurar evento para validar cuando se cambia la fecha
    $('#select-fecha').datepicker().on('changeDate', function(e){
        console.log(e)
        if (e.date == null || e.date.getDay() != selectDia.value) {
            console.log('La fecha es inválida')
            fechaState = false
            $('#select-fecha').addClass('is-invalid').removeClass('is-valid')
        } else {
            fechaState = true
            $('#select-fecha').addClass('is-valid').removeClass('is-invalid')
        }
    });
    // configurar apariencia
    $('#select-fecha').datepicker().on('show', function(e){
        // esto es para cambiar los estilos de la tabla y que se vea un poco mejor
        $(document.querySelectorAll('.datepicker')).addClass('rounded-4 px-4 pt-3 mt-2 shadow-lg')
        $(document.querySelectorAll('.table-condensed')).addClass('table-sm mx-3').removeClass('table-condensed')
    })
    request()   
})

function requestAndUpdate(evt) { 
    request()
    // updateDatepicker()
    $('#select-fecha').datepicker('beforeShowDay')
    $('#select-fecha').datepicker('setDaysOfWeekHighlighted', [selectDia.value])
    $('#select-fecha').datepicker('setDate', $('#select-fecha').val())
}

function request() {
    const route = `/api/horarios/${selectDia.value}`
    console.log(route)
    $.ajax({
        url: route,
        async: false,
        success: function(horarios) {
            console.log('Request complete!')
            selectHora.value = -1
            selectHora.options[0].innerHTML = "Elige un horario"
            for (var i = 1; i < selectHora.options.length; i++) {
                let opcionHora = selectHora.options[i]
                
                // no hay horarios para el día elegido
                if (horarios.length == 0) {
                    // iterará todos las opciones y las deshabilita
                    opcionHora.setAttribute('hidden', true)
                    opcionHora.setAttribute('disabled', true)
                    if (i == selectHora.options.length - 1) {
                        selectHora.value = -1
                        selectHora.options[0].innerHTML = 'Sin horarios disponibles, elija otro día.'
                        return
                    }
                    continue
                }

                // Con cada opción [0, 24] iteramos con las horas disponibles
                for (var k = 0; k < horarios.length; k++) {
                    const horario = horarios[k]
                    // iterar hasta que el horario se encuentre con la opción con el mismo ID
                    if (Number(opcionHora.value) === Number(horario.id_hora)) {
                        opcionHora.removeAttribute('hidden')
                        opcionHora.removeAttribute('disabled')
                        opcionHora.innerHTML = String(horario.hora)
                        break
                    }
                    // si no coincide el ID, ocultar la opción
                    opcionHora.setAttribute('hidden', true)
                    opcionHora.setAttribute('disabled', true)
                    opcionHora.innerHTML = " "
                }
            }
            selectHora.value = -1
        },
        error: function(jqXHR, exception) {
            if (jqXHR.status === 0) {
                alert('Not connect.\n Verify Network.');
            } else if (jqXHR.status == 404) {
                alert('Requested page not found. [404]');
            } else if (jqXHR.status == 500) {
                alert('Internal Server Error [500].');
            } else if (exception === 'parsererror') {
                alert('Requested JSON parse failed.');
            } else if (exception === 'timeout') {
                alert('Time out error.');
            } else if (exception === 'abort') {
                alert('Ajax request aborted.');
            } else {
                alert('Uncaught Error.\n' + jqXHR.responseText);
            }
        }
    })
}

// EVENTOS DE SELECCIONAR DÍA
selectDia = document.getElementById('select-dia')
if (selectDia) {
    selectDia.addEventListener('input', requestAndUpdate)
    selectDia.addEventListener("select", requestAndUpdate);
    selectDia.addEventListener("onchange", requestAndUpdate);

    selectDia.addEventListener('input', evt => { 
        if (evt.currentTarget.value === '') {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
            return
        } 
        // Algunos inputs tienen un mínimo de caracteres
        let minlength = evt.currentTarget.getAttribute('minlength')
        let muycorto = minlength !== null &&  evt.currentTarget.value.length < minlength
        if (!evt.currentTarget.checkValidity() || muycorto || evt.currentTarget.value < 1 || evt.currentTarget.value > 7) {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.add('is-invalid')
        } else {
            evt.currentTarget.classList.add('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
        }
    })
    
    selectDia.addEventListener('blur', evt => {
        // quitar los espacios con trim()
        evt.currentTarget.value = $.trim(evt.currentTarget.value)
        evt.currentTarget.classList.remove('is-valid')
        evt.currentTarget.classList.remove('is-invalid')
    }, true)
    
    selectDia.addEventListener('focus', evt => {
        if (!evt.currentTarget.checkValidity() || evt.currentTarget.value < 1 || evt.currentTarget.value > 7) {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.add('is-invalid')
        } else {
            evt.currentTarget.classList.add('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
        }
    }, true)

    // Este evento no llama a requestAndUpdate, lo que pasaría al invocar un Evento "submit"
    selectDia.addEventListener('validate_on_submit', evt => { 
        console.log('Target:')
        console.log(evt.target)
        if (evt.currentTarget.value === '') {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
            return
        } 
        // Algunos inputs tienen un mínimo de caracteres
        if (!evt.currentTarget.checkValidity() || evt.currentTarget.value < 1 || evt.currentTarget.value > 7) {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.add('is-invalid')
        } else {
            evt.currentTarget.classList.add('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
        }
    })
}

// EVENTOS DE SELECCIONAR HORA
selectHora = document.getElementById('select-hora')
if (selectHora) {
    selectHora.addEventListener('input', evt => { 
        console.log('Input')
        console.log(evt.currentTarget.value == "-1")
        if (evt.currentTarget.value === '') {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
            return
        } 
        // Algunos inputs tienen un mínimo de caracteres
        let minlength = evt.currentTarget.getAttribute('minlength')
        let muycorto = minlength !== null &&  evt.currentTarget.value.length < minlength
        if (!evt.currentTarget.checkValidity() || muycorto || evt.currentTarget.value == "-1") {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.add('is-invalid')
        } else {
            evt.currentTarget.classList.add('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
        }
    })

    // Cuando se desenfoca el input, quitar la validación y espacios
    selectHora.addEventListener('blur', evt => {
        // quitar los espacios con trim()
        evt.currentTarget.value = $.trim(evt.currentTarget.value)
        evt.currentTarget.classList.remove('is-valid')
        evt.currentTarget.classList.remove('is-invalid')
    }, true)

    // Validar cuando se enfoca el input
    selectHora.addEventListener('focus', evt => {
        if (!evt.currentTarget.checkValidity() || evt.currentTarget.value == "-1") {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.add('is-invalid')
        } else {
            evt.currentTarget.classList.add('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
        }
    }, true)
}

// EVENTOS PARA LA FECHA
selectFecha = document.getElementById('select-fecha')
if (selectFecha) {
    selectFecha.setAttribute('max', new Date())
    selectFecha.addEventListener('input', evt => { 
        // Algunos inputs tienen un mínimo de caracteres
        let minlength = evt.currentTarget.getAttribute('minlength')
        let muycorto = minlength !== null &&  evt.currentTarget.value.length < minlength
        if (!evt.currentTarget.checkValidity() || !fechaState) {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.add('is-invalid')
        } else {
            evt.currentTarget.classList.add('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
        }
    })

    // Validar cuando se enfoca el input
    selectFecha.addEventListener('focus', evt => {
        if (!evt.currentTarget.checkValidity() || !fechaState) {
            evt.currentTarget.classList.remove('is-valid')
            evt.currentTarget.classList.add('is-invalid')
        } else {
            evt.currentTarget.classList.add('is-valid')
            evt.currentTarget.classList.remove('is-invalid')
        }
    }, true)
}

let form = document.getElementById('formulario')
if (form){
    // evento para validar antes de enviar el formulario
    form.addEventListener('submit', evt => {
        let falloDia = (selectDia.value < 1 || selectDia.value > 7)
        let falloHora = (selectHora.value == -1)
        if (!form.checkValidity() || falloDia || falloHora || !fechaState ) {
            console.log('Formulario no validado - no enviado')
            console.log(`State:${fechaState}`)
            evt.preventDefault()
            evt.stopPropagation()

            // mandar a validar una vez más, para mostrar qué campos no se validaron
            let event = new Event('input')
            selectHora.dispatchEvent(event)
            selectFecha.dispatchEvent(event)
            selectDia.dispatchEvent(new Event('validate_on_submit'))
        } else {
            console.log('[Debug] - Formulario validado')
            // evt.preventDefault()
            // evt.stopPropagation()
        }
    }, true)
}
