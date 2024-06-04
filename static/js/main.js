const btnDelete = document.querySelectorAll('.btn-delete');
const selectDependenciaSolicitante = document.querySelectorAll('#selectDependenciaSolicitante option');
const arraySelectDependenciaSolicitante = Array.from(selectDependenciaSolicitante).map(el => el.value);
const selectAula = document.querySelectorAll('#selectAula option');
const arraySelectAula = Array.from(selectAula).map(el => el.value);
const selectHorario = document.querySelectorAll('#selectHorario option');
const arraySelectHorario = Array.from(selectHorario).map(el => el.value);
const elemsAulas = ['#selectAula', '#selectHorario', '#otraAula', '#otroHorario', '#labelAula', '#labelHorario', "#addAula"]
const elemsEquipos = ['#labelCodInventario', '#codigoInventario', '#labelInfoEquipo', '#infoEquipo', '#labelFormaPrestamo', '#selectFormaPrestamo', '#labelHoraInicio', '#horaInicioEquipo', '#labelHoraFinal', '#horaFinalEquipo', "#addEquipo", "#divCodIng", "#divInfoEq", "#divFormaPrest", "#divHoraInicio", "#divHoraFinal", "#divArcComp"]
const elemsNovedades = ['#labelInfoNovedad', '#infoNovedad', "#addNovedad", "#divInfoNovedad"]
var fechaInicioReporte
var fechaFinReporte

//_________________FUNCIONES AUXILIARES_______________________//
function showHideElems(elemShow, elemHide, obs) {
  $.each(elemShow, function (i, elem) {
    $(elem).show()
  })
  $('#observaciones').prop('value', obs)
  $.each(elemHide, function (i, elem) {
    $(elem).hide()
  })
}
function removeDups(my_Array) {
  let NewArray = my_Array.filter(function (element, index, self) {
    return index === self.indexOf(element);
  });
  return NewArray
}

function limpiarCargar(etiqueta, arrayValores) {
  $('#' + etiqueta)
    .find('option')
    .remove()
    .end()
  for (let value of arrayValores) {
    if (value == 'Seleccione una dependencia' || value == 'Seleccione un aula' || value == 'Seleccione un horario') {
      $('#' + etiqueta).append(`<option disabled selected value="${value}">${value}</option>`);
    }
    else {
      $('#' + etiqueta).append(`<option value="${value}">${value}</option>`);
    }

  }
}

function getInforPersona(identificador, ruta) {
  if (event.which == 16) {

    let valueCedula = $(identificador).prop('value');
    let urlGetInfo = '/' + ruta + '/' + valueCedula
    console.log(urlGetInfo)
    console.log(arraySelectDependenciaSolicitante)
    $.ajax({
      url: urlGetInfo,
      data: $('form').serialize(),
      type: 'POST',
      dataType: 'json',
      success: function (response) {
        try {

          $('#nombreSolic').val(response[0].nombre)
          //limpio el campo de dependencias
          $('#selectDependenciaSolicitante')
            .find('option')
            .remove()
            .end()
          //cargo opciones en las dependencias basadas en la consulta
          for (let i = 0; i < response.length; i++) {
            if (arraySelectDependenciaSolicitante.indexOf(response[i].dependencia) > -1 && $("#selectDependenciaSolicitante option[value='" + response[i].dependencia + "']").length <= 0) {
              let optionValueText = arraySelectDependenciaSolicitante[arraySelectDependenciaSolicitante.indexOf(response[i].dependencia)]
              $('#selectDependenciaSolicitante').append(`<option value="${optionValueText}">${optionValueText}</option>`);
            }
          }
          if (identificador == "#cedDocente") {
            //limpio el campo de aulas
            $('#selectAula')
              .find('option')
              .remove()
              .end()
            //limpio el campo de horarios
            $('#selectHorario')
              .find('option')
              .remove()
              .end()
            //cargo las opciones de las aulas basadas en la cosulta
            for (let i = 0; i < response.length; i++) {
              if (arraySelectAula.indexOf(response[i].aula) > -1 && $("#selectAula option[value='" + response[i].aula + "']").length <= 0) {
                let optionValueText = arraySelectAula[arraySelectAula.indexOf(response[i].aula)]
                $('#selectAula').append(`<option value="${optionValueText}">${optionValueText}</option>`);
              }
            }
            console.log(arraySelectHorario)
            //cargo las opciones de los horarios basados en la cosulta
            for (let i = 0; i < response.length; i++) {
              if (arraySelectHorario.indexOf(response[i].h_inicio + " - " + response[i].h_fin) > -1 && $("#selectHorario option[value='" + response[i].h_inicio + " - " + response[i].h_fin + "']").length <= 0) {
                let optionValueText = arraySelectHorario[arraySelectHorario.indexOf(response[i].h_inicio + " - " + response[i].h_fin)]
                $('#selectHorario').append(`<option value="${optionValueText}">${optionValueText}</option>`);
              }
            }
          }

          $('#codPrestamo').focus();
        }
        catch {
          limpiarCargar('selectDependenciaSolicitante', arraySelectDependenciaSolicitante)
          limpiarCargar('selectAula', arraySelectAula)
          limpiarCargar('selectHorario', arraySelectHorario)
          $(identificador).val('')
          $('#nombreSolic').val('')
          $(identificador).focus();
          alert("No se han encontrado resultados para la cédula ingresada.")

        }

      },
      error: function (error) {
        alert("Error de petición al servidor, intente nuevamente.")
      }
    })
  }
}

//________________FUNCION CUANDO EL DOCUMENTO ESTÁ LISTO__________________//
$(document).ready(function () {
  /*
  $(document).bind("contextmenu",function(e) {
      e.preventDefault();
  });
  */
 //cuando se selecciona una fecha para el reporte se actualiza la variable
  $("#fechaFinReporte").datepicker();
    $("#fechaFinReporte").on("change",function(){
        fechaFinReporte = $(this).val();
        $(this).datepicker('hide'); 
    });
  
  $("#fechaInicioReporte").datepicker();
  $("#fechaInicioReporte").on("change",function(){
      fechaInicioReporte = $(this).val();
      $(this).datepicker('hide');
  });
  //función que atiende la petición para descargar reporte de docentes
  function validar_generar_reporte(tipoPersona){
    if (fechaFinReporte != undefined && fechaInicioReporte != undefined) {
      if(new Date(fechaFinReporte)>=new Date(fechaInicioReporte)){
        fechaInicioReporte = fechaInicioReporte + " 00:00:00"
        fechaFinReporte = fechaFinReporte + " 23:59:00"
        window.location.href = "/download/report/"+fechaInicioReporte+"/"+fechaFinReporte+"/"+tipoPersona;
      }
      else{
        alert("La fecha fin debe ser mayor o igual que la fecha inicio")
      }
        
    }
    else {
      alert("Por favor ingrese las fechas para generar el reporte.")
    }
  }
  //evento para llamar la función generar reporte de docentes
  $('#btnReporteDocentes').on('click',function(){validar_generar_reporte("DOCENTE")})

  //evento para llamar la función generar reporte de contratistas
  $('#btnReporteContratistas').on('click',function(){validar_generar_reporte("CONTRATISTA")})

  //establezco focus en la cédula al cargar el doc
  $('#cedDocente').focus();
  //$("#infoEquipo").prop("readonly",true)
  //oculta formulario de prestamo de aulas y equipos
  $.each(elemsAulas, function (i, elem) {
    $(elem).hide()
  })
  $.each(elemsEquipos, function (i, elem) {
    $(elem).hide()
  })
  $.each(elemsNovedades, function (i, elem) {
    $(elem).hide()
  })

 
  //agregar las aulas al prestamo
  $('#addAula').on('click', function () {
    let aulaPrestar = $("#selectAula option:selected").text()
    let horarioPrestar = $("#selectHorario option:selected").text()
    if (aulaPrestar != "Seleccione un aula" && horarioPrestar != "Seleccione un horario") {
      $('#todo').append("<div class= 'row'><li class='list-group-item'><input type='text' name='items' class='form-control' id='itemPrestamoAula' value='" + "Aula: " + $("#selectAula option:selected").text() + " Horario: " + $("#selectHorario option:selected").text() + " Observaciones: " + $("#observaciones").val() + "' readonly></input>" + "<button class='btn'><i class='fa fa-trash'></i></button></li></div>");
    }
    else {
      alert("No se puede agregar el equipo porque faltan datos por completar")
    }
    $('#codPrestamo').focus();
    //$('#subFormAula').hide()
  });
  //agregar los equipos al prestamo
  $('#addEquipo').on('click', function () {
    let informacion = $("#infoEquipo").val()
    let formaPrestamo = $("#selectFormaPrestamo option:selected").text()
    let horaInicio = $("#horaInicioEquipo").val()
    let horaFinal = $("#horaFinalEquipo").val()
    let observaciones = $("#observaciones").val()
    //validación para agregar un equipo
    if (formaPrestamo != 'Seleccione una forma de prestamo' && informacion != '' && horaInicio != '' && horaFinal != '' && observaciones != '') {
      if (horaInicio < horaFinal) {
        $('#todo').append("<div class= 'row'><li class='list-group-item'><input type='text' class='form-control' name='items' id='itemPrestamoEquipo' value='" + "Forma de prestamo: " + $("#selectFormaPrestamo option:selected").text() + " Información: " + $("#infoEquipo").val() + " Placa: " + $("#codigoInventario").val() +" Hora Inicio: " + $("#horaInicioEquipo").val() + " Hora Final: " + $("#horaFinalEquipo").val() + " Observaciones: " + $("#observaciones").val() + "' readonly></input>" + "<button class='btn'><i class='fa fa-trash'></i></button></li></div>");
      }
      else {
        alert("La hora de inicio no puede ser mayor que la hora de finalización")
      }
    }
    else {
      alert("No se puede agregar el equipo porque faltan datos por completar")
    }
    $('#codigoInventario').focus();
  });
  //agregar novedades
  $('#addNovedad').on('click', function () {
    let informacionNovedad = $("#infoNovedad").val()
    let observaciones = $("#observaciones").val()
    //validación para agregar un equipo
    if (informacionNovedad != '' && observaciones != '') {
      $('#todo').append("<div class= 'row'><li class='list-group-item'><input type='text' class='form-control' name='items' id='itemNovedad' value='"+ " Información de la novedad: " + $("#infoNovedad").val() + " Observaciones: " + $("#observaciones").val() + "' readonly></input>" + "<button class='btn'><i class='fa fa-trash'></i></button></li></div>");
    }
    else {
      alert("No se puede agregar la novedad porque faltan datos por completar")
    }
    $('#infoNovedad').focus();
  });
  $("body").on('click', '#todo input', function () {
    $(this).prop("disabled", true)
  })
  //remover de los items
  $("body").on('click', '#todo button', function () {
    $(this).closest("li").remove();
    $('#selectTipoPrestamo')
      .show()
      .val('Seleccione una opción');
  });

  //despliego los campos dependiendo del código del prestamo
  $('#codPrestamo').keydown(function (event) {
    let codPrestamo = $(this).prop('value')
    if (event.which == 16) {
      if (codPrestamo == '01') {
        showHideElems(elemsAulas, elemsEquipos.concat(elemsNovedades), 'Se presta aula con llaves')

      }
      else if (codPrestamo == '03') {
        showHideElems(elemsEquipos, elemsAulas.concat(elemsNovedades), 'Se presta elemento en buenas condiciones')
        $('#codigoInventario').focus();
      }
      else if (codPrestamo == '05') {
        showHideElems(elemsNovedades, elemsAulas.concat(elemsEquipos), '')
        $('#infoNovedad').focus();
      }
    }
  })
  //cargar nuevamente todas las dependencias
  $('#otraDependencia').on('click', function () {
    limpiarCargar('selectDependenciaSolicitante', arraySelectDependenciaSolicitante)
  });
  //cargar nuevamente todas las aulas
  $('#otraAula').on('click', function () {
    limpiarCargar('selectAula', arraySelectAula)
  });
  //cargar nuevamente todos los horarios
  $('#otroHorario').on('click', function () {
    limpiarCargar('selectHorario', arraySelectHorario)
  });

  //se obtiene información de la base de datos basado en la cédula
  $('#cedDocente').keydown(function (event) {
    getInforPersona("#cedDocente", "getInfoDocente")
  });
  $('#cedContratistas').keydown(function (event) {
    getInforPersona("#cedContratistas", "getInfoContratista")
  });
  $('#cedEstudiante').keydown(function (event) {
    getInforPersona("#cedEstudiante", "getInfoEstudiante")
  });
  //se obtiene la descripción del equipo basado en el código de inventario
  $('#codigoInventario').keydown(function (event) {

    if (event.which == 16) {

      let valueCodInventario = $('#codigoInventario').prop('value');
      let urlGetInfo = '/getInfoEquipo/' + valueCodInventario
      console.log(urlGetInfo)
      $.ajax({
        url: urlGetInfo,
        data: $('form').serialize(),
        type: 'POST',
        dataType: 'json',
        success: function (response) {
          try {
            //obtengo la info del equipo
            $('#infoEquipo').val(response[0].tipo + " - " + response[0].marca)
            //establecer el foco en el código de prestamo
            $('#selectFormaPrestamo').focus();
          }
          catch {
            alert("No se ha encontrado resultados para el código: " + valueCodInventario)
          }

        },
        error: function (error) {
          alert("Error de petición al servidor, intente nuevamente.")
        }
      })
    }
  });

  //función para antender click en entregar
  $("#btnEntregar").on("click", function () {
    let selected = new Array();
    $("#tableReg input[type=checkbox]:checked").each(function () {
      selected.push(this.value);
    });
    if (selected.length > 0) {
      $.ajax({
        url: "/updateRecords",
        type: "POST",
        data: { "selected": selected },
        success: function (response) {
          alert("Registros actualizados correctamente")
          setTimeout(function () {// wait for 5 secs(2)
            location.reload(); // then reload the page.(3)
          }, 10);
        },
        error: function (error) {
          alert("Ha ocurrido un error al actualizar los registros.")
        },
      });
    }
    else {
      alert("Por favor seleccione el/los elementos a entregar.")
    }
  });
  //agrega el docente en caso de no estar.
  $("#addDoc").on("click", function () {
    let cedulaDoc = $("#cedDocente").val()
    let nombreDoc = $("#nombreSolic").val()
    let depDoc = $("#selectDependenciaSolicitante option:selected").text();
    if (cedulaDoc != "" && nombreDoc != "" && depDoc != "" && depDoc != "Seleccione una dependencia") {
      $.ajax({
        url: "/createDoc",
        type: "POST",
        data: {"cedulaDoc": cedulaDoc, "nombreDoc":nombreDoc, "depDoc":depDoc},
        success: function (response) {
          alert("Docente creado correctamente")
          $('#codPrestamo').focus();
        },
        error: function (error) {
          alert("Ha ocurrido un error al crear el docente.")
        },
      });
    }
    else {
      alert("Por favor ingrese los campos de cédula, nombre y dependencia.")
    }
  });
  //agrega el contratista en caso de no estar.
  $("#addContrat").on("click", function () {
    let cedulaCont = $("#cedContratistas").val()
    let nombreCont = $("#nombreSolic").val()
    let depCont = $("#selectDependenciaSolicitante option:selected").text();
    if (cedulaCont != "" && nombreCont != "" && depCont != "" && depCont != "Seleccione una dependencia") {
      $.ajax({
        url: "/createCont",
        type: "POST",
        data: {"cedulaCont": cedulaCont, "nombreCont":nombreCont, "depCont":depCont},
        success: function (response) {
          alert("Administrativo creado correctamente")
          $('#codPrestamo').focus();
        },
        error: function (error) {
          alert("Ha ocurrido un error al crear el administrativo.")
        },
      });
    }
    else {
      alert("Por favor ingrese los campos de cédula, nombre y dependencia.")
    }
  });
  //agrega el contratista en caso de no estar.
  $("#addEst").on("click", function () {
    let cedulaEst = $("#cedEstudiante").val()
    let nombreEst = $("#nombreSolic").val()
    let depEst = $("#selectDependenciaSolicitante option:selected").text();
    if (cedulaEst != "" && nombreEst != "" && depEst != "" && depEst != "Seleccione una dependencia") {
      $.ajax({
        url: "/createEst",
        type: "POST",
        data: {"cedulaEst": cedulaEst, "nombreEst":nombreEst, "depEst":depEst},
        success: function (response) {
          alert("Estudiante creado correctamente")
          $('#codPrestamo').focus();
        },
        error: function (error) {
          alert("Ha ocurrido un error al crear el estudiante.")
        },
      });
    }
    else {
      alert("Por favor ingrese los campos de cédula, nombre y dependencia.")
    }
  });
  //tabla de registros con opciones de busqueda y filtro, con lenguaje en español
  $('#tableReg').dataTable({
    "language": {
      "url": "//cdn.datatables.net/plug-ins/1.10.15/i18n/Spanish.json"
    }
  }

  );


});