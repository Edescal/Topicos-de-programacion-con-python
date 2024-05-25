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

function filter_spec_chars(str) { 
    let regex = /[^\w]{1,20}/
    let res = str.replace(regex, "")
    while(res !== str) {
        str = res
        res = str.replace(regex, "")
    }
    return res
 }

 export { capitalize, filter_spec_chars }